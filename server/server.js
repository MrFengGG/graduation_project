//引入UDP模块
var dgram = require("dgram");
//引入path模块
var path = require('path');
//引入express模块
var express = require('express');
//引入session模块
var session = require('express-session');
//引入参数解析模块
var bodyParser = require('body-parser');
//引入http模块
var httpServer = require("http");
//加载配置文件
var config = require("./config");
//初始化服务器
var app = express();
//命令行工具导入
var spawn = require('child_process').spawn;

app.use(bodyParser.urlencoded({
	extended:true
}));
var http = httpServer.Server(app);
//初始化socket连接
var io = require("socket.io")(http);
var serverSocket = dgram.createSocket("udp4");
serverSocket.bind(9999);
//初始化mongodb
var MongoClient = require("mongodb").MongoClient;
//初始化连接池
var connections = {};
var connectionid = new Set();

//初始化全局变量
var isWarning = true;

app.use(session({
    secret: 'hubwiz app', //secret的值建议使用随机字符串
    cookie: {maxAge: 60 * 1000 * 30} // 过期时间（毫秒）
}));
app.use(express.static(path.join(__dirname, 'public')));
app.set("views",path.join(__dirname,"views"));
app.set("view engine","html");
app.engine(".html",require("ejs").__express);
//拦截器
app.use(function (req, res, next) {
	if (req.session.user) {  // 判断用户是否登录
		next();
	}else{
    	// 解析用户请求的路径
    	var arr = req.url.split('/');
    	// 去除 GET 请求路径上携带的参数
    	for (var i = 0, length = arr.length; i < length; i++) {
      		arr[i] = arr[i].split('?')[0];
    	}
    	// 判断请求路径是否为登录、登出，如果是不做拦截
    	if(arr.length >= 2 && arr[1] == 'login' || arr[1] == 'logout') {
      		next();
    	}else { 
      		req.session.originalUrl = req.originalUrl ? req.originalUrl : null;  // 记录用户原始请求路径
      		res.redirect('/login');  // 将用户重定向到登录页面
    	}
  	}
});

//登录页面
app.get("/login",function(req,res,next){
	res.render("login.html");
});
//登录请求
app.post("/login",function(req,res,next){
	queryMongo(config.userCollection,{},{},0,0,req,res,vaildate);
})
//登出请求
app.get("/logout",function(req,res,next){
	delete req.session.user;
	res.redirect('login');
})
//设置get页面
app.get("/",function(req,res){
	res.render("home.html");
});
app.get("/camera",function(req,res){
	res.render("camera.html");
})
app.get("/download",function(req,res){
	res.render("download.html");
})
app.get("/music",function(req,res){
	res.render("music.html");
});
app.get("/theatra",function(req,res){
	res.render("theatra.html");
});
app.get("/storage",function(req,res){
	res.render("storage.html");
});
app.get("/setting",function(req,res){
	res.render("setting.html");
});
app.post("/data/move",function(req,res){
	var page = parseInt(req.body.page?req.body.page:1);
	var pageSize = parseInt(req.body.pageSize?req.body.pageSize:0);
	var condition = req.body.condition?req.body.condition:{};
	for(var c in condition){
		condition[c] = new RegExp(condition[c]);
	}
	var field = req.body.field?req.body.field:{};
	var isClass = req.body.isClassifi?parseInt(req.body.isClassifi):0;
	for(var i in field){
		field[i] = parseInt(field[i])
	}
	queryMongo(config.collection,condition,field,page,pageSize,req,res,sendData);
})
app.post("/data/download",function(req,res){
	var url = req.body.download_url;
	var command = []
	command.push("cd "+config.download_path)
	command.push("aria2c "+url)
	res.writeHead(200,{"Content-Type":'text/plain','charset':'utf-8','Access-Control-Allow-Origin':'*','Access-Control-Allow-Methods':'PUT,POST,GET,DELETE,OPTIONS'});
	exec(spawn,command,dataCallBack,exitCallBack,res);
})
//监听websocket连接
io.on("connection",function(socket){
	//监听到连接时,将socket加入连接池中
	socket.send("连接成功");
	connections[socket.id] = socket;
	connectionid.add(socket.id);
	console.log("增加一个连接,当前连接数量为"+connectionid.size)
	//获得来自网页的陀螺仪信息,转发
	socket.on("command",function(msg,info){
		if(msg){
			serverSocket.send(msg,0,msg.length,config.commandPort,config.commandIP);
		}
	});
	socket.on("imageCommand",function(msg,info){
		if(msg){
			if(JSON.parse(msg)['command'] == "analyze"){
				isWarning = !isWarning
				for(var a of connectionid){
					connections[a].emit("analyze",isWarning?"1":"0");
				}
			}
			serverSocket.send(msg,0,msg.length,config.imagePort,config.imageIP);
		}
	});
	//断开连接时,将连接从连接池中删除
	socket.on("disconnect",function(){
		delete connections[socket.id];
		connectionid.delete(socket.id);
		console.log("删除一个连接,当前连接数量为"+connectionid.size);
	});
})
//监听udp连接,如果有画面,将画面广播出去
serverSocket.on("message",function(msg,info){
		for(var a of connectionid){
			connections[a].send(msg);
		}
	});
