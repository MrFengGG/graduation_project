import cv2
import time
import copy
import socket
import multiprocessing
from monitors import WatchDog,CamShiftTracker,DlibTracker
from utils import IOUtil,logger
from managers import CameraManager,CommandManager
from transmitters import Dispatcher,EmailClient
from items import MessageItem
from threading import Thread
from settings import *

def sendEmail(images):
	'''
	发送图片邮件,传入一个图片路径数组参数
	'''
	emailClient = EmailClient(USER_EMAIL,USER_LICENSE)
	imageHtml = ''
	for image in images:
		timeString = image.split(".")[0].split("/")[1].split("_")
		timeString = timeString[0]+"-"+timeString[1]+"-"+timeString[2]+" "+timeString[3]+":"+timeString[4]+":"+timeString[5]
		imageHtml += "<p>"+timeString+"</br><image src='cid:"+image+"></p>"
	emailClient.sendHtml(TARGET_EMAIL,"入侵警报","<p>发现移动物体</p><p>信息如下</p>"+imageHtml,images)
def startSendEmail(images):
	'''
	开启发送图片线程
	'''
	multiprocessing.Process(target=sendEmail,args=(images,)).start()
def show(mydict):  
	'''
	用于本机调试图像识别的图像显示函数
	'''
	while True:
		item = mydict['item']
		if item is not None:
			cv2.imshow("track",item.getFrame())
			k = cv2.waitKey(1) & 0xff
			if k == 27:
				break
def startShow(mydict):
	'''
	开启本机显示线程
	'''
	multiprocessing.Process(target=show,args=(mydict,)).start()
def warning(mydict,screenCenter):
	'''
	开启预警
	'''
	box = None
	warnImages = []
	watchDog = WatchDog()
	tracker = DlibTracker()
	sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
	IOUtil.mkdir(WARN_DIR)
	isWatching = True
	isTracking = False
	direction = {"right":'{"module":2,"command":0}',
	              "left":'{"module":2,"command":1}',
	                "up":'{"module":2,"command":3}',
	              "down":'{"module":2,"command":2}'}
	logger.info("是否开启预警模式:"+str(mydict['isWarning']))
	while mydict['isWarning']: 
		item = None
		#若为运动检测模式,进入运动检测
		if isWatching:
			#若未初始化运动检测器,初始化运动检测器
			if not watchDog.isWorking():
				watchDog.startWorking(mydict['frame'])
			else:
				item = watchDog.update(mydict['frame'])
				mydict['item'] = item
			if item is not None and item.getMessage()['isGet']:
				#若发现动态物体,延时1秒,拍摄10张照片
				imageFileName = WARN_DIR + IOUtil.getImageFileName()
				warnImages.append(imageFileName)
				time.sleep(MOVEMENT_TRACK_DELAY)
				box = IOUtil.countBox(item.getMessage()["rect"])
				logger.info("发现一个运动物体位于"+str(box))
				cv2.imwrite(imageFileName,item.getFrame())
				logger.info("写入一张预警图片:"+imageFileName)
			else:
				warnImages = []
			if len(warnImages) >= MOVE_TRACK_COUNT:
				#一秒后退出动态监控状态,进入运动追踪模式
				logger.info("累计侦测到目标十次运动,锁定目标,开启目标追踪模式,关闭运动检测")
				startSendEmail(warnImages)
				isWatching = False
				if watchDog.isWorking():
					watchDog.stopWorking()
				logger.info("开启目标追踪...")
				isTracking = True
		if isTracking:
            #若为运动追踪模式,开启运动追踪
			if not tracker.isWorking():
				logger.info('开始目标追踪,初始化追踪范围为'+str(box))
				tracker.startWorking(mydict['frame'],box)
			else:
				item = tracker.update(mydict['frame'])
			if item is not None and item.getMessage()['isGet']:
				mydict['item'] = item
				center = item.getMessage()['center']
				levelDirect = "right" if center[0] - screenCenter[0] < 0 else "left"
				levelDiss = abs(center[0] - screenCenter[0])
				if levelDiss > MOVEMENT_THRESHOLD:
					sock.sendto(direction[levelDirect].encode(),(CAMERA_COMMAND_IP,CAMERA_COMMAND_PORT))
				virtDirect = "up" if center[1] - screenCenter[1] < 0 else "down"
				virtDiss = abs(center[1] - screenCenter[1])
				if virtDiss > MOVEMENT_THRESHOLD:
					sock.sendto(direction[virtDirect].encode(),(CAMERA_COMMAND_IP,CAMERA_COMMAND_PORT))
			else:
				logger.info("目标丢失,退出目标追踪模式,进入运动监控状态")
				isTracking = False
				if tracker.isWorking():
					tracker.stopWorking()
				logger.info("开启运动检测...")
				isWatching = True
	sock.close()
	logger.info("预警结束")
