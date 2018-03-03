var config = {
	//数据库地址
	ip:"119.23.210.76",
	//数据库端口
	port:"27017",
	//数据库名
	db:"film",
	//数据库集合
	collection:"move",
	//用户名集合
	userCollection:"user",
	//登录过期时间
	expireTime:60 * 1000 * 60,
	//监听命令IP
	commandIP:"127.0.0.1",
	//监听命令端口
	commandPort:9997,
	//图像监听IP
	imageIP:"127.0.0.1",
	//图像监听端口
	imagePort:9998,
	//http请求监听端口
	listenPort:3000,
	//下载目录
	download_path:"D://常用应用",
	//youget路径
	yougetPath:"/usr/local/you-get",
	//云盘根路径
	cludPath:"D://Foreign Sorftware",
	garbPath:"D://学习/代码",
	//文件压缩比例
	compressRate:1,
	//临时文件名称
	tempFileName:"/tmp/temp.zip",
	//上传文件夹
	uploadFilePath:"d://",
	//文件格式设置
	图片:['.jepg','.jpg','.gif','.png','.bmp'],
	文档:['.txt','.log'],
	视频:['.rmvb','.flv'],
	种子:['.terroent'],
	音乐:['.mp3'],
	其他:['.其他'],
	全部文件:['']
}
module.exports = config;