#encoding=utf-8
import cv2
import numpy
import time

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
        self._frame = None
        self._imageFilename = None
        self._videoFilename = None
        self._videoEncoding = None
        self._videoWriter = None
        self._isShow = True
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
        if self._windowManager is not None:
            if self._isShow:
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
    #窗口管理类
    def __init__(self,windowName,keypressCallback = None):
        '''
        :param windowName:窗口名称 
        :param keypressCallback: 按钮回调函数
        '''
        self.keypressCallback = keypressCallback
        self.windowName = windowName
        self._isWindowExist = False
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
    def processEvents(self):
        #事件处理函数
        keycode = cv2.waitKey(1)
        if self.keypressCallback is not None and keycode != -1:
            keycode &= 0xFF
            self.keypressCallback(keycode)