//开启监听网页
http.listen(config.listenPort,function(socket){
	console.log("listening on "+config.listenPort);
});
//执行命令行
function exec(spawn,command,data_callback,exit_callback,res){
	command_process = spawn("bash");
	command_process.stdout.on("data",function(data){
		if(data_callback){
			data_callback(data,res)
		}
	});
	command_process.stderr.on("data",function(data){
		if(data_callback){
			data_callback(data,res)
		}
	});
	command_process.on("exit",function(code,signal){
		if(exit_callback){
			exit_callback(code,signal,res)
		}
	});
	for(var i = 0;i < command.length;i++){
		command_process.stdin.write(command[i]+"\n");
	}
	command_process.stdin.end();
}
//命令行数据回调函数
function dataCallBack(data,res){
	for(var a of connectionid){
		connections[a].emit("prograss",msg);
	}
}
//命令行结束回调函数
function exitCallBack(code,signal,res){
	res.write(code.toString(),'utf-8');
	res.end()
}
//工具函数
function bufferToJason(bufferdata){
	//将buf转化为json格式数据
	return JSON.parse(bufferdata.toString("utf-8"));
}

function getdbUrl(){
	//获得mongodburl
	return 'mongodb://'+config.ip+":"+config.port+'/'+config.db;
}
//发送数据
function sendData(doc,req,res){
	res.writeHead(200,{"Content-Type":'text/plain','charset':'utf-8','Access-Control-Allow-Origin':'*','Access-Control-Allow-Methods':'PUT,POST,GET,DELETE,OPTIONS'});
	res.write(JSON.stringify(doc),'utf-8');
	res.end();
}
//验证登录信息
function vaildate(doc,req,res){
	var result = {};
	var user = req.body;
	var redirectUrl = '';
	for(var i = 0;i < doc.length;i++){
		if(doc[i]['user']==user['user'] && doc[i]['password']==user['password']){
			req.session.user = {"name":"feng"};
			result['code']=1;
			result['note']="登录成功"
			result['message'] = '/';
			sendData(result,req,res);
			return
		}
	}
	result['code']=-1;
	result['note']="用户名不存在或密码错误"
	sendData(result,req,res);
}
function queryMongo(collection,condition,field,page,pageSize,req,res,callback){
	//查询数据库
	MongoClient.connect(getdbUrl(), function(error, db){
		var db = db.db(config.db)
	    var col = db.collection(collection);
		col.find(condition).limit(pageSize).skip((page-1)*pageSize).project(field).toArray(function(err,doc){
			callback(doc,req,res);
		})
	});
}

