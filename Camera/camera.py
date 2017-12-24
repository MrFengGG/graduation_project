#encoding=utf-8
import cv2
from managers import WindowManager
from managers import CameraManager
from items import MessageItem
from dispatchers import Dispatcher
from analyzers import MoveAnalyzer
class Camera(object):
    #主控程序
    def __init__(self,windowManager = None,captureManager = None,dispatcher = None,analyzers=None):
        '''
        :param windowManager: 窗口管理器
        :param captureManager: 视屏采集器
        '''
        if windowManager:
            self.windowManager = windowManager
        if captureManager:
            self.captureManager = captureManager
        if not windowManager:
            self.windowManager = WindowManager("cameo",self.onKeypress)
        if not captureManager:
            self.captureManager = CameraManager(cv2.VideoCapture(0),self.windowManager,True)
        if not dispatcher:
            self.dispatcher = Dispatcher()
        if not analyzers:
            self.analyzers = MoveAnalyzer()
        self.isAnalyze = True
    def run(self):
        while self.captureManager.isWorking():
            self.captureManager.nextFrame()
            frame = self.captureManager.getFrame()

            '''
            进行图像处理,视屏分发
            '''
            item = MessageItem(frame,None)
            if self.isAnalyze:
                if not self.analyzers.isWorking():
                    self.analyzers.startWorking(frame)
                item = self.analyzers.analyze(frame)
            self.dispatcher.dispense(item)
            self.captureManager.processFrame()
            self.windowManager.processEvents()
    def onKeypress(self,keycode):
        #按钮回调函数
        print(keycode)
        if keycode == 32:
            #空格键截图
            self.captureManager.initWriteImage("screenshoot.png")
        elif keycode == 9:
            #tab键开启录像
          if not self.captureManager.isWritingVideo():
              self.captureManager.initWriteVideo("screencast.avi")
          else:
              self.captureManager.stopWriteVideo()
        elif keycode == 27:
            #esc键结束应用
            self.windowManager.destoryWindow()
            self.captureManager.stopWorking()
        elif keycode == 8:
            #back键改变镜像
            self.captureManager.changeMirror()
        elif keycode == 13:
            #回车键暂停显示
            self.captureManager.changeShow()
        elif keycode == 97:
            self.isAnalyze = not self.isAnalyze
            if self.analyzers.isWorking():
                self.analyzers.stopWorking()

if __name__=="__main__":
    Camera().run()




