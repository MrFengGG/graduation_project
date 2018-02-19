import cv2
import time
import copy
import multiprocessing
from managers import CameraManager
from managers import CommandManager
from items import MessageItem
from transmitters import Dispatcher
from monitors import WatchDog,CamShiftTracker,DlibTracker
from threading import Thread
from settings import *
from utils import IOUtil,logger
 
def show(mydict):  
	while True:
		if 'frame' in mydict and mydict['frame'] is not None:
			cv2.imshow("track",mydict['frame'])
		else:
			print("没有")
		k = cv2.waitKey(1) & 0xff
		if k == 27:
			break
def startShow(mydict):
	multiprocessing.Process(target=show,args=(mydict,)).start()
def warning(mydict):
	#预警线程
	count = 0   #当前运动目标
	box = None  #运动目标位置
	logger.info("是否开启预警模式:"+str(mydict['isWarning']))
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
				count+=1
				time.sleep(moveTrackDelay)
				box = IOUtil.countBox(mydict['item'].getMessage()["rect"])
				logger.info("发现一个运动物体位于"+str(box))
			else:
				count = 0
			if count >= moveToTrackThreshold:
				#一秒后退出动态监控状态,进入运动追踪模式
				logger.info("累计侦测到目标十次运动,锁定目标,开启目标追踪模式")
				count = 0
				logger.info("关闭运动检测")
				isWatching = False
				if watchDog.isWorking():
					watchDog.stopWorking()
				logger.info("开启目标追踪...")
				isTracking = True
		if isTracking:
            #若为运动追踪模式,开启运动追踪
			if not tracker.isWorking():
				print('开始目标追踪,追踪范围为'+str(box))
				tracker.startWorking(mydict['frame'],box)
			else:
				item = tracker.update(mydict['frame'])
				mydict['item'] = tracker.update(mydict['frame'])
			if item is not None and item.getMessage()['isGet']:
				pass
			else:
				logger.info("目标丢失,退出目标追踪模式,进入运动监控状态")
				logger.info("关闭目标追踪...")
				isTracking = False
				if tracker.isWorking():
					tracker.stopWorking()
				logger.info("开启运动检测...")
				isWatching = True
def startWarning(mydict):
	multiprocessing.Process(target=warning,args=(mydict,)).start()
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
if __name__=="__main__":
	mydict=multiprocessing.Manager().dict() 
	mydict['isWorking'] = True
	mydict['isWarning'] = True
	mydict['isDispense'] = True
	mydict['item'] = None
	captureManager = CameraManager(cv2.VideoCapture(0))
	captureManager.start()
	time.sleep(1)
	startShow(mydict)
	startWarning(mydict)
	startDispense(mydict)
	while mydict['isWorking']:
		mydict['frame'] = captureManager.getFrame()
