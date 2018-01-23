
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

def sendAlertEmail(iAlertText: str, iModuleDescr: str):
    # Create the root message and fill in the from, to, and subject headers
    msgRoot = MIMEMultipart('related')
    msgRoot['Subject'] = 'AOM - Rangehood alert for module ' + iModuleDescr
    msgRoot['From'] = strfrom
    msgRoot['To'] = strto
    msgRoot.preamble = 'This is a multi-part message in MIME format.'

    header = 'From: ' + strfrom + '\n' + 'To: ' + strto + '\n' + msgRoot['Subject']

    msgAlternative = MIMEMultipart('alternative')
    msgRoot.attach(msgAlternative)

    dtnow = datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S")
    msgText = MIMEText(iAlertText)
    msgAlternative.attach(msgText)

    # We reference the image in the IMG SRC attribute by the ID we give it below
    msgText = MIMEText(iAlertText + ' <br><img src="cid:image1">', 'html')
    msgAlternative.attach(msgText)

    # Send the email (this example assumes SMTP authentication is required)
    smtp = smtplib.SMTP(smtpserver, smtpport)

    smtp.ehlo()
    smtp.starttls()
    smtp.ehlo()

    smtp.login(smtpuser,smtppass)
    smtp.sendmail(strfrom, strto.split(','), msgRoot.as_string())
    smtp.quit()
   
    print ('Alert has been sent successfully!')

    return header;
