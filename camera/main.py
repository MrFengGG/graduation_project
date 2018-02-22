import cv2
import time
import copy
import multiprocessing
from monitors import WatchDog,CamShiftTracker,DlibTracker
from utils import IOUtil,logger
from managers import CameraManager,CommandManager
from transmitters import Dispatcher,EmailClient
from items import MessageItem
from threading import Thread
from settings import *

def sendEmail(images):
	emailClient = EmailClient()
	imageHtml = ''
	for image in images:
		timeString = image.split(".")[0].split("/")[1].split("_")
		timeString = timeString[0]+"-"+timeString[1]+"-"+timeString[2]+" "+timeString[3]+":"+timeString[4]+":"+timeString[5]
		imageHtml += "<p>"+timeString+"</br><image src='cid:"+image+"></p>"
	emailClient.sendHtml(userEmail,"入侵警报","<p>发现移动物体</p><p>信息如下</p>"+imageHtml,images)
def startSendEmail(images):
	multiprocessing.Process(target=sendEmail,args=(images,)).start()
def show(mydict):  
	while True:
		item = mydict['item']
		if item is not None:
			cv2.imshow("track",item.getFrame())
			k = cv2.waitKey(1) & 0xff
			if k == 27:
				break
def startShow(mydict):
	multiprocessing.Process(target=show,args=(mydict,)).start()
def warning(mydict,screenCenter):
	#预警线程
	box = None  #运动目标位置
	warnImages = []
	logger.info("是否开启预警模式:"+str(mydict['isWarning']))
	IOUtil.mkdir(WARN_DIR)
	watchDog = WatchDog()
	tracker = DlibTracker()
	isWatching = True
	isTracking = False
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
				time.sleep(moveTrackDelay)
				box = IOUtil.countBox(item.getMessage()["rect"])
				logger.info("发现一个运动物体位于"+str(box))
				cv2.imwrite(imageFileName,item.getFrame())
				logger.info("写入一张预警图片:"+imageFileName)
			else:
				warnImages = []
			if len(warnImages) >= moveToTrackThreshold:
				#一秒后退出动态监控状态,进入运动追踪模式
				logger.info("累计侦测到目标十次运动,锁定目标,开启目标追踪模式")
				logger.info("关闭运动检测")
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
				print("x:"+str(screenCenter[0]-center[0])+",y:"+str(screenCenter[1]-center[1]))
			else:
				logger.info("目标丢失,退出目标追踪模式,进入运动监控状态")
				logger.info("关闭目标追踪...")
				isTracking = False
				if tracker.isWorking():
					tracker.stopWorking()
				logger.info("开启运动检测...")
				isWatching = True
def startWarning(mydict,screenCenter):
	multiprocessing.Process(target=warning,args=(mydict,screenCenter,)).start()
def stopWarning(mydict):
	mydict['isWarning'] = False
	logger.info("关闭预警")
def dispense(mydict):
	logger.info("是否开启图片分发:"+str(mydict['isDispense']))
	dispatcher = Dispatcher()
	while mydict['isDispense']:
		try:
			dispatcher.dispenseImage(mydict['item'],(imageIp,imagePort))
		except EOFError as e:
			print(e)
def startDispense(mydict):
	multiprocessing.Process(target=dispense,args=(mydict,)).start()
def stopDispense(mydict):
	mydict['isDispense'] = False
	logger.info("关闭图片分发")
def onCommandGet(mydict):
	pass
if __name__=="__main__":
	mydict=multiprocessing.Manager().dict() 
	mydict['isWorking'] = True
	mydict['isWarning'] = False
	mydict['isDispense'] = True
	mydict['item'] = None
	video = cv2.VideoCapture(0)
	captureManager = CameraManager(video)
	screenCenter = (int(video.get(cv2.CAP_PROP_FRAME_WIDTH)/2),int(video.get(cv2.CAP_PROP_FRAME_HEIGHT)/2))
	captureManager.start()
	time.sleep(1)
	startShow(mydict)
	#startWarning(mydict,screenCenter)
	startDispense(mydict)
	onCommandGet(mydict)
	while mydict['isWorking']:
		frame = captureManager.getFrame()
		mydict['frame'] = frame
		if not mydict['isWarning']:
			message = {}
			message['isGet'] = False
			mydict['item'] = MessageItem(frame,message)

