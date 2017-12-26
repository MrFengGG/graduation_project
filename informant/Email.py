import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

class EmailClient(object):
	def __init__(self,user="763484204@qq.com",license="edbecalqanpobefj"):
		self.user = user
		self.license = license
		self.server = smtplib.SMTP_SSL("smtp.qq.com",465)
		self.server.login(self.user,self.license)

	def sendEmail(self,targetEmail,subject,content.images=[]):
		letter = MIMEText(content)
		letter['Subject'] = subject
		letter['From'] = self.user
		letter['To'] = targetEmail
		self.server.sendmail(self.user,targetEmail,letter.as_string())

if __name__ == "__main__":
	client = EmailClient()
	client.sendEmail("763484204@qq.com","测试邮件","测试邮件发送")