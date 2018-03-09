#encoding=utf-8
import socket
import cv2
import numpy
import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from io import BytesIO
from utils import IOUtil,logger
from PIL import Image
import time
'''
传递者模块,用于分发需要散布的信息
'''
class Dispatcher(object):
    #信息分发器,用于将信息分发到指定的ip和端口上
    def __init__(self):
        #初始化udp socket
        self._sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.fileName = 0
        logger.info("分发器初始化完毕")
    def dispenseImage(self,item,address):
        #分发图片到指定的地址
    	if item is None:
        	return
    	try:
    		self._sock.sendto(item.getBinaryFrame(),address)
    	except Exception as e:
    		logger.error("分发器错误:"+str(e))
    def dispenseCommand(self,command,address):
    	if command is None:
        	return
    	try:
    		self._sock.sendto(bytes(command),address)
    	except Exception as e:
    		raise Exception(e)
    def close(self):
    	self._sock.close()
class TcpDispatcher(object):
 	def __init__(self):
 		self.sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
 		self.isWorking = False
 	def initWorking(self,address = (TCP_IMAGE_IP,TCP_IMAGE_PORT)):
 		self.sock.connect(address)
 		self.isWorking = True
 		print("图片分发器初始化成功")
 	def dispatcher(self,item):
 		if not self.isWorking:
 			raise Exception("分发器未初始化,请使用initWorking()进行初始化")
 		self.sock.send(item.getBinaryFrame());
class EmailClient(object):
	'''
	邮箱分发者,发送邮件信息
	'''
	def __init__(self,user,license):
		self.user = user
		self.license = license
		try:
			self.server = smtplib.SMTP_SSL("smtp.qq.com",465)
			self.server.login(self.user,self.license)
		except Exception as e:
			logger.error("服务器初始化错误:"+str(e))
		logger.info("邮件分发器初始化完毕")
	def sendTextEmail(self,targetEmail,subject,content):
		'''
		发送普通文本信息
		'''
		letter = MIMEText(content)
		letter['Subject'] = subject
		letter['From'] = self.user
		letter['To'] = targetEmail
		try:
			self.server.sendmail(self.user,targetEmail,letter.as_string())
			logger.info("普通邮件发送成功")
		except Exception as e:
			logger.error("普通邮件发送失败:"+str(e))
	def sendHtml(self,targetEmail,subject,content,images=["cat.jpg"]):
		'''
		发送html格式邮件
		'''
		try:
			letter = MIMEMultipart()
			letter['Subject'] = Header(subject)
			letter['From'] = Header(self.user)
			letter['to'] = Header(targetEmail)
			letter.attach(MIMEText(content,'html','utf-8'))
			for image in images:
				with open(image,"rb") as fp:
					imageMsg = MIMEImage(fp.read())
					imageMsg.add_header('Content-ID','<'+image+'>')
					letter.attach(imageMsg)
			logger.info("构造一条HTML邮件")
		except Exception as e:
			logger.error("HTML邮件构造错误,错误信息为:"+str(e))
			return
		try:
			self.server.sendmail(self.user,targetEmail,letter.as_string())
			logger.info("邮件发送成功")
		except Exception as e:
			logger.error("邮件发送错误,错误信息为"+str(e))
	def close(self):
		self.server.close()

