#encoding=utf-8
import cv2
from managers import CameraManager
from managers import CommandManager
from items import MessageItem
from transmitters import Dispatcher
from monitors import WatchDog,CamShiftTracker,DlibTracker
from threading import Thread
from settings import *
import time
import copy
from utils import IOUtil,logger
'''
主控程序
'''
class Camera(object):
    #主控程序
    def __init__(self,captureManager = None,dispatcher = None,watchDog=None,commandManager=None,tracker=None,isShow=True):
        '''
        :param captureManager: 视屏采集器
        :param dispatcher:信息分发器
        :param watchDog:入侵检测器
        :param tracker:目标追踪器
        :param commandManager:命令管理器
        '''
        logger.info("主控程序初始化...")
        self.captureManager = captureManager if captureManager is not None else CameraManager(cv2.VideoCapture(0))
        self.dispatcher = dispatcher if dispatcher is not None  else Dispatcher()
        self.watchDog = watchDog if watchDog is not None else WatchDog()
        self.commandManager = commandManager if commandManager is not None else CommandManager(commandIp,commandPort)
        self.tracker = tracker if tracker is not None else DlibTracker()
        #是否开启运动检测
        self.isWatching = True
        #是否开启目标追踪
        self.isTracking = False
        #是否开启图像分发
        self.isDispense = True
        #是否在本地显示
        self.isShow = isShow
        #是否开启预警
        self.isWarning = True
        #item为预警器处理后的图像以及坐标信息
        self.item = None
        #原始图像
        self.frame = None
        #检测到运动后拍摄的图片
        self.waraingImage = []
        #发现几次运动目标后开启运动追踪
        self.warnCount = 10
        #拍摄图像间隔
        self.imageDelay = 0.1
        logger.info("主控程序初始化完毕...")
    def _dispatch(self):
        #信息分发线程
        logger.info("是否开启图片分发:"+str(self.isDispense))
        while self.isDispense:
            try:
                self.dispatcher.dispenseImage(self.item,(imageIp,imagePort))
            except EOFError as e:
                print(e)
    def _warning(self):
        #预警线程
        count = 0   #当前运动目标
        box = None  #运动目标位置
        logger.info("是否开启预警模式:"+str(self.isWarning))
        while self.isWarning: 
            #若为运动检测模式,进入运动检测
            if self.isWatching:
                #若未初始化运动检测器,初始化运动检测器
                if not self.watchDog.isWorking():
                    self.watchDog.startWorking(self.frame)
                else:
                    self.item = self.watchDog.update(self.frame)
                if self.item is not None and self.item.getMessage()['isGet']:
                    #若发现动态物体,延时1秒,拍摄10张照片
                    count+=1
                    time.sleep(self.imageDelay)
                    box = IOUtil.countBox(self.item.getMessage()["rect"])
                    logger.info("发现一个运动物体位于"+str(box))
                else:
                    count = 0
                if count >= self.warnCount:
                    #一秒后退出动态监控状态,进入运动追踪模式
                    logger.info("累计侦测到目标十次运动,锁定目标,开启目标追踪模式")
                    count = 0
                    self.stopWatching()
                    self.startTracking(box)
            if self.isTracking:
                #若为运动追踪模式,开启运动追踪
                if not self.tracker.isWorking():
                    print('开始目标追踪,追踪范围为'+str(box))
                    self.tracker.startWorking(self.frame,box)
                else:
                    self.item = self.tracker.update(self.frame)
                if self.item is not None and self.item.getMessage()['isGet']:
                    pass
                else:
                    print("目标丢失,退出目标追踪模式,进入运动监控状态")
                    self.stopTracking()
                    self.startWatching()
    def run(self):
        logger.info("\n################################################################")
        self.startWarning()
        self.startDispatch()
        self.captureManager.start()
        self.commandManager.startWorking()
        logger.info("初始化运动检测器背景采集...")
        time.sleep(1)
        while self.captureManager.isWorking():
            self.frame = self.captureManager.getFrame()
            if self.frame is None:
                continue
            if self.isShow and self.item is not None:
                cv2.imshow("show",self.item.getFrame())
                keycode = cv2.waitKey(1)
                self.onKeypress(keycode)
            self.onCommand(self.commandManager.getCommand())
    def startWarning(self):
        #开启警示
        logger.info("预警功能开启...")
        Thread(target=self._warning,args=()).start()
    def stopWarning(self):
        #关闭警示
        logger.info("预警功能关闭...")
        self.isWarning = False
        self.stopTracking()
        self.stopWatching()
    def startDispatch(self):
        #开启分发
        logger.info("开启分发")
        Thread(target=self._dispatch,args=()).start()
    def startWatching(self):
        #开始动态监控
        logger.info("开启运动检测...")
        self.isWatching = True
    def stopWatching(self):
        #停止动态监控
        logger.info("关闭运动检测")
        self.isWatching = False
        if self.watchDog.isWorking():
            self.watchDog.stopWorking()
    def startTracking(self,frame):
        #开始追踪
        logger.info("开启目标追踪...")
        self.isTracking = True
    def stopTracking(self):
        #停止追踪
        logger.info("关闭目标追踪...")
        self.isTracking = False
        if self.tracker.isWorking():
            self.tracker.stopWorking()
    def onKeypress(self,keycode):
        #按钮回调函数
        if keycode == 32:
            #空格键截图
            self.captureManager.writeImage()
        elif keycode == 9:
            #tab键开启录像
          if not self.captureManager.isWritingVideo():
              self.captureManager.startWritingVideo()
          else:
              self.captureManager.stopWritingVideo()
        elif keycode == 27:
            #esc键结束应用
            self.isDispense = False
            self.captureManager.stop()
            self.commandManager.stopWorking()
            self.dispatcher.close()
            self.isWarning= False
        elif keycode == 97:
            self.isWatching = not self.isWatching
            if self.watchDog.isWorking():
                self.watchDog.stopWorking()
    def onCommand(self,command):
        # 按钮回调函数
        if command == "screensheet":
            # 空格键截图
            self.captureManager.writeImage()
        elif command == "recording":
            #tab键开启录像
          if not self.captureManager.isWritingVideo():
              self.captureManager.startWritingVideo()
          else:
              self.captureManager.stopWritingVideo()
        elif command == "over":
            # esc键结束应用
            self.isDispense = False
            self.captureManager.stop()
            self.commandManager.stopWorking()
            self.dispatcher.close()
            self.isWarning = False
        elif command == "analyze":
            print("状态改变")
            self.isWatching = not self.isWatching
            if self.watchDog.isWorking():
                self.watchDog.stopWorking()
if __name__=="__main__":
    Camera().run()
