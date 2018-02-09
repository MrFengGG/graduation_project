#encoding=utf-8
import cv2
import dlib
import time
import numpy as np
import logging
import sys
from utils import IOUtil,logger
from items import MessageItem

#利用侦差法的基本的运动检测模块
class WatchDog(object):
    def __init__(self,frame=None):
        #运动检测器构造函数
        self._background = None
        if frame is not None:
            self._background = cv2.GaussianBlur(cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY),(21,21),0)
        self.es = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10, 10))
        logger.info("运动检测器初始化完毕")
    def isWorking(self):
        #运动检测器是否工作
        return self._background is not None
    def startWorking(self,frame):
        #运动检测器开始工作
        if frame is not None:
            self._background = cv2.GaussianBlur(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), (21, 21), 0)
            logger.info("运动检测器开始工作")
    def stopWorking(self):
        #运动检测器结束工作
        self._background = None
        logger.info("运动检测器结束工作")
    def update(self,frame):
        #运动检测
        if frame is None:
            return
        if not self.isWorking():
            logger.error("运动检测器未初始化")
            raise Exception("运动检测器未初始化")
        item = None
        sample_frame = cv2.GaussianBlur(cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY),(21,21),0)
        diff = cv2.absdiff(self._background,sample_frame)
        diff = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]
        diff = cv2.dilate(diff, self.es, iterations=2)
        image, cnts, hierarchy = cv2.findContours(diff.copy(),cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        bigC = None
        bigMulti = 0
        for c in cnts:
            if cv2.contourArea(c) < bigMulti:
                continue
            bigMulti = cv2.contourArea(c)
            (x,y,w,h) = cv2.boundingRect(c)
            bigC = ((x,y),(x+w,y+h))
        message = {}
        if bigC is not None:
            center = IOUtil.countCenter(bigC)
            cv2.circle(frame,center,5,(55,255,155),1)
            cv2.rectangle(frame, bigC[0],bigC[1], (255,0,0), 2, 1)
            message['isGet'] = True
            message['center'] = center
            message["rect"] = bigC 
            message['time'] = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
            item = MessageItem(frame,message)
        else:
            message['isGet'] = False
            item = MessageItem(frame,message)
        return item
#利用背景减除法的运动检测模块
class KnnWatchDog(object):
    def knnTrack(self):
        bs = cv2.createBackgroundSubtractorKNN(detectShadows = True)
        capture = cv2.VideoCapture(0)
        while True:
            ret,frame = capture.read()
            fgmask = bs.apply(frame)
            th = cv2.threshold(fgmask.copy(),244,255,cv2.THRESH_BINARY)[1]
            dilated = cv2.dilate(th,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3)),iterations=2)
            image,contours,hier = cv2.findContours(dilated,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
            for c in contours:
                if cv2.contourArea(c) > 1600:
                    (x,y,w,h) = cv2.boundingRect(c)
                    cv2.rectangle(frame,(x,y),(x+w,y+h),(255,255,0),2)
                    cv2.imshow("mog",fgmask)
                    cv2.imshow("thresh",th)
                    cv2.imshow("detection",frame)
                    if cv2.waitKey(30) & 0xff==27:
                        break
#依赖contrib的追踪器
class ContribTracker(object):
    def __init__(self,tracker_type = "BOOSTING"):
        '''
        初始化追踪器,可选6种算法,分别为
        'BOOSTING', 'MIL','KCF', 'TLD', 'MEDIANFLOW', 'GOTURN'
        默认选择BOOSTING
        '''
        self.tracker_type = tracker_type
        self._isWorking = False
        #构造追踪器
        self.tracker = self.initTracker(self.tracker_type)
        logger.info("追踪器初始化完毕,类型为:"+"ContribTracker")
    def initTracker(self,tracker_type):
        tracker = None
        if tracker_type == 'BOOSTING':
            tracker = cv2.TrackerBoosting_create()
        elif tracker_type == 'MIL':
            tracker = cv2.TrackerMIL_create()
        elif tracker_type == 'KCF':
            tracker = cv2.TrackerKCF_create()
        elif tracker_type == 'TLD':
            tracker = cv2.TrackerTLD_create()
        elif tracker_type == 'MEDIANFLOW':
            tracker = cv2.TrackerMedianFlow_create()
        elif tracker_type == 'GOTURN':
            tracker = cv2.TrackerGOTURN_create()
        else:
            logger.error("contrb追踪器算法选择错误")
            raise Exception("没有此类追踪器"+tracker_type)
        return tracker
    def isWorking(self):
        return self._isWorking
    def stopWorking(self):
        self.tracker = initTracker(self.tracker_type)
    def startWorking(self,frame,box):
        status = self.tracker.init(frame,box)
        if not status:
            self._isWorking = False
            logger.error('追踪器追踪区域锁定失败')
            return
        self.coord = box
        self._isWorking = True
        logger.info("追踪器开始工作")
    def update(self,frame):
        if frame is None:
            return
        if not self.isWorking():
            logger.error('追踪器未初始化')
            raise Exception("追踪器未初始化")
        item = None
        message = {}
        status,coord = self.tracker.update(frame)
        if status:
            rect = (
                    (int(coord[0]),int(coord[1])),
                    (int(coord[0] + coord[2]),int(coord[1]+coord[3])))
            center = IOUtil.countCenter(rect)
            cv2.rectangle(frame, rect[0], rect[1], (255,0,0), 2, 1)
            message['isGet'] = True
            message['center'] = center
            message["rect"] = rect
            message['time'] = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
        else:
            message['isGet'] = False
        return MessageItem(frame,message)
#使用CamShift的追踪器
class CamShiftTracker(object):
    def __init__(self):
        self._isWorking = False
        self.loseDistance = 30
        logger.info("追踪器初始化完毕,类型为:"+"CamShiftTracker")
    def startWorking(self,frame,box):
        if frame is None:
            self._isWorking = False
            logger.error('追踪器追踪区域锁定失败')
            return
        c,r,w,h = box
        roi = frame[r:r+h, c:c+w]
        self.track_window = (c,r,w,h)
        self.hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(self.hsv_roi, np.array((0., 30.,32.)), np.array((180.,255.,255.)))
        self.roi_hist = cv2.calcHist([self.hsv_roi], [0], mask, [180], [0, 180])
        cv2.normalize(self.roi_hist, self.roi_hist, 0, 255, cv2.NORM_MINMAX)
        self.term_crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 80, 10)
        self._isWorking = True
        logger.info("追踪器开始工作")
    def stopWorking(self):
            self._isWorking = False
            self.track_window = None
            self.hsv_roi = None
            self.roi_hist = None
            self.term_crit = None
            logger.info("追踪器结束工作")
    def isWorking(self):
        return self._isWorking
    def update(self,frame):
        if frame is None:
            return
        if not self.isWorking():
            logger.error('追踪器未初始化')
            raise Exception("跟踪器未初始化")
        item = None
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        dst = cv2.calcBackProject([hsv], [0], self.roi_hist, [0,180], 1)
        #ret, self.track_window = cv2.meanShift(dst, self.track_window, self.term_crit)
        ret, self.track_window = cv2.CamShift(dst, self.track_window, self.term_crit)
        x,y,w,h = self.track_window
        center = IOUtil.countCenter(((x,y),(x+w,y+h)))
        cv2.circle(frame,center,5,(55,255,155),1)
        cv2.rectangle(frame, (x,y), (x+w,y+h), 255, 2)
        cv2.putText(frame, 'Tracked', (x-25,y-10), cv2.FONT_HERSHEY_SIMPLEX,
            1, (255,255,255), 2, cv2.LINE_AA)
        screenSize = frame.shape
        #print(center[0],":",center[1],":",abs(center[0] - screenSize[1]),":",abs(center[1] - screenSize[0]))
        message = {}
        if(center[0] > self.loseDistance and center[1] > self.loseDistance and abs(center[0] - screenSize[1]) > self.loseDistance and abs(center[1] - screenSize[0]) > self.loseDistance):
            message['isGet'] = True
            message['center'] = center
            message["rect"] = ((x,y),(x+w,y+h))
            message['time'] = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
        else:
            message['isGet'] = False
        return MessageItem(frame,message)
