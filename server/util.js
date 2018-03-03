var util = {}
util.execSync = require('child_process').execSync;
util.fs = require('fs')
util.textEncoding = require('text-encoding')
util.spawn = require('child_process').spawn;
util.decoder = new util.textEncoding.TextDecoder();
util.MongoClient = require("mongodb").MongoClient;
/**
 * [parseByteSize 将文件大小转换为合适的单位]
 * @return {[type]} [description]
 */
util.parseByteSize = function(size,up){
	if(!size){
		return "--";
	}
	var kbs = size / up;
	if(kbs < 2000){
		return kbs+"KB";
	}
	mbs = kbs / up;
	if(mbs < 2000){
		return mbs+"M"
	}
	gbs = mbs / up;
	return gbs+"G"
}
/**
 * [downloadFile 下载文件]
 * @param  {[type]} path     [文件路径]
 * @param  {[type]} req      [请求]
 * @param  {[type]} res      [响应]
 * @param  {[type]} fileName [文件回写名称]
 * @return {[type]}          [description]
 */
util.downloadFile = function(path,req,res,fileName){
	var f = this.fs.createReadStream(path);
	res.writeHead(200, {
	    'Content-Type': 'application/force-download',
	    'Content-Disposition': 'attachment; filename='+fileName
  	});
  	f.pipe(res);
}

/**
 * [compressFiles 将多个文件夹压缩为一个]
 * @param  {[type]} files 		   [文件夹]
 * @param  {[type]} compressRate   [压缩比,1到9]
 * @param  {[type]} targetFileName [目标文件]
 * @return {[type]}       		   [json对象]
 */
util.compressFiles = function(files,compressRate,targetFileName){
	var result = {};
	try{
		console.log('zip -r -'+compressRate+' -q -o '+targetFileName+' '+files);
	    var cmd = this.execSync('zip -r -'+compressRate+' -q -o '+targetFileName+' '+files);
	    result['code'] = 1;
    	result['note']= cmd && cmd.toString("utf-8") || "压缩成功";
	}catch(err){
		result['code'] = -1;
		result['note']= err && err.toString("utf-8") || "压缩失败";
	}
	return result;
}
/**
 * [moveFiles 移动文件]
 * @param  {[type]} preFiles [原文件]
 * @param  {[type]} newFiles [移动目标]
 * @return {[type]}          [json对象]
 */
util.moveFiles = function(preFiles,newPath){
	var result = {}
	try{
		console.log('mv '+preFiles+" "+newPath);
		var cmd = this.execSync('mv '+preFiles+" "+newPath);
		result['code'] = 1;
	    result['note']= cmd && cmd.toString("utf-8") || "移动成功";
	}catch(err){
		result['code'] = -1;
	    result['note'] = err.toString;
	}
	return result;
}
/**
 * [createFile 在指定目录下创建新文件夹,默认名称为新建文件夹]
 * @param  {[type]} path     [文件路径]
 * @param  {[type]} fileName [文件名]
 * @return {[type]}          [json对象]
 */
util.createFile = function(path,fileName){
	var result = {}
	try{
		var filePath = path + "/"+fileName;
		var num = 0;
		while(this.fs.existsSync(filePath)){
			filePath = filePath+(++num);
		}
		console.log('mkdir '+filePath);
	    var cmd = this.execSync('mkdir '+filePath);
	    result['code'] = 1;
	    result['note']= cmd && cmd.toString("utf-8") || "创建成功";
	}catch(err){
		console.log(err);
	    result['code'] = -1;
	    result['note'] = err.toString;
	}
	return result;
}
/**
 * [removeFile 删除文件]
 * @param  {[type]} files [文件列表]
 * @return {[type]}       [json对象]
 */
util.removeFile = function(files){
	var result = {}
	var cmd;
	try{
	    var cmd = this.execSync('rm -rf '+files);
	    result['code'] = 1;
	    result['note']= cmd && cmd.toString("utf-8") || "删除成功";
	}catch(err){
		console.log(err);
	    result['code'] = -1;
	    result['note'] = err.toString;
	}
	return result;
}
/**
 * [execCommand 异步执行命令行,用于创建进度条]
 * @param  {[type]} command       [命令]
 * @param  {[type]} data_callback [标准输出]
 * @param  {[type]} exit_callback [结束时的回调函数]
 * @return {[type]}               [json数据]
 */
