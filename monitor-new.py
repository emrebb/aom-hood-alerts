# Send an HTML email with an embedded image and a plain text message for
# email clients that don't want to display the HTML.
# define global constants

import datetime
import time
import smtplib
##import urllib2
import logging
log_format = '%(Levelname)s | %(acstime)-15s |%(message)s'
logging.basicConfig(format=log_format, level=logging.DEBUG)
import RPi.GPIO as gpio
import configparser

##import gettext
##import os
##
###innitialize the text internationalization module
##localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locale')
##translate = gettext.translation(this.name,localedir, fallback=true)
##_ = translate.gettext #This is the translator module
POWER_SWITCH = 'Power Switch'
POWER_ON = 'Power On'
POWER_OFF = 'Power Off'
FAULT_A = 'Fault module A'
FAULT_B = 'Fault module B'

cfg = configparser.RawConfigParser()
cfg.read('ClientParameters.cfg')       # Read file


#print cfg.getboolean('Settings','bla') # Manual Way to acess them

par=dict(cfg.items("Settings"))
for p in par:
    par[p]=par[p].split("#",1)[0].strip() # To get rid of inline comments
    
globals().update(par)  #Make them availible globally

class AOMModule:
    def __init__ (self, id: int, description: str, gpioPowerUp: int, gpioFaultA: int, gpioFaultB: int):
        self.id = id
        self.description = description
        self.gpioPowerUp = gpioPowerUp
        self.gpioPowerUpDescr = self.description + ' ' + POWER_ON
        self.gpioPowerOffDescr = self.description + ' ' + POWER_OFF
        self.gpioPowerAlertStatus  = 0
        self.gpioPowerStatus  = 0 ##will be read from gpio after setup
        self.gpioFaultA = gpioFaultA
        self.gpioFaultADescr = FAULT_A
        self.gpioFaultB = gpioFaultB
        self.gpioFaultBDescr = FAULT_B
        self.status = {status: 'initialized', date: dateNow(), module: self.description, gpio: ''}
        self.statusLog = []
        
        initializeGPIO( )
        
    def getGpioDesc(gpioId):
        return { FAULT_A : self.gpioFaultA,
                 FAULT_B : self.gpioFaultB,
                 POWER_UP: self.gpioPowerUp }[gpioId].get(gpioId, 'No GPIO')
        
    def newStatus(statusText, gpioId):      
        self.status = {status: statusText, date: dateNow(), module: self.description, gpio: getGpioDesc(gpioId)}
        self.statusLog.append(self.status)
        
    def initializeGPIO( ):
        msgText = 'Initializing error monitor for module ' + self.description 
        print(msgText)
        
        gpio.setup(self.gpioPowerUp, gpio.IN, pull_up_down = gpio.PUD_OFF)
        gpio.setup(self.gpioFaultA, gpio.IN, pull_up_down = gpio.PUD_UP)
        gpio.setup(self.gpioFaultB, gpio.IN, pull_up_down = gpio.PUD_UP)
                
        self.gpioPowerStatus = gpio.input(self.gpioPowerUp)
        gpio.add_interrupt_callback(self.gpioPowerUp, self.gpioCallback, threaded_callback=True, debounce_timeout_ms=100)
        
        self.status = 'initialized'
        if self.gpioPowerStatus == self.gpioPowerAlertStatus:
            setPowerOn( )
        else:
            setPowerOff( )
            
    def setPowerOff( ):
        gpio.del_interrupt_calback(self.gpioFaultA)
        gpio.del_interrupt_calback(self.gpioFaultB)
        msgText = 'Power is OFF for module ' + self.description + '. Switching OFF the error monitor'
        print(msgText)
        sendAlertEmail(msgText, self)
        
    def setPowerOn( ):
        gpio.add_interrupt_callback(self.gpioFaultA, self.gpioCallback, threaded_callback=True, debounce_timeout_ms=100)
        gpio.add_interrupt_callback(self.gpioFaultB, self.gpioCallback, threaded_callback=True, debounce_timeout_ms=100)
        msgText = 'Power is ON for module ' + self.description + '. Error monitor is now ON'
        print(msgText)
        sendAlertEmail(msgText, self)
    
    def setErrorStatusA( ):
        msgText = 'Module ' + self.description + ' needs attention due to error type A. /n' + ''
        print(msgText)
        sendAlertEmail(msgText, self)
        
        
    def gpioCallback(gpioId, value):
        if gpioId == self.gpioPowerUp:
            self.gpioPowerStatus = value
            if self.gpioPowerStatus == self.gpioPowerAlertStatus:
                setPowerOn( )
            else:
                setPowerOff( )
        
        else:
            if gpioId == self.gpioFaultA:
                print('Error')
            else:
                ## self.gpioFaultB
                print('Error')
            
        return;
    
        
##AOM connector port
gpioPort  = 16
gpioPort  = int(gpioport)
gpio.setmode(gpio.BCM)
##gpio.setup(gpioPort, gpio.IN, pull_up_down = gpio.PUD_UP)


from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

def dateNow( ): 
    return datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S");

dtnow = dateNow()
print ('AOM Rangehood alerts application now loaded '  + dtnow )

def sendAlertEmail(iAlertText: str, oModule: AOMModule):
    # Create the root message and fill in the from, to, and subject headers
    msgRoot = MIMEMultipart('related')
    msgRoot['Subject'] = 'AOM - Rangehood alert for module ' + oModule.description
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
    
while True:
    input_value = gpio.input(gpioPort)
    if input_value == False:

        print("\033c")
        dtnow = datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S")
        print ("Alert has been triggered @ " + dtnow )

                # Encapsulate the plain and HTML versions of the message body in an
                # 'alternative' part, so message agents can decide which they want to display.
        header = sendAlertEmail('Alert has been triggered')
        
        time.sleep(15)
        print (header + '\n' + 'Message: Alert triggered @ ' + dtnow )

while input_value == False:
            input_value = gpio.input(gpioPort)
            