#使用模板查找的追踪器
class TemplateTracker(object):
    def __init__(self,method=2):
        self.method = method
        self.valThre = 0.97
        self.updateRet = 0.98
        self._isWorking = False
        logger.info("追踪器初始化完毕,类型为:"+"TemplateTracker")
    def startWorking(self,frame,box):
        if frame is None:
            self._isWorking = False
            logger.error('追踪器追踪区域锁定失败')
            return
        c,r,w,h = box
        self.objectFrame = frame[r:r+h, c:c+w]
        self.h = h
        self.w = w
        self._isWorking = True
        logger.info('追踪器开始工作')
    def isWorking(self):
        return self._isWorking
    def update(self,frame):
        if frame is None:
            return
        if not self.isWorking():
            logger.error('追踪器未初始化')
            raise Exception("跟踪器未初始化")
        item = None
        message = {}
        result = cv2.matchTemplate(frame,self.objectFrame,self.method)
        minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(result)
        if maxVal > self.updateRet:
            pass
            #self.objectFrame = frame[maxLoc[0]:maxLoc[0]+self.w,maxLoc[1]:maxLoc[1]+self.h]
        if maxVal > self.valThre:
            center = IOUtil.countCenter((maxLoc,(maxLoc[0] + self.w,maxLoc[1] + self.h)))
            cv2.rectangle(frame, maxLoc,(maxLoc[0] + self.w,maxLoc[1] + self.h), 255, 2)
            message['isGet'] = True
            message['center'] = center
            message["rect"] = (maxLoc,(maxLoc[0] + self.w,maxLoc[1] + self.h))
            message['time'] = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
        else:
            message['isGet'] = False
        return MessageItem(frame,message)
