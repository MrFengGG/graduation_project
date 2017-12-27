#encoding=utf-8
import smtplib
from email.header import Header
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

class EmailClient(object):
	'''
	邮箱客户端
	'''
	def __init__(self,user="763484204@qq.com",license="edbecalqanpobefj"):
		self.user = user
		self.license = license
		try:
			self.server = smtplib.SMTP_SSL("smtp.qq.com",465)
			self.server.login(self.user,self.license)
		except Exception as e:
			print("服务器初始化错误,错误信息为:"+str(e))

	def sendTextEmail(self,targetEmail,subject,content):
		'''
		发送普通文本信息
		'''
		letter = MIMEText(content)
		letter['Subject'] = subject
		letter['From'] = self.user
		letter['To'] = targetEmail
		self.server.sendmail(self.user,targetEmail,letter.as_string())

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
		except Exception as e:
			print("邮件构造错误,错误信息为:"+str(e))
			return
		try:
			self.server.sendmail(self.user,targetEmail,letter.as_string())
			print("邮件发送成功")
		except Exception as e:
			print("邮件发送错误,错误信息为"+str(e))


if __name__ == "__main__":
	client = EmailClient()
	client.sendHtml("763484204@qq.com","测试邮件","<p>测试图片邮件发送</p><p>图片演示</p><p><image src='cid:cat.jpg'</p>")