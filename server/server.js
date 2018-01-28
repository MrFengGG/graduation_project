//引入UDP包
var dgram = require("dgram");
//path工具
var path = require('path');
//引入express模块
var express = require('express');

var fs = require("fs");
//初始化服务器
var app = express();
var http = require("http").Server(app);
var io = require("socket.io")(http);
//session模块
var session = require('express-session');
//参数解析器
var bodyParser = require('body-parser');
app.use(bodyParser.urlencoded({
	extended:true
}));
//初始化udpsocket
var serverSocket = dgram.createSocket("udp4");
serverSocket.bind(9999);

//初始化连接池
var connections = {};
var connectionid = new Set();
var config = {
	/*
	ip:"119.23.210.76",
	port:27017,
	db:'film'
	*/
	ip:"127.0.0.1",
	port:"27017",
	db:"test"
}
app.use(session({
    secret: 'hubwiz app', //secret的值建议使用随机字符串
    cookie: {maxAge: 60 * 1000 * 30} // 过期时间（毫秒）
}));

//设置静态文件目录
app.use(express.static(path.join(__dirname, 'public')));
app.set("views",path.join(__dirname,"views"));
app.set("view engine","html");
app.engine(".html",require("ejs").__express);
var MongoClient = require("mongodb").MongoClient;
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
    		console.log("拦截一次");
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
	console.log(req.body)
	req.session.user = {"name":"feng"};  // 将用户信息写入 session
 	if (req.session.originalUrl) {  // 如果存在原始请求路径，将用户重定向到原始请求路径
		var redirectUrl = req.session.originalUrl;
		req.session.originalUrl = null;  // 清空 session 中存储的原始请求路径
 	}else {  // 不存在原始请求路径，将用户重定向到根路径
		var redirectUrl = '/';
	}
	res.redirect(redirectUrl);
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
	console.log(condition);
	for(var c in condition){
		condition[c] = new RegExp(condition[c]);
	}
	console.log(condition)
	var field = req.body.field?req.body.field:{};
	var isClass = req.body.isClassifi?parseInt(req.body.isClassifi):0;
	for(var i in field){
		field[i] = parseInt(field[i])
	}
	queryMongo(condition,field,page,pageSize,req,res);
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
			serverSocket.send(msg,0,msg.length,9997,"127.0.0.1");
		}
	});
	socket.on("imageCommand",function(msg,info){
		if(msg){
			serverSocket.send(msg,0,msg.length,9998,"127.0.0.1")
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
http.listen(3000,function(socket){
	console.log("listening on 3000")
});


//工具函数
function bufferToJason(bufferdata){
	//将buf转化为json格式数据
	return JSON.parse(bufferdata.toString("utf-8"));
}
function vaildate(request){
	return true;
}
function sendCommand(msg){
	//转发命令
	var serverSocket = dgram.createSocket('udp4');
	serverSocket.send(msg,0,msg.length,9997,"127.0.0.1")
}
function queryMongo(document,condition){
	//查询mongodb数据库,document为查询的目标文档,condition为条件
}
function loadJsonFile(filename,page,pageSize){
	var result = fs.readFileSync(filename,"utf-8");
	results = result.split("\n").slice(page * pageSize,(page + 1) * pageSize);
	return JSON.stringify(results);
}
function getdbUrl(){
	return 'mongodb://'+config.ip+":"+config.port+'/'+config.db;
}
function queryMongo(condition,field,page,pageSize,req,res){
	MongoClient.connect(getdbUrl(), function(error, db){
		var db = db.db('test')
	    var col = db.collection("move");
		col.find(condition).limit(pageSize).skip((page-1)*pageSize).project(field).toArray(function(err,doc){
		    res.writeHead(200,{"Content-Type":'text/plain','charset':'utf-8','Access-Control-Allow-Origin':'*','Access-Control-Allow-Methods':'PUT,POST,GET,DELETE,OPTIONS'});
			res.write(JSON.stringify(doc),'utf-8');
			res.end();
		})
	});
}

