import cv2
import sys
sys.path.append("../imagecollection")
from items import MessageItem


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
                message = {"coord":self.coord}
                if self.draw_coord:
                    p1 = (int(self.coord[0]), int(self.coord[1]))
                    p2 = (int(self.coord[0] + self.coord[2]), int(self.coord[1] + self.coord[3]))
                    cv2.rectangle(frame, p1, p2, (255,0,0), 10)
                    cv2.putText(frame, self.tracker_type + " is tracking", (100,20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50),2);
            else:
                cv2.putText(frame, tracker_type + " lose the target", (100,20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50,170,50),2);
        return MessageItem(frame,message)

if __name__ == '__main__' :
    tracker = Tracker(tracker_type="MIL")
    video = cv2.VideoCapture(0)
    ok, frame = video.read()
    bbox = cv2.selectROI(frame, False)
    tracker.initWorking(frame,bbox)
    while True:
        # Read a new frame
        ok, frame = video.read()
        if not ok:
            break
        message = tracker.track(frame)
        cv2.imshow("追踪测试",message.getFrame())
        k = cv2.waitKey(1) & 0xff
        if k == 27 : break