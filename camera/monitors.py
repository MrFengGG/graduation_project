#encoding=utf-8
import cv2
from items import MessageItem
import time
import numpy as np
'''
监视者模块,负责入侵检测,目标跟踪
'''
class WatchDog(object):
  #入侵检测者模块,用于入侵检测
    def __init__(self,frame=None):
        #运动检测器构造函数
        self._background = None
        if frame is not None:
            self._background = cv2.GaussianBlur(cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY),(21,21),0)
        self.es = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10, 10))
    def isWorking(self):
        #运动检测器是否工作
        return self._background is not None
    def startWorking(self,frame):
        #运动检测器开始工作
        if frame is not None:
            self._background = cv2.GaussianBlur(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), (21, 21), 0)
    def stopWorking(self):
        #运动检测器结束工作
        self._background = None
    def analyze(self,frame):
        #运动检测
        if frame is None or self._background is None:
            return
        sample_frame = cv2.GaussianBlur(cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY),(21,21),0)
        diff = cv2.absdiff(self._background,sample_frame)
        diff = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]
        diff = cv2.dilate(diff, self.es, iterations=2)
        image, cnts, hierarchy = cv2.findContours(diff.copy(),cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        coordinate = []
        bigC = None
        bigMulti = 0
        for c in cnts:
            if cv2.contourArea(c) < 1500:
                continue
            (x,y,w,h) = cv2.boundingRect(c)
            if w * h > bigMulti:
                bigMulti = w * h
                bigC = ((x,y),(x+w,y+h))
        if bigC:
            cv2.rectangle(frame, bigC[0],bigC[1], (255,0,0), 2, 1)
        coordinate.append(bigC)
        message = {"coord":coordinate}
        message['msg'] = None
        return MessageItem(frame,message)

class Tracker(object):
    '''
    追踪者模块,用于追踪指定目标
    '''
    def __init__(self,tracker_type = "BOOSTING",draw_coord = True):
        '''
        初始化追踪器种类
        '''
        #获得opencv版本
        (major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')
        self.tracker_types = ['BOOSTING', 'MIL','KCF', 'TLD', 'MEDIANFLOW', 'GOTURN']
        self.tracker_type = tracker_type
        self.isWorking = False
        self.draw_coord = draw_coord
        #构造追踪器
        if int(minor_ver) < 3:
            self.tracker = cv2.Tracker_create(tracker_type)
        else:
            if tracker_type == 'BOOSTING':
                self.tracker = cv2.TrackerBoosting_create()
            if tracker_type == 'MIL':
                self.tracker = cv2.TrackerMIL_create()
            if tracker_type == 'KCF':
                self.tracker = cv2.TrackerKCF_create()
            if tracker_type == 'TLD':
                self.tracker = cv2.TrackerTLD_create()
            if tracker_type == 'MEDIANFLOW':
                self.tracker = cv2.TrackerMedianFlow_create()
            if tracker_type == 'GOTURN':
                self.tracker = cv2.TrackerGOTURN_create()
    def initWorking(self,frame,box):
        '''
        追踪器工作初始化
        frame:初始化追踪画面
        box:追踪的区域
        '''
        if not self.tracker:
            raise Exception("追踪器未初始化")
        status = self.tracker.init(frame,box)
        if not status:
            raise Exception("追踪器工作初始化失败")
        self.coord = box
        self.isWorking = True

    def track(self,frame):
        '''
        开启追踪
        '''
        message = None
        if self.isWorking:
            status,self.coord = self.tracker.update(frame)
            if status:
                message = {"coord":[((int(self.coord[0]), int(self.coord[1])),(int(self.coord[0] + self.coord[2]), int(self.coord[1] + self.coord[3])))]}
                if self.draw_coord:
                    p1 = (int(self.coord[0]), int(self.coord[1]))
                    p2 = (int(self.coord[0] + self.coord[2]), int(self.coord[1] + self.coord[3]))
                    cv2.rectangle(frame, p1, p2, (255,0,0), 2, 1)
                    message['msg'] = "is tracking"
        return MessageItem(frame,message)

class ObjectTracker(object):
    def __init__(self,dataSet):
        self.cascade = cv2.CascadeClassifier(dataSet)
    def track(self,frame):
        gray = cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        faces = self.cascade.detectMultiScale(gray,1.03,5)
        for (x,y,w,h) in faces:
            cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
        return frame


if __name__ == '__main__' :
    '''
    a = ['BOOSTING', 'MIL','KCF', 'TLD', 'MEDIANFLOW', 'GOTURN']
    tracker = Tracker(tracker_type="KCF")
    video = cv2.VideoCapture(0)
    ok, frame = video.read()
    bbox = cv2.selectROI(frame, False)
    tracker.initWorking(frame,bbox)
    '''
    cap = cv2.VideoCapture(0)
    ret,frame = cap.read()
    '''
    r,h,c,w = 10,200,10,200
                track_window = (c,r,w,h)'''
    c,r,w,h = cv2.selectROI(frame, False)
    track_window = (c,r,w,h)
    roi = frame[c:c+w,r:r+h]

    hsv_roi = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_roi,np.array((100.,30.,32.)),
        np.array((180.,120.,255.)))

    roi_hist = cv2.calcHist([hsv_roi],[0],mask,[180],[0,180])
    cv2.normalize(roi_hist,roi_hist,0,255,cv2.NORM_MINMAX)
    term_crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT,10,1)
    while True:
        ret,frame = cap.read()
        if ret:
            hav = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
            dst = cv2.calcBackProject([hav],[0],roi_hist,[0,180],1)

            ret,track_window = cv2.meanShift(dst,track_window,term_crit)
            x,y,w,h = track_window
            img2 = cv2.rectangle(frame,(x,y),(x+w,y+h),255,2)
            cv2.imshow("img2",img2)
            k = cv2.waitKey(1) & 0xff
            if k == 27:
                break
    cv2.destroyAllWindows()
    cap.release()

