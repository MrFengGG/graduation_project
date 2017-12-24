#encoding=utf-8
import cv2
from items import MessageItem
import numpy as np
class MoveAnalyzer(object):
    #运动检测分析器
    def __init__(self,frame=None):
        #运动检测器构造函数
        if frame:
            self._background = cv2.GaussianBlur(cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY),(21,21),0)
        self._background = None
        self.es = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10, 10))
    def isWorking(self):
        #运动检测器是否工作
        return self._background is not None
    def startWorking(self,frame):
        #运动检测器开始工作
        self._background = cv2.GaussianBlur(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), (21, 21), 0)
    def stopWorking(self):
        #运动检测器结束工作
        self._background = None
    def analyze(self,frame):
        #运动检测
        sample_frame = cv2.GaussianBlur(cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY),(21,21),0)
        diff = cv2.absdiff(self._background,sample_frame)
        diff = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]
        diff = cv2.dilate(diff, self.es, iterations=2)
        image, cnts, hierarchy = cv2.findContours(diff.copy(),cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        coordinate = []
        for c in cnts:
            if cv2.contourArea(c) < 1500:
                continue
            (x,y,w,h) = cv2.boundingRect(c)
            coordinate.append({"x":x,"y":y,"w":w,"h":h})
            cv2.rectangle(frame,(x,y),(x+w,y+h), (255, 255, 0), 2)
        return MessageItem(frame,coordinate)


