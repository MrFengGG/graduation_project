import sys
#照片保存文件夹
SCREENSHOT_DIR = "screenshots/"
#视频保存文件夹
VIDEO_DIR = "videos/"
#预警信息文件夹
WARN_DIR = "warn/"
#日志文件夹
LOG_DIR = "log/"
#日志文件
LOG_FILE = "camera.log"
#命令监听ip
commandIp = ""
#命令监听端口
commandPort = 9998
#图像发送IP
imageIp = "127.0.0.1"
#图像发送端口
imagePort = 9999
#日志输出格式
logFormatter = "%(asctime)s %(levelname)-8s: %(message)s"
#日志输出名称
logName = 'cameraLogger'
#日志文件路径
logFile = LOG_DIR + LOG_FILE
#运动物体拍照间隔
moveTrackDelay = 0.5 
#经过多少次运动检测后开启目标追踪
moveToTrackThreshold = 10