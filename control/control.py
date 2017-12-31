#coding=UTF-8
import RPi.GPIO as GPIO
import time
import threading
import socket
import json
class Controller(object):
    def __init__(self,levelPin,virtPin,ip="",port=9997,isWarnings = False):
        '''
        外设控制类,用于接收来自远程端口的命令,默认端口为9997
        '''
        GPIO.setmode(GPIO.BCM)
        #设置水平舵机输出Pin
        self.levelPin = levelPin
        #设置竖直舵机输出Pin
        self.virtPin = virtPin
        self.shaft = {1:self.levelPin,2:self.virtPin}
        #设置输出端口
        GPIO.setup(self.levelPin,GPIO.OUT)
        GPIO.setup(self.virtPin,GPIO.OUT)
        #水平方向移动状态
        self.status = 0
        #当前角度
        self.nowAngle = {1:None,2:None}
        #初始化sock
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.sock.bind((ip,port))
        #默认移动速度为10
        self.speed = 10
        #标签
        self.label = {1:"水平方向",2:"竖直方向"}
        #设置转动角度
        self.maxLevel = 180
        self.minLevel = 0
        self.maxVirt = 180
        self.minVirt = 20
        #初始化错误打印类
        self.printer = MsgPrinter()
    def move(self,angle,shaft):
        #试图运动到一个角度
        plusewidth = (angle * 11) + 500
        GPIO.output(self.shaft[shaft],GPIO.HIGH)
        time.sleep(plusewidth/1000000.0)
        GPIO.output(self.shaft[shaft],GPIO.LOW)
        time.sleep(20.0/1000 - plusewidth/1000000.0)
    def move_to_angle(self,angle,shaft,speed):
        #移动到一个角度上
        self.printer.printMessage("当前%s角度为:%s,将会移动到%d度"%(self.label[shaft],str(self.nowAngle[shaft]),angle))
        self.status = True
        if not self.nowAngle[shaft]:
            self.nowAngle[shaft] = 0
        print("间隔为"+str(self.nowAngle[shaft] - angle))
        for i in range(abs(self.nowAngle[shaft]-angle)):
           self.move(angle,shaft)
           time.sleep(1/speed)
        self.nowAngle[1] = angle
        if shaft == 1:
            self.levelAngle = angle
        else:
            self.virtAngle = angle
        self.nowAngle[shaft] = angle
        self.status = False
    def moduleTwo(self,jsondata):
        print(jsondata)
        command = int(jsondata)
        if command == 0:
            self.move(0,1)
        if command == 1:
            self.move(180,1)
        if command == 2:
            self.move(0,2)
        if command == 3:
            self.move(180,2)
    def moduleOne(self,jsondata):
        print("module1")
        #模式1,使用陀螺
        try:
            levelAngle = int(jsondata['level']['angle'])
            levelSpeed = int(jsondata['level']['speed'])

            virtAngle = int(jsondata['virt']['angle'])
            virtSpeed = int(jsondata['virt']['speed'])

            if not self.status:
                if (levelAngle < self.maxLevel and levelAngle > self.minLevel) and levelAngle != self.nowAngle[1]:
                    level = threading.Thread(
                            target = self.move_to_angle,
                            args=(levelAngle,1,levelSpeed,)
                            )
                    level.start()
                else:
                    self.printer.printMessage("水平方向达到极值或当前已在目标位置"+str(self.nowAngle[1])+"度")
                if (virtAngle < self.maxVirt and virtAngle > self.minVirt) and virtAngle != self.nowAngle[2]:
                    virt = threading.Thread(
                            target = self.move_to_angle,
                            args=(virtAngle,2,virtSpeed,)
                            )
                    virt.start()
                else:
                    self.printer.printMessage("竖直方向达到极值或当前已在目标位置"+str(self.nowAngle[2])+"度")
        except Exception as e:
            self.printer.printMessage("错误:"+str(e))

    def run(self):
        while True:
            data,addr = self.sock.recvfrom(1024)
            jsondata = json.loads(data.decode())
            if int(jsondata['module']) == 1:
                #模式一
                self.moduleOne(jsondata['command'])
            if int(jsondata['module']) == 2:
                #模式二
                self.moduleTwo(jsondata['command'])

class MsgPrinter(object):
    '''
    用于发布错误信息
    '''
    def __init__(self):
        pass
    def printMessage(self,msg):
        print(msg)
if __name__ == "__main__":
    controller = Controller(18,24)
    controller.run()
