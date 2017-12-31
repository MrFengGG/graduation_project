//引入UDP包
var dgram = require("dgram");
//path工具
var path = require('path');
//引入express模块
var express = require('express');

//初始化服务器
var app = express();
var http = require("http").Server(app);
var io = require("socket.io")(http);

//初始化udpsocket
var serverSocket = dgram.createSocket("udp4");
serverSocket.bind(9999);

//初始化连接池
var connections = {};
var connectionid = new Set();

//设置静态文件目录
app.use(express.static(path.join(__dirname, 'public')));

//设置登录选项
app.post("/",function(req,res){
	console.log(req.query.id);
	console.log(req.body);
	if(vaildate(req)){
		res.sendfile("public/home.html");
	}else{
		res.sendfile("public/login.html");
	}
});
//设置get页面
app.get("/",function(req,res){
	if(vaildate(req)){
		res.sendfile("public/home.html");
	}else{
		res.sendfile("public/login.html");
	}
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
		console.log(msg);
		if(msg){
			serverSocket.send(msg,0,msg.length,9997,"192.168.137.39");
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

			connections[a].send(bufferToJason(msg));
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
	var serverSocket = dgram.createSocket('udp4');
	serverSocket.send(msg,0,msg.length,9997,"127.0.0.1")
	console.log("send a message");
}
