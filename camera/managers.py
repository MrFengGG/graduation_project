#encoding=utf-8
import cv2
import numpy
import socket
import json
import threading
import os
import time
from settings import *

'''
管理者模块,负责控制信息获取,命令获取
'''
class CameraManager(object):
    #相机管理类,负责控制信息获取
    def __init__(self,capture,windowManager = None,isMirror = False):
        '''
        :param capture: 摄像头对象
        :param windowManager: 钩子类,窗口管理,按键
        :param isMirror: 是否开启镜像
        '''

        #从配置文件中读取截图目录和录像目录
        self.screenshot_dir = SCREENSHOT_DIR
        self.video_dir = VIDEO_DIR
        '''
        添加创建文件夹逻辑
        '''
        self._windowManager = windowManager
        self._isMirror = isMirror
        self._capture = capture
        #当前画面
        self._frame = None
        #截图文件
        self._imageFilename = None
        #录像文件
        self._videoFilename = None
        #录像编码
        self._videoEncoding = None
        #视频写入工具
        self._videoWriter = None
        #是否开启延时
        self._isShow = True
        #是否开启工作
        self._isWorking = True
        self._fps = 30
    def getFrame(self):
        #返回当前的帧
        return self._frame
    def isWritingImage(self):
        #是否开启写入图片
        return self._imageFilename is not None
    def isWritingVideo(self):
        #是否开启写入视频
        return self._videoFilename is not None
    def nextFrame(self):
        #读取下一个页面
        timer = cv2.getTickCount()
        if self._capture is not None:
            _,self._frame = self._capture.read()
        self._fps = int(cv2.getTickFrequency() / (cv2.getTickCount() - timer)/100);
        print(self._fps)
    def processFrame(self):
        #处理每一帧图像的函数,其中可以运行包括写入视频,写入图片,显示视频的钩子函数
        if self._windowManager is not None and self._isWorking:
            #是否工作
            if self._isShow:
                #是否开启显示
                if self._isMirror:
                    #是否开启镜像
                    mirrorFrame = numpy.fliplr(self._frame).copy()
                    self._windowManager.show(mirrorFrame)
                else:
                    self._windowManager.show(self._frame)
            if self.isWritingImage():
                #是否写入图片
                self.writeImage(self._imageFilename,self._frame)
            if self.isWritingVideo():
                #是否写入视频
                self.writeVideo()
    def initWriteImage(self,filename=None,imageformat=".png"):
        #初始化写入图片文件,默认文件名为当前时间
        if not filename:
            filename = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
        filename += imageformat
        self._imageFilename = os.path.join(self.screenshot_dir,filename)

    def writeImage(self,filename,frame):
        #写入图片文件
        print("写入一个图片文件,路径为:"+self._imageFilename)
        cv2.imwrite(self._imageFilename,self._frame)
        self._imageFilename = None

    def initWriteVideo(self,filename=None,fps=60,encoding=cv2.VideoWriter_fourcc("I","4","2","0"),videoformat=".avi"):
        #初始化写入视频文件
        if not filename:
            filename = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
        filename += videoformat
        self._videoFilename = os.path.join(self.video_dir,filename)
        self._fps = fps
        self._videoEncoding = encoding
    def stopWriteVideo(self):
        #关闭视频写入
        self._videoFilename = None
        self._videoWriter = None
        self._videoEncoding = None
    def writeVideo(self):
        #写入视频文件
        if self._videoWriter is None:
            self._fps = self._videoWriter = self._capture.get(cv2.CAP_PROP_FPS)
            self._fps = self._fps if self._fps!=0 else 30
            size = (int(self._capture.get(cv2.CAP_PROP_FRAME_WIDTH)),int(self._capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
            print(self._fps)
            self._videoWriter = cv2.VideoWriter(self._videoFilename,self._videoEncoding,self._fps,size)
        self._videoWriter.write(self._frame)
    def changeMirror(self):
        #修改镜像状态
        self._isMirror  = not self._isMirror
    def changeShow(self):
        #是否开启显示
        self._isShow = not self._isShow
    def stopWorking(self):
        #结束工作
        self._isWorking = False
    def startWorking(self):
        #开启工作
        self._isWorking = True
    def isWorking(self):
        #工作控制
        return self._isWorking
class WindowManager(object):
    #视频控制类
    def __init__(self,windowName,keypressCallback = None,commandCallback=None,commandManager=None):
        '''
        :param windowName:窗口名称 
        :param keypressCallback: 按钮回调函数
        '''
        self.keypressCallback = keypressCallback
        self.commandCallback = commandCallback
        self.windowName = windowName
        self._isWindowExist = False
        self.commandManager = commandManager
        self.commandManager.startWorking()
    def isWindowExist(self):
        #是否存在窗口
        return self._isWindowExist
    def createWindow(self):
        #创建一个窗口
        cv2.namedWindow(self.windowName)
        self._isWindowExist = True
    def show(self,frame):
        #显示画面
        cv2.imshow(self.windowName,frame)
    def destoryWindow(self):
        #销毁窗口
        cv2.destroyWindow(self.windowName)
        self._isWindowExist = False
    def stopWorking(self):
        cv2.destroyWindow(self.windowName)
        self._isWindowExist = False
        self.commandManager.stopWorking()
    def processKeyEvents(self):
        #按键事件处理函数
        keycode = cv2.waitKey(1)
        if self.keypressCallback is not None and keycode != -1:
            keycode &= 0xFF
            self.keypressCallback(keycode)
    def processCommandEvents(self):
        #命令时间处理函数
        if self.commandManager:
            command = self.commandManager.getCommand()
            if self.commandCallback is not None and command is not None:
                self.commandCallback(command)
class CommandManager(object):
    '''
    命令管理类,监听一个指定的端口传来的命令,命令为json格式,使用键"command"取出命令
    当传来over命令时候结束监听
    '''
    def __init__(self,port=9998,ip=""):
        '''
        :param port:监听的端口 
        :param ip: 监听的ip(一般不指定)
        '''
        self.ip = ip
        print(self.ip)
        self.port = port
        #构建套接字
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        #监听端口
        print(type(self.ip))
        self.sock.bind((self.ip,self.port))
        #初始化命令
        self.command = None
        #工作线程初始化,放在init函数中,一个管理类只需要初始化一次线程
        self._task = threading.Thread(target=self._listenCommand)
    def _listenCommand(self):
        #开启侦听
        while True:
            data, addr = self.sock.recvfrom(1024 * 1024)
            jsondata = json.loads(data.decode())
            self.command = jsondata["command"]
            #如果接收到over指令,结束侦听
            if self.command == "over":
                break
    def startWorking(self):
        #开始工作,启动侦听线程
        self._task.start()
    def stopWorking(self):
        #发送over信号结束工作
        self._isWorking = False
        self.sock.sendto('{"command":"over"}'.encode(),("127.0.0.1",9998))
    def getCommand(self):
        #获得发送的命令
        result = self.command
        #获取命令之前将本地命令置空,防止命令重复执行
        self.command = None
        return result