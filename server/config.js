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
	download_path:"/tmp"

}
module.exports = config;