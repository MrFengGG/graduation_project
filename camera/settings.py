#照片保存文件夹
SCREENSHOT_DIR = "screenshots/"
#视频保存文件夹
VIDEO_DIR = "videos/"
#预警图片文件夹
WARN_DIR = "warn/"
#日志文件夹
LOG_DIR = "log/"
#日志文件
LOG_FILE = "camera.log"
#命令监听ip
IMAGE_COMMAND_IP = ""
#命令监听端口
IMAGE_COMMAND_PORT = 9998
#图像发送IP
IMAGE_IP = "127.0.0.1"
#图像发送端口
IMAGE_PORT = 9999
#日志输出格式
LOG_FORMATTER = "%(asctime)s %(levelname)-8s: %(message)s"
#日志输出名称
LOG_NAME = 'cameraLogger'
#运动物体拍照间隔
MOVEMENT_TRACK_DELAY = 0.5 
#经过多少次运动检测后开启目标追踪
MOVE_TRACK_COUNT = 2
#是否发送邮件
IS_SEND_EMAIL = False
#邮件发送间隔
EMAIL_DELAY = 10
#宿主邮箱
USER_EMAIL = '763484204@qq.com'
#宿主邮箱服务器口令
USER_LICENSE = "edbecalqanpobefj"
#预警邮件发送邮箱
TARGET_EMAIL = '763484204@qq.com'
#移动阈值
MOVEMENT_THRESHOLD = 20
#摄像头命令端口
CAMERA_COMMAND_PORT = 9997
#摄像头命令IP
CAMERA_COMMAND_IP = "127.0.0.1"
#追踪器类型,1为camshift,2为dlib,3为
TRACKER_TYPE = 3
#追踪器阈值
TRACK_THRESHOLD = 0.97
#追踪器更新阈值
TRACKER_UPDATE_THRESHOLD = 0.97
#是否打开本地窗口
IS_WINDOW_ON = False