util.execCommand = function(command,data_callback,exit_callback){
	command_process = this.spawn("bash");
	command_process.stdout.on("data",function(data){
		if(data_callback){
			data_callback(data);
		}
	});
	command_process.stderr.on("data",function(data){
		if(data_callback){
			data_callback(data);
		}
	});
	command_process.on("exit",function(code,signal){
		if(exit_callback){
			exit_callback(code,signal);
		}
	});
	for(var i = 0;i < command.length;i++){
		command_process.stdin.write(command[i]+"\n");
	}
	command_process.stdin.end();
}
/**
 * [listFile 列出一个文件夹下的所有信息]
 * @param  {[type]} dir [文件夹]
 * @param  {[type]} msg [额外信息]
 * @return {[type]}     [json对象,适配layui的表格的数据接口]
 */
util.listFile = function(dir,msg){
	var result = []
	var num = 0;
	files = this.fs.readdirSync(dir);//需要用到同步读取
	for(var i = 0;i < files.length;i++){
		num++;
		states = this.fs.statSync(dir+'/'+files[i]); 
		result.push({"fileName":files[i],"fileSize":this.parseByteSize(states.size,1024),"birthTime":states.birthtime,"updateTime":states.mtime,"isFord":states.isDirectory()?"文件夹":"文件"});
	}
	return {"code":0,"msg":msg,count:num,"data":result};
}
util.listAllFile = function(dir,msg,pattern,dePrefer){
	var result = []
	this.readFileList(dir,result,pattern,dePrefer);
	return {"code":0,"msg":msg,count:result.length,"data":result};
}
/**
 * [readFileList 列出所有文件]
 * @param  {[type]} path      [description]
 * @param  {[type]} filesList [description]
 * @param  {[type]} filesList [需要去掉的前缀]
 * @return {[type]}           [description]
 */
util.readFileList = function(path, filesList,patterns,dePrefer) {
	var that = this;
    var files = this.fs.readdirSync(path);
    files.forEach(function (itm, index) {
        var states = that.fs.statSync(path +'/'+ itm);
        if (states.isDirectory()) {
        //递归读取文件
            that.readFileList(path + "/"+itm, filesList,patterns,dePrefer);
        } else {
        	for(var i = 0;i < patterns.length;i++){
        		if(itm.indexOf(patterns[i]) > 0){
        			//console.log(that.dePrefer);
        			console.log("path:"+path+"defer:"+dePrefer);
            		filesList.push({"fileName":itm,"fileSize":that.parseByteSize(states.size,1024),"birthTime":states.birthtime,"updateTime":states.mtime,"completePath":path.replace(dePrefer,"")});
            		break;
        		}
        	}
        }
    })

}
/**
 * [sendData 向response回写json数据]
 * @param  {[type]} data [json对象]
 * @param  {[type]} req  [请求]
 * @param  {[type]} res  [响应]
 * @return {[type]}      [description]
 */
util.sendData = function(data,req,res){
	res.writeHead(200,{"Content-Type":'text/plain','charset':'utf-8','Access-Control-Allow-Origin':'*','Access-Control-Allow-Methods':'PUT,POST,GET,DELETE,OPTIONS'});
	res.write(JSON.stringify(data),'utf-8');
	res.end();
}
/**
 * [util 将arrayBuffer写入字符串]
 * @param  {[type]} arrayBuffer [description]
 * @param  {[type]} decoder     [description]
 * @return {[type]}             [description]
 */
util.bufferToString = function(arrayBuffer,decoder){
	return this.decoder.decode(new Uint8Array(arrayBuffer));
}
/**
 * [isExist 判断文件是否存在]
 * @param  {[type]}  filePath [description]
 * @return {Boolean}          [description]
 */
util.isExist = function(filePath){
	return this.fs.existsSync(filePath);
}
/**
 * [getdbUrl 根据给定的ip,端口,数据库实例获得链接地址]
 * @return {[type]} [description]
 */
util.getdbUrl = function(ip,port,db){
	//获得mongodburl
	return 'mongodb://'+ip+":"+port+'/'+db;
}
util.queryMongo = function(url,nextDb,collection,condition,field,page,pageSize,req,res,callback){
	//查询数据库
	this.MongoClient.connect(url, function(error, db){
		var db = db.db(nextDb)
	    var col = db.collection(collection);
		col.find(condition).limit(pageSize).skip((page-1)*pageSize).project(field).toArray(function(err,doc){
			callback(doc,req,res);
		})
	});
}
module.exports = util;