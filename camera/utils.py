#encoding=utf-8
import time
import numpy
import base64
from PIL import Image
from io import BytesIO
'''
常用工具类
'''
class IOUtil(object):
    #流操作工具类
    @staticmethod
    def array_to_bytes(pic,formatter="jpeg"):
        '''
        静态方法,将numpy数组转化二进制流
        :param pic: numpy数组
        :param format: 图片格式
        :return: 
        '''
        stream = BytesIO()
        picture = Image.fromarray(pic)
        picture.save(stream,format=formatter)
        jepg = stream.getvalue()
        print("压缩后图片长度为"+str(len(jepg)))
        stream.close()
        return jepg
    @staticmethod
    def bytes_to_base64(byte):
        '''
        静态方法,bytes转base64编码
        :param byte: 
        :return: 
        '''
        return base64.b64encode(byte)
    @staticmethod
    def transport_rgb(frame):
        '''
        将bgr图像转化为rgb图像,或者将rgb图像转化为bgr图像
        '''
        return frame[...,::-1]
