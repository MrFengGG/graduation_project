#encoding=utf-8
import cv2
import socket
import numpy
import base64
import json
from PIL import Image
from io import BytesIO
'''
address=('',9999)
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.bind(address)
while True:
    data,addr = sock.recvfrom(1024*1024)
    jsondata = json.loads(data.decode())
    data = base64.b64decode(jsondata['frame'])
    buf = BytesIO(data)
    image = numpy.array(Image.open(buf))
    cv2.imshow("haha", image)
    key = cv2.waitKey(1)
    if key == 27:
        cv2.destroyWindow("haha")
        break
        '''
sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
sock.sendto('{"command":"analyze"}'.encode(),("127.0.0.1",9998))

