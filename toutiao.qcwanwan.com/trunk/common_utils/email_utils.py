# _*_ coding: utf-8 _*_
# @Time    : 2018/4/9 下午2:51
# @Author  : 杨楚杰
# @File    : data_email.py
# @license : Copyright(C), 安锋游戏
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class BIEmail(object):
    smtp_server = "hwsmtp.exmail.qq.com"
    smtp_server_port = 465
    from_email = "ycj@anfan.com"
    from_email_pwd = "43P7X26E7qy9PBtT"

    def __init__(self, subject, to_email, html_content):
        self.subject = subject
        self.to_email = to_email
        self.html_content = html_content

    def send_email(self):
        msg = MIMEMultipart('alternative')
        msg['Subject'] = self.subject
        msg['From'] = self.from_email
        msg['To'] = self.to_email

        part1 = MIMEText(self.html_content, 'html')
        msg.attach(part1)

        try:
            s = smtplib.SMTP_SSL(self.smtp_server)
            s.connect(self.smtp_server, self.smtp_server_port)
            s.login(self.from_email, self.from_email_pwd)
            s.sendmail(self.from_email, self.to_email, msg.as_string())
            s.quit()
        except Exception as e:
            print(repr(e))
