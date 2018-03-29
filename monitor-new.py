# Send an HTML email with an embedded image and a plain text message for
# email clients that don't want to display the HTML.
# define global constants

import datetime
import time

##import urllib2
import logging
log_format = '%(Levelname)s | %(acstime)-15s |%(message)s'
logging.basicConfig(format=log_format, level=logging.DEBUG)
import configparser
import json
import ast

##import gettext
##import os
##
###innitialize the text internationalization module
##localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'locale')
##translate = gettext.translation(this.name,localedir, fallback=true)
##_ = translate.gettext #This is the translator module

cfg = configparser.RawConfigParser()
cfg.read('ClientParameters-new.cfg')       # Read file

#print cfg.getboolean('Settings','bla') # Manual Way to acess them

par=dict(cfg.items("Settings"))
for p in par:
    par[p]=par[p].split("#",1)[0].strip() # To get rid of inline comments
    
globals().update(par)  #Make them availible globally
 
moduleList = []
i=0
parModules=dict(cfg.items("Modules"))
for name in parModules:
    parModules[name]=parModules[name].split("#",1)[0].strip() # To get rid of inline comments
    moduleList.append(ast.literal_eval(parModules[name]))
##import RPi.GPIO as gpio

import emails as emails

def dateNow(): 
    return datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S");

''' def sendAlertEmail(iAlertText: str, iModuleDescr: str):
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

    return header; '''


import threading #import this library so that modules can run in parallel

##localData = threading.local
##localData.Modules = dict()

class AOMModule:
    POWER_SWITCH = 'Power Switch'
    POWER_ON = 'Power On'
    POWER_OFF = 'Power Off'
    FAULT_A = 'Fault module A'
    FAULT_B = 'Fault module B'
    
    @staticmethod
    def getInstance(id: int, descr: str, gpioPowerUp: int, gpioFaultA: int, gpioFaultB: int):
        try:
            return AOMModule(id,descr,gpioPowerUp,gpioFaultA,gpioFaultB) 
        except expression as identifier:            
            print('Cannot initialize alert monitor for', args) 
            raise CANNOT_INITIALIZE         
      
    def __init__ (self, id: int, descr: str, gpioPowerUp: int, gpioFaultA: int, gpioFaultB: int):
        self.id = id
        self.descr = descr
        self.gpioPowerUp = gpioPowerUp
        self.gpioPowerUpDescr = self.descr + ' ' + AOMModule.POWER_ON
        self.gpioPowerOffDescr = self.descr + ' ' + AOMModule.POWER_OFF
        self.gpioPowerAlertStatus  = 0
        self.gpioPowerStatutims  = 0 ##will be read from gpio after setup
        self.gpioFaultA = gpioFaultA
        self.gpioFaultADescr = AOMModule.FAULT_A        
        self.gpioFaultB = gpioFaultB
        self.gpioFaultBDescr = AOMModule.FAULT_B
        self.initialized = dateNow()
        self.status = {} ## {status: 'initialized', date: dateNow(), module: self.descr, gpio: ''}
        self.statusLog = []

    def start(self):
        self.__initializeGPIO()
    def getGpioDesc(self,gpioId):
        return { FAULT_A : self.gpioFaultA,
                 FAULT_B : self.gpioFaultB,
                 POWER_UP: self.gpioPowerUp }[gpioId].get(gpioId, 'No GPIO')                
    def __newStatus(self,statusText, gpioId):      
        self.status = {status: statusText, date: dateNow(), module: self.descr, gpio: getGpioDesc(gpioId)}
        self.statusLog.append(self.status)
        
    def __initializeGPIO(self):
        msgText = 'Initializing error monitor for module ' + self.descr 
        print(msgText)

        import RPi.GPIO as gpio
        gpio.setmode(gpio.BCM)
        gpio.setup(self.gpioPowerUp, gpio.IN, pull_up_down = gpio.PUD_OFF)
        gpio.setup(self.gpioFaultA, gpio.IN, pull_up_down = gpio.PUD_UP)
        gpio.setup(self.gpioFaultB, gpio.IN, pull_up_down = gpio.PUD_UP)
                
        self.gpioPowerStatus = gpio.input(self.gpioPowerUp)
        gpio.add_interrupt_callback(self.gpioPowerUp, self.gpioCallback, threaded_callback=True, debounce_timeout_ms=100)
        
        self.__newStatus('initialized', self.gpioPowerUp)
        if self.gpioPowerStatus == self.gpioPowerAlertStatus:
            __setPowerOn()
        else:
            __setPowerOff()
        return
    def __setPowerOff(self):
        gpio.del_interrupt_calback(self.gpioFaultA)
        gpio.del_interrupt_calback(self.gpioFaultB)
        msgText = 'Power is OFF for module ' + self.descr + '. Switching OFF the error monitor'
        print(msgText)
        sendAlertEmail(msgText, self)
        
    def __setPowerOn(self):
        gpio.add_interrupt_callback(self.gpioFaultA, self.gpioCallback, threaded_callback=True, debounce_timeout_ms=100)
        gpio.add_interrupt_callback(self.gpioFaultB, self.gpioCallback, threaded_callback=True, debounce_timeout_ms=100)
        msgText = 'Power is ON for module ' + self.descr + '. Error monitor is now ON'
        print(msgText)
        sendAlertEmail(msgText, self)
    
    def __setErrorStatusA(self):
        msgText = 'Module ' + self.descr + ' needs attention due to error type A. \n' + ''
        print(msgText)
        sendAlertEmail(msgText, self)

            
    def __gpioCallback(self,gpioId, value):
        if gpioId == self.gpioPowerUp:
            self.gpioPowerStatus = value
            if self.gpioPowerStatus == self.gpioPowerAlertStatus:
                __setPowerOn( )
            else:
                __setPowerOff( )
        else:
            if gpioId == self.gpioFaultA:
                print('Error')
            else:
                ## self.gpioFaultB
                print('Error')
            
        return;
    
md=moduleList[0]
#for m in moduleList:
oModule=AOMModule.getInstance(md['id'], md['description'], md['gpioPowerUp'], md['gpioFaultA'], md['gpioFaultB'])    
oModule.start()

##AOM connector port
gpioPort  = 16
gpioPort  = int(gpioport)
gpio.setmode(gpio.BCM)
##gpio.setup(gpioPort, gpio.IN, pull_up_down = gpio.PUD_UP)




dtnow = dateNow()
print ('AOM Rangehood alerts application now loaded '  + dtnow )


    
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
            
