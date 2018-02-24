#encoding=utf-8
import cv2
import numpy
import socket
import json
import threading
import os
import time
import copy
from settings import *
from threading import Thread
from utils import IOUtil,logger

'''
管理者模块,负责控制信息获取,命令获取
'''
class CameraManager(object):
    #相机管理类,负责控制信息获取
    def __init__(self,capture):
        '''
        :param capture: 摄像头对象
        :param windowManager: 钩子类,窗口管理,按键
        '''
        #从配置文件中读取截图目录和录像目录创建文件夹
        self.screenshot_dir = SCREENSHOT_DIR
        self.video_dir = VIDEO_DIR
        self._capture = capture
        #当前画面
        self._frame = None
        #录像编码
        self._videoEncoding = None
        #视频写入工具
        self._videoWriter = None
        #是否开启显示
        self._isShow = False
        #是否工作
        self._isWorking = True
        #fps
        self._fps = 0
        #是否正在写入视频
        self._videoFilename = None
        IOUtil.mkdir(self.screenshot_dir)
        IOUtil.mkdir(self.video_dir)
        logger.info("视频采集器初始化完毕!")
    def getFrame(self):
        #返回当前的帧
        return copy.copy(self._frame)
    def getFps(self):
        #获得当前fps
        return self._fps
    def isWritingVideo(self):
        #是否正在写入视频
        return self._videoFilename is not None
    def start(self):
        #开始工作
        logger.info("开启视频采集")
        frameThread = Thread(target = self._update,args=())
        frameThread.start()
        return self
    def stop(self):
        #停止工作
        self._isWorking = False
        self._videoFilename = None
        logger.info("关闭视频采集")
    def _update(self):
        #更新摄像头画面
        logger.info("视频采集线程启动...")
        while self._isWorking:
            startTime = time.time()
            if self._capture is not None:
                _,self._frame = self._capture.read()
            try:
                self._fps = 1/(time.time() - startTime)
            except:
                self._fps = 30
        logger.info("视频采集线程关闭...")
    def getImageFileName(self,filename=None,imageformat=".png"):
        #获得图片文件名
        if not filename:
            filename = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
        filename += imageformat
        return os.path.join(self.screenshot_dir,filename)
    def writeImage(self):
        #写入图片文件
        logger.info("开始写入一张图片")
        imageFileName = self.getImageFileName()
        try:
            cv2.imwrite(imageFileName,self._frame)
        except Exception as e:
            logger.error("写入图片失败:"+str(e))
        logger.info("写入图片成功"+imageFileName)
    def getVideoFileName(self,filename=None,videoformat=".avi"):
        #获得视频文件名
        if not filename:
            filename = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
        filename += videoformat
        return os.path.join(self.video_dir,filename)
    def startWritingVideo(self,filename=None,encoding=cv2.VideoWriter_fourcc("I","4","2","0"),videoformat=".avi"):
        #初始化写入视频文件
        logger.info("开启视频录制")
        self._videoFilename = self.getVideoFileName()
        self._videoEncoding = encoding
        Thread(target = self._writingVideo,args=()).start()
    def stopWritingVideo(self):
        #关闭视频写入
        self._videoFilename = None
        self._videoWriter = None
        self._videoEncoding = None
    def _writingVideo(self):
        #写入视频文件
        logger.info("视频采集线程启动,目标文件为:"+self._videoFilename)
        if self._videoWriter is None:
                size = (int(self._capture.get(cv2.CAP_PROP_FRAME_WIDTH)),int(self._capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
                self._videoWriter = cv2.VideoWriter(self._videoFilename,self._videoEncoding,self._fps,size)
        while self._videoFilename is not None:
            self._videoWriter.write(self._frame)
        logger.info("写入视频完毕,文件名为:"+self._videoFilename)
    def isWorking(self):
        #工作控制
        return self._isWorking
class CommandManager(object):
    '''
    命令管理类,监听一个指定的端口传来的命令,命令为json格式,使用键"command"取出命令
    当传来over命令时候结束监听
    '''
    def __init__(self,ip,port):
        self.ip = ip
        self.port = port
        #构建套接字
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        #监听端口
        self.sock.bind((self.ip,self.port))
        #初始化命令
        self.command = None
        #控制工作流
        self._isWorking = False
        logger.info("命令监听器初始化完毕!")
    def _listenCommand(self):
        #开启侦听
        logger.info("开启命令监听线程...")
        logger.info("开始监听IP:%s,PORT:%d"%(self.ip,self.port))
        while self._isWorking:
            data = None
            try:
                data, addr = self.sock.recvfrom(1024)
            except Exception as e:
                logger.error("命令监听线程出错,错误原因"+str(e))
            jsondata = json.loads(data.decode())
            self.command = jsondata["command"]
            logger.info("捕获到一条命令:"+self.command)
            #如果接收到over指令,结束侦听
            if self.command == "over":
                break
        logger.info("结束命令监听")
    def startWorking(self):
        #开始工作,启动侦听线程
        logger.info("开启命令监听")
        self._isWorking = True
        threading.Thread(target=self._listenCommand,args=()).start()
    def stopWorking(self):
        self._isWorking = False
        self.sock.sendto('{"command":"over"}'.encode(),("127.0.0.1",self.port))
        logger.info("发送结束命令,结束命令监听")
    def getCommand(self):
        #获得发送的命令
        result = self.command
        #获取命令之前将本地命令置空,防止命令重复执行
        self.command = None
        return result        
if __name__ == "__main__":
    video = cv2.VideoCapture(0)
    camera = CameraManager(video)
    camera.start()
    while True:
        frame = camera.getFrame()
        if frame is not None:
            cv2.imshow("track",frame)
            k = cv2.waitKey(1) & 0xff
            if k == 27:
                camera.stop()
                break
            elif k == 9:
            #tab键开启录像
              if not camera.isWritingVideo():
                  camera.startWritingVideo()
              else:
                  camera.stopWritingVideo()
            elif k == 32:
                #空格键截图
                camera.writeImage()