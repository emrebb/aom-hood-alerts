# Send an HTML email with an embedded image and a plain text message for
# email clients that don't want to display the HTML.

import datetime
import time
import smtplib
##import urllib2
import RPi.GPIO as gpio
import configparser

cfg = configparser.RawConfigParser()
cfg.read('ClientParameters.cfg')       # Read file

#print cfg.getboolean('Settings','bla') # Manual Way to acess them

par=dict(cfg.items("Settings"))
for p in par:
    par[p]=par[p].split("#",1)[0].strip() # To get rid of inline comments

globals().update(par)  #Make them availible globally


##AOM connector port
gpioPort  = 16
gpioPort  = int(gpioport)
gpio.setmode(gpio.BCM)
gpio.setup(gpioPort, gpio.IN, pull_up_down = gpio.PUD_UP)


from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

dtnow = datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S")
print ('AOM Rangehood alerts application now loaded '  + dtnow )


##smtpServer = 'smtp.gmail.com'
##smtpPort = '587'
##
##smtpUser = 'francoisbolomey08@gmail.com'
##smtpPass = 'fifi9876'
##
##strFrom = 'francoisbolomey08@gmail.com'
##strTo = 'emrebo@gmail.com'


# Create the root message and fill in the from, to, and subject headers
msgRoot = MIMEMultipart('related')
msgRoot['Subject'] = 'AOM - Rangehood alert'
msgRoot['From'] = strfrom
msgRoot['To'] = strto
msgRoot.preamble = 'This is a multi-part message in MIME format.'

header = 'From: ' + strfrom + '\n' + 'To: ' + strto + '\n' + 'Subject: AOM - Rangehood alert' 


while True:
    input_value = gpio.input(gpioPort)
    if input_value == False:

        print("\033c")
        dtnow = datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S")
        print ("Alert has been triggered @ " + dtnow )

                # Encapsulate the plain and HTML versions of the message body in an
                # 'alternative' part, so message agents can decide which they want to display.
        msgAlternative = MIMEMultipart('alternative')
        msgRoot.attach(msgAlternative)

        dtnow = datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S")
        msgText = MIMEText('Error signal received @ ' + dtnow)
        msgAlternative.attach(msgText)

        # We reference the image in the IMG SRC attribute by the ID we give it below
        msgText = MIMEText('Error signal received @ ' + dtnow + ' <br><img src="cid:image1">', 'html')
        msgAlternative.attach(msgText)


        # Get ReoLink Image
##                request = urllib2.Request(
##                        r'http://192.168.0.11/cgi-bin/api.cgi?cmd=Snap&channel=0&rs=wuuPhkmUCeI9WG7C&user=admin&password=12345',
##                        headers={'User-Agent':'Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 firefox/2.0.0.11'})
##                page = urllib2.urlopen(request)
##                with open('doorbell.png','wb') as f:
##                        f.write(page.read())
##
##                # This example assumes the image is in the current directory
##                fp = open('doorbell.png', 'rb')
##                msgImage = MIMEImage(fp.read())
##                fp.close()

                # Define the image's ID as referenced above
##                msgImage.add_header('Content-ID', '<image1>')
##                msgRoot.attach(msgImage)

                # Send the email (this example assumes SMTP authentication is required)
        smtp = smtplib.SMTP(smtpserver, smtpport)

        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()

        smtp.login(smtpuser,smtppass)
        smtp.sendmail(strfrom, strto.split(','), msgRoot.as_string())
        time.sleep(15)
        smtp.quit()

        print ('Email sent successful!')
        print (header + '\n' + 'Message: Alert triggered @ ' + dtnow )

while input_value == False:
            input_value = gpio.input(gpioPort)
            
