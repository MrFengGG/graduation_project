#encoding=utf-8
import socket
import cv2
import numpy
from io import BytesIO
from utils import IOUtil
from PIL import Image
class Dispatcher(object):
    #分发器
    def __init__(self):
        #初始化udp socket
        self._sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.fileName = 0
    def dispense(self,item,address = ("127.0.0.1",9999)):
        #分发到指定的地址
        self._sock.sendto(item.getJson().encode(),address)