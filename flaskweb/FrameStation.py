#encoding=utf-8

import socket
import threading
import json
import base64
from io import BytesIO

class FrameStation(object):
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.frame = None
        self.initWorking()
        self._task = threading.Thread(target=self.working)
        self._task.start()
    def initWorking(self,port=9999,ip=""):
        self.sock.bind((ip,port))
    def working(self):
        while True:
            data, addr = self.sock.recvfrom(1024 * 1024)
            jsondata = json.loads(data.decode())
            data = base64.b64decode(jsondata['frame'])
            buf = BytesIO(data)
            self.frame = buf
    def getFrame(self):
        return self.frame
