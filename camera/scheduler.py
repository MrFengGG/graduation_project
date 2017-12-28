#encoding=utf-8
import cv2
from managers import WindowManager
from managers import CameraManager
from managers import CommandManager
from items import MessageItem
from transmitters import Dispatcher
from monitors import WatchDog
'''
主控程序
'''
class Camera(object):
    #主控程序
    def __init__(self,windowManager = None,captureManager = None,dispatcher = None,watchDog=None):
        '''
        :param windowManager: 窗口管理器
        :param captureManager: 视屏采集器
        :param dispatcher:信息分发器
        :param watchDog:入侵检测器
        '''
        self.windowManager = windowManager
        self.captureManager = captureManager
        self.dispatcher = dispatcher
        self.watchDog = watchDog
        if not windowManager:
            self.windowManager = WindowManager("cameo",keypressCallback=self.onKeypress,commandCallback=self.onCommand,commandManager=CommandManager(9998))
        if not captureManager:
            self.captureManager = CameraManager(cv2.VideoCapture(0),self.windowManager,True)
        if not dispatcher:
            self.dispatcher = Dispatcher()
        if not watchDog:
            self.watDog = WatchDog()
        self.isWatching = True
    def run(self):
        while self.captureManager.isWorking():
            self.captureManager.nextFrame()
            frame = self.captureManager.getFrame()
            item = MessageItem(frame,None)
            if self.isWatching:
                if not self.watDog.isWorking():
                    self.watDog.startWorking(frame)
                item = self.watDog.analyze(frame)
            self.dispatcher.dispense(item)
            self.dispatcher.dispense(item,("127.0.0.1",9997))
            self.captureManager.processFrame()
            self.windowManager.processKeyEvents()
            self.windowManager.processCommandEvents()
    def onKeypress(self,keycode):
        #按钮回调函数
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
            self.windowManager.stopWorking()
            self.captureManager.stopWorking()
        elif keycode == 8:
            #back键改变镜像
            self.captureManager.changeMirror()
        elif keycode == 13:
            #回车键暂停显示
            self.captureManager.changeShow()
        elif keycode == 97:
            self.isWatching = not self.isWatching
            if self.watDog.isWorking():
                self.watDog.stopWorking()
    def onCommand(self,command):
        # 按钮回调函数
        if command == "screensheet":
            # 空格键截图
            self.captureManager.initWriteImage("screenshoot.png")
        elif command == "recording":
            # tab键开启录像
            if not self.captureManager.isWritingVideo():
                self.captureManager.initWriteVideo("screencast.avi")
            else:
                self.captureManager.stopWriteVideo()
        elif command == "over":
            # esc键结束应用
            self.windowManager.stopWorking()
            self.captureManager.stopWorking()

        elif command == "mirror":
            # back键改变镜像
            self.captureManager.changeMirror()
        elif command == "stop":
            # 回车键暂停显示
            self.captureManager.changeShow()
        elif command == "analyze":
            self.isWatching = not self.isWatching
            if self.watDog.isWorking():
                self.watDog.stopWorking()
if __name__=="__main__":
    Camera().run()