def startWarning(mydict,screenCenter):
	'''
	开启预警线程
	'''
	mydict['isWarning'] = True
	multiprocessing.Process(target=warning,args=(mydict,screenCenter,)).start()
def stopWarning(mydict):
	'''
	关闭预警线程
	'''
	mydict['isWarning'] = False
	logger.info("关闭预警")
def dispense(mydict):
	'''
	图片分发
	'''
	logger.info("是否开启图片分发:"+str(mydict['isDispense']))
	dispatcher = Dispatcher()
	while mydict['isDispense']:
		try:
			dispatcher.dispenseImage(mydict['item'],(IMAGE_IP,IMAGE_PORT))
		except EOFError as e:
			print(e)
	dispatcher.close()
def dispensePlus(mydict):
	'''
	图片分发额外进程
	'''
	logger.info("是否开启图片分发增强:"+str(mydict['isDispensePlus']))
	dispatcher = Dispatcher()
	while mydict['isDispensePlus']:
		try:
			dispatcher.dispenseImage(mydict['item'],(IMAGE_IP,IMAGE_PORT))
		except EOFError as e:
			print(e)
	dispatcher.close()
def startDispensePlus(mydict):
	'''
	开启图片分发额外进程
	'''
	mydict['isDispensePlus'] = True
	multiprocessing.Process(target=dispensePlus,args=(mydict,)).start()
def stopDispensePlus(mydict):
	'''
	关闭图片分发额外进程
	'''
	mydict['isDispensePlus'] = False
	logger.info("关闭图片分发增强进程")
def startDispense(mydict):
	'''
	开启图片分发进程
	'''
	mydict['isDispense'] = True
	multiprocessing.Process(target=dispense,args=(mydict,)).start()
def stopDispense(mydict):
	mydict['isDispense'] = False
	logger.info("关闭图片分发")
def onCommandGet(command,captureManager,mydict,screenCenter):
	'''
	命令监听
	'''
	if command is None:
		return
	# 按钮回调函数
	if command == "screensheet":
	    # 空格键截图
	    captureManager.writeImage()
	elif command == "recording":
	    #tab键开启录像
	  if not captureManager.isWritingVideo():
	      captureManager.startWritingVideo()
	  else:
	      captureManager.stopWritingVideo()
	elif command == "analyze":
		isWarning = mydict['isWarning']
		logger.info("预警状态改变为"+str(not isWarning))
		if not isWarning:
			startWarning(mydict,screenCenter)
			stopDispensePlus(mydict)
		else:
			startDispensePlus(mydict)
			stopWarning(mydict)
if __name__=="__main__":
	mydict=multiprocessing.Manager().dict() 
	mydict['isWorking'] = True
	mydict['isWarning'] = True
	mydict['isDispense'] = True
	mydict['isDispensePlus'] = False
	mydict['item'] = None
	mydict['frame'] = None
	video = cv2.VideoCapture(0)
	captureManager = CameraManager(video)
	commandManager = CommandManager(IMAGE_COMMAND_IP,IMAGE_COMMAND_PORT)
	screenCenter = (int(video.get(cv2.CAP_PROP_FRAME_WIDTH)/2),int(video.get(cv2.CAP_PROP_FRAME_HEIGHT)/2))
	commandManager.startWorking()
	captureManager.start()
	time.sleep(1)
	#startShow(mydict)
	startWarning(mydict,screenCenter)
	startDispense(mydict)
	while mydict['isWorking']:
		frame = captureManager.getFrame()
		mydict['frame'] = frame
		message = {}
		message['isGet'] = False
		mydict['item'] = MessageItem(frame,message)
		onCommandGet(commandManager.getCommand(),captureManager,mydict,screenCenter)

