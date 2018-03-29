
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import datetime
class emailinfo():    
    strfrom='test'
    strto='test'
    smtpserver=''
    smtpport=''
    smtpuser=''
    smtppass=''


def initialize(ifrom, ito, iserver, iport,user,passw):
	emailinfo.strfrom=ifrom
	emailinfo.strto=ito
	emailinfo.smtpserver=iserver
	emailinfo.smtpport=iport
	emailinfo.smtpuser=user
	emailinfo.smtppass=passw
	return
def sendAlertEmail(iAlertText: str, iModuleDescr: str):
    # Create the root message and fill in the from, to, and subject headers
    msgRoot = MIMEMultipart('related')
    msgRoot['Subject'] = 'AOM - Rangehood alert for module ' + iModuleDescr
    msgRoot['From'] = emailinfo.strfrom
    msgRoot['To'] = emailinfo.strto
    msgRoot.preamble = 'This is a multi-part message in MIME format.'

    header = 'From: ' + emailinfo.strfrom + '\n' + 'To: ' + emailinfo.strto + '\n' + msgRoot['Subject']

    msgAlternative = MIMEMultipart('alternative')
    msgRoot.attach(msgAlternative)

    dtnow = datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S")
    msgText = MIMEText(iAlertText)
    msgAlternative.attach(msgText)

    # We reference the image in the IMG SRC attribute by the ID we give it below
    msgText = MIMEText(iAlertText + ' <br><img src="cid:image1">', 'html')
    msgAlternative.attach(msgText)

    # Send the email (this example assumes SMTP authentication is required)
    smtp = smtplib.SMTP(emailinfo.smtpserver, emailinfo.smtpport)
    ##smtp.starttls()
    
    ##smtp.connect()
    #smtp.ehlo()
    smtp.starttls()
    #smtp.ehlo()

    smtp.login(emailinfo.smtpuser,emailinfo.smtppass)
    smtp.sendmail(emailinfo.strfrom, emailinfo.strto.split(','), msgRoot.as_string())
    smtp.quit()
   
    print ('Alert has been sent successfully!')

    return header;