#使用dlib的追踪器
class DlibTracker(object):
    def __init__(self):
        self.tracker = dlib.correlation_tracker()
        self._isWorking = False
        self.loseDistance = 50
        logger.info("追踪器初始化完毕,类型为:"+"DlibTracker")
    def startWorking(self,frame,box):
        if frame is None:
            self._isWorking = False
            return
        self.tracker.start_track(frame, dlib.rectangle(box[0],box[1],box[0]+box[2],box[1]+box[3]))
        self._isWorking = True
        logger.info("追踪器开始工作")
    def stopWorking(self):
        self._isWorking = False
        self.tracker = dlib.correlation_tracker()
        logger.info("追踪器结束工作")
    def isWorking(self):
        return self._isWorking
    def update(self,frame):
        if frame is None:
            return
        if not self.isWorking():
            logger.error("追踪器未初始化")
            raise Exception("追踪器未初始化")
        message = {}
        item = None
        self.tracker.update(frame)
        box_predict = self.tracker.get_position()
        screenSize = frame.shape
        rect = ((int(box_predict.left()),int(box_predict.top())),(int(box_predict.right()),int(box_predict.bottom())))
        center = IOUtil.countCenter(rect)
        cv2.rectangle(frame,rect[0],rect[1],(0,255,255),1)  # 用矩形框标注出来
        if(center[0] > self.loseDistance and center[1] > self.loseDistance and abs(center[0] - screenSize[1]) > self.loseDistance and abs(center[1] - screenSize[0]) > self.loseDistance):
            message['isGet'] = True
            message['center'] = center
            message["rect"] = rect
            message['time'] = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
        else:
            message['isGet'] = False
        return MessageItem(frame,message)
#追踪器测试函数
def testTracker(tracker):
    video = cv2.VideoCapture(0)
    cam = tracker
    ok,frame = video.read()
    bbox = cv2.selectROI(frame, False)
    cam.startWorking(frame,bbox);
    screenCenter = (int(video.get(cv2.CAP_PROP_FRAME_WIDTH)/2),int(video.get(cv2.CAP_PROP_FRAME_HEIGHT)/2))
    while True:
        _,frame = video.read();
        if(_):
            item = cam.update(frame);
            cv2.imshow("track",item.getFrame())
            if item.getMessage() and item.getMessage()['isGet']:
                print("get")
            else:
                print("loose");
            k = cv2.waitKey(1) & 0xff
            if k == 27:
                break
def testDog(dog):
    video = cv2.VideoCapture(0)
    for i in range(100):
        _,frame = video.read()
    cam = dog
    ok,frame = video.read()
    cam.startWorking(frame);
    screenCenter = (int(video.get(cv2.CAP_PROP_FRAME_WIDTH)/2),int(video.get(cv2.CAP_PROP_FRAME_HEIGHT)/2))
    while True:
        _,frame = video.read();
        if(_):
            item = cam.update(frame);
            cv2.imshow("track",item.getFrame())
            if item.getMessage() and item.getMessage()['isGet']:
                print("get")
            else:
                print("loose");
            k = cv2.waitKey(1) & 0xff
            if k == 27:
                break

if __name__ == '__main__' :
    '''
    tracker = CamShiftTracker()
    tracker = TemplateTracker()
    tracker = ContribTracker()
    '''
    tracker = WatchDog()
    testDog(tracker);