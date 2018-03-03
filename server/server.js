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

var progressStream = require('progress-stream');
//引入http模块
var httpServer = require("http");
//加载配置文件和工具类
var config = require("./config");
var util = require("./util");
//文件上传模块
const upload = require('multer')({ dest: config.uploadFilePath});
//初始化服务器
var app = express();
app.use(bodyParser.urlencoded({
	extended:true,
	uploadDir:config.uploadFilePath
}));

var http = httpServer.Server(app);
//初始化socket连接
var io = require("socket.io")(http);
var serverSocket = dgram.createSocket("udp4");
serverSocket.bind(9999);
//初始化连接池
var connections = {};
var connectionid = new Set();
//初始化全局变量
var isWarning = true;

app.use(session({
    secret: 'smartControl app', //secret的值建议使用随机字符串
    cookie: {maxAge: config.expireTime} // 过期时间（毫秒）
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
	util.queryMongo(util.getdbUrl(config.ip,config.port,config.db),config.db,config.userCollection,{},{},0,0,req,res,vaildate);
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
app.get("/message",function(req,res){
	res.render("message.html");
});
/**
 * [电影数据查询接口]
 * @param  {[type]} req        [description]
 * @param  {[type]} res){	var page          [description]
 * @return {[type]}            [description]
 */
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
	util.queryMongo(util.getdbUrl(config.ip,config.port,config.db),config.db,config.collection,condition,field,page,pageSize,req,res,util.sendData);
})
/**
 * [普通数据离线下载接口]
 * @param  {[type]} req        [description]
 * @param  {[type]} res){	var url           [description]
 * @param  {[type]} req        [description]
 * @param  {[type]} res);}    [description]
 * @return {[type]}            [description]
 */
app.post("/data/normalDownload",function(req,res){
	var url = req.body.download_url;
	var command = []
	command.push("cd "+config.download_path)
	command.push("aria2c "+ url)
	util.execCommand(command,dataCallBack,exitCallBack,res);
	uti.sendData({"code":1,note:"下载开始"},req,res);
});
/**
 * [音频数据离线下载接口]
 * @param  {[type]} req        [description]
 * @param  {[type]} res){	var url           [description]
 * @param  {[type]} req        [description]
 * @param  {[type]} res);}    [description]
 * @return {[type]}            [description]
 */
app.post('/data/VideoDownload',function(req,res){
	var url = req.body.download_url;
	var command = [];
	command.push("cd "+config.yougetPath);
	command.push("./you-get -o "+config.download_path+" "+url);
	util.execCommand(command,dataCallBack,exitCallBack,res);
	util.sendData({"code":1,note:"下载开始"},req,res);
});
/**
 * [本地下载接口]
 * @param  {[type]} req                          [description]
 * @param  {[type]} res){	var                   filePath      [description]
 * @param  {[type]} config.compressRate          [description]
 * @param  {[type]} config.tempFileName)['code'] >             0){		util.downloadFile(config.tempFileName,req,res,"test.zip");	}	if(util.isExist(config.tempFileName)){		util.removeFile(config.tempFileName);	}} [description]
 * @return {[type]}                              [description]
 */
app.get("/data/download",function(req,res){
	var filePath = req.query.filePath;
	var filePaths = filePath.split("`");
	result = []
	for(var i = 0;i < filePaths.length;i++){
		if(req.query.type == "grab"){
			result.push(config.garbPath+filePaths[i]);
		}else if(req.query.type == "download"){
			result.push(config.download_path+filePaths[i]);
		}else{
			result.push(config.cludPath+filePaths[i]);
		}
	}

	if(util.compressFiles(result.join(" "),config.compressRate,config.tempFileName)['code'] > 0){
		util.downloadFile(config.tempFileName,req,res,"result.zip");
	}
	if(util.isExist(config.tempFileName)){
		util.removeFile(config.tempFileName);
	}
})
/**
 * [文件查询数据接口]
 * @param  {[type]} req        [description]
 * @param  {[type]} res){	var nowPath       [description]
 * @return {[type]}            [description]
 */
app.post('/data/queryFile',function(req,res){
	var nowPath = req.body.nowPath;
	var completePath = '';
	nowPath = nowPath || "";
	if(req.body.type == "grab"){
		completePath = config.garbPath + nowPath;
	}else if(req.body.type == "download"){
		completePath = config.download_path + nowPath;
	}else{
		completePath = config.cludPath+nowPath;
	}
	util.sendData(util.listFile(completePath,nowPath),req,res);
});
/**
 * [分类文件查询接口]
 * @param  {[type]} req        [description]
 * @param  {[type]} res){	var nowPath       [description]
 * @return {[type]}            [description]
 */
app.post('/data/queryClassificationFile',function(req,res){
	var nowPath = req.body.nowPath;
	var fileType = req.body.fileType;
	nowPath = nowPath || "";
	var completePath = '';
	if(req.body.type == "garb"){
		completePath = config.garbPath + nowPath;
		util.sendData(util.listAllFile(completePath,fileType,config[fileType],config.garbPath),req,res);
	}else if(req.body.type == "download"){
		completePath = config.download_path + nowPath;
		util.sendData(util.listAllFile(completePath,fileType,config[fileType],config.download_path),req,res);
	}else{
		completePath = config.cludPath+nowPath;
		util.sendData(util.listAllFile(completePath,fileType,config[fileType],config.cludPath),req,res);
	}
});
/**
 * [文件操作接口]
 * @param  {[type]} req          [description]
 * @param  {[type]} res){	var   filePath      [description]
 * @param  {[type]} req          [description]
 * @param  {[type]} res);	}else if(optType    [description]
 * @return {[type]}              [description]
 */
app.post("/data/optFile",function(req,res){
	var filePath = req.body.filePath;
	var optType = req.body.optType;
	var result = {}
	if(!filePath && optType == "rm"){
		result['code'] = -1;
		result['note'] = "文件为空";
		util.sendData(result,req,res);
	}
	var prefix = "";
	if(req.body.type == "grab"){
		prefix = config.garbPath;
	}else if(req.body.type == "download"){
		prefix = config.download_path;
	}else{
		prefix = config.cludPath;
	}
	if(optType == "rm"){
		var filePaths = filePath.split("`");
		result = []
		for(var i = 0;i < filePaths.length;i++){
			result.push(prefix+filePaths[i]);
		}
		util.sendData(util.removeFile(result.join(' ')),req,res);
	}else if(optType == "ct"){
		console.log(prefix);
		util.sendData(util.createFile(prefix+filePath,"新建文件夹"),req,res);
	}else if(optType == "mv"){
		var newPath = prefix+req.body.newPath;
		var filePaths = filePath.split("`");
		result = []
		for(var i = 0;i < filePaths.length;i++){
			result.push(prefix+filePaths[i]);
		}
		util.sendData(moveFile(filePath,newPath));
	}
})
//文件上传
app.post("/data/upload",upload.single('temp'),function(req,res,next){
	var nowPath = req.body.nowPath;
	var type = req.body.type;
	var prefer = "";
	if(type == "grab"){
		prefix = config.garbPath;
	}else if(type == "download"){
		prefix = config.download_path;
	}else{
		prefix = config.cludPath;
	}
  	var fileMessage = req.file;
  	util.moveFiles(fileMessage.path,prefix+nowPath+"/"+fileMessage.originalname);
  	util.sendData(fileMessage,req,res);
});

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
	//获得来自网页的视频设置信息
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
/**
 * [dataCallBack 命令行标准输出回调函数]
 * @param  {[type]} data [description]
 * @return {[type]}      [description]
 */
function dataCallBack(data){
	for(var a of connectionid){
		connections[a].emit("prograss",util.bufferToString(data));
	}
}
/**
 * [exitCallBack 命令行执行结束回调函数]
 * @param  {[type]} code   [description]
 * @param  {[type]} signal [description]
 * @return {[type]}        [description]
 */
function exitCallBack(code,signal){
	if(code == 0){
		for(var a of connectionid){
			connections[a].emit("over","success");
		}
	}else{
		for(var a of connectionid){
			connections[a].emit("over","fail");
		}
	}
}

/**
 * [vaildate 验证登录信息]
 * @param  {[type]} doc [数据库查询结果]
 * @param  {[type]} req [description]
 * @param  {[type]} res [description]
 * @return {[type]}     [description]
 */
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
			util.sendData(result,req,res);
			return
		}
	}
	result['code']=-1;
	result['note']="用户名不存在或密码错误"
	util.sendData(result,req,res);
}

