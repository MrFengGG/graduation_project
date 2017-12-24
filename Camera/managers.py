#encoding=utf-8
import cv2
import numpy
import socket
import json
import threading

class CameraManager(object):
    #相机管理类
    def __init__(self,capture,windowManager = None,isMirror = False):
        '''
        :param capture: 摄像头对象
        :param windowManager: 钩子类,窗口管理,按键
        :param isMirror: 是否开启镜像
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
        if self._capture is not None:
            _,self._frame = self._capture.read()
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
                cv2.imwrite(self._imageFilename,self._frame)
                self._imageFilename = None
            if self.isWritingVideo():
                #是否写入视频
                self.writeVideo()
    def initWriteImage(self,filename):
        #初始化写入图片文件
        self._imageFilename = filename
    def initWriteVideo(self,filename,fps=60,encoding=cv2.VideoWriter_fourcc("I","4","2","0")):
        #初始化写入视频文件
        self._videoFilename = filename
        self.fps = fps
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
            self._fps = self._fps if self._fps!=0 else self.fps
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
        command = self.commandManager.getCommand()
        if self.commandCallback is not None and command is not None:
            self.commandCallback(command)
class CommandManager(object):
    def __init__(self,ip,port):
        self.ip = ip
        self.port = port
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.sock.bind((self.ip,self.port))
        self.command = None
        self._isWorking = True
        self._task = None
        self.startWorking()
    def _listenCommand(self):
        #开启侦听
        while self._isWorking:
            data, addr = self.sock.recvfrom(1024 * 1024)
            jsondata = json.loads(data.decode())
            self.command = jsondata["command"]
            print(self.command)
    def startWorking(self):
        #开始工作
        self._task = threading.Thread(target=self._listenCommand)
        self._task.start()
    def stopWorking(self):
        #结束工作
        self._isWorking = False
        self.sock.close()
        self._task = None
    def getCommand(self):
        #获得发送的命令
        result = self.command
        self.command = None
        return result

