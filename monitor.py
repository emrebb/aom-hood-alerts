# Send an HTML email with an embedded image and a plain text message for
# email clients that don't want to display the HTML.
# define global constants

import datetime
import time
import configparser
##import urllib2
import logging
import ast
import threading #import this library so that modules can run in parallel
import gpiozero #as gpio
import os
##import signal
from gpiozero import Button
from signal import pause
from threading import Thread
from time import sleep
from os import linesep as LS
log_format = '%(Levelname)s | %(acstime)-15s |%(message)s'
logging.basicConfig(format=log_format, level=logging.DEBUG)
##import json

cfg = configparser.RawConfigParser()
cfg.read('ClientParameters-new.cfg')       # Read file

try:
    par=dict(cfg.items("Settings"))
except configparser.NoSectionError:
    pass
finally:        
    for p in par:
        par[p]=par[p].split("#",1)[0].strip() # To get rid of inline comments
    globals().update(par)  #Make them availible globally
 
moduleList = []
i=0

try:
    parModules=dict(cfg.items("Modules"))
except configparser.NoSectionError:
    print('Please define the Modules in the configuration file')
finally:
    for name in parModules:
        parModules[name]=parModules[name].split("#",1)[0].strip() # To get rid of inline comments
        moduleList.append(ast.literal_eval(parModules[name]))
##import RPi.GPIO as gpio

import emails 

def dateNow(): 
    return datetime.datetime.now().strftime("%m-%d-%Y %H:%M:%S");
    
emails.initialize(strfrom, strto, smtpserver, smtpport, smtpuser,smtppass)

##localData = threading.local
##localData.Modules = dict()

class AOMModule(Thread):
    POWER_SWITCH = 'Power Switch'
    POWER_ON = 'Power On'
    POWER_UP = 'Power Up'
    POWER_OFF = 'Power Off'
    FAULT_A = 'Fault module A'
    FAULT_B = 'Fault module B'
    
    @staticmethod
    def getInstance(id: int, descr: str, gpioPowerUp: int, gpioFaultA: int, gpioFaultB: int):
        try:
            return AOMModule(id,descr,gpioPowerUp,gpioFaultA,gpioFaultB) 
        except AssertionError as error:            
            print('Cannot initialize alert monitor for ' + descr ) 
##            raise CANNOT_INITIALIZE         
      
    def __init__ (self, id: int, descr: str, gpioPowerUp: int, gpioFaultA: int, gpioFaultB: int):
        Thread.__init__(self)
        self.id = id
        self.descr = descr
        self.gpioPowerUp = gpioPowerUp
        self.gpioPowerUpDescr = self.descr + ' ' + AOMModule.POWER_ON
        self.gpioPowerOffDescr = self.descr + ' ' + AOMModule.POWER_OFF
        self.gpioPowerAlertStatus  = False
        self.gpioPowerStatutims  = 0 ##will be read from gpio after setup
        self.gpioFaultA = gpioFaultA
        self.gpioFaultADescr = AOMModule.FAULT_A        
        self.gpioFaultB = gpioFaultB
        self.gpioFaultBDescr = AOMModule.FAULT_B
        self.initialized = dateNow()
        self.status = {} ## {status: 'initialized', date: dateNow(), module: self.descr, gpio: ''}
        self.statusLog = []
        self.deamon = True
        self.swPowerUp = Button(self.gpioPowerUp)
        self.swFaultA = Button(self.gpioFaultA)
        self.swFaultB = Button(self.gpioFaultB)
        self.start()
		
        # def startModule(self):
    #     self.__initializeGPIO()
    def run(self):
        self.__initializeGPIO()
        
    def getGpioDesc(self,gpioId):   
        ports = { self.gpioFaultA :  AOMModule.FAULT_A ,
                  self.gpioFaultB :  AOMModule.FAULT_B ,
                  self.gpioPowerUp : AOMModule.POWER_UP }
        return ports.get(gpioId, 'No GPIO')
                    
    def __newStatus(self,statusText, gpioId):      
        self.status = {'status': statusText, 'date': dateNow(), 'module': self.descr, 'gpio': gpioId, 'moduleinfo': self.getGpioDesc(gpioId)}
        self.statusLog.append(self.status)
    def __initializeGPIO(self):
        msgText = 'Initializing error monitor for module ' + self.descr 
        print(msgText)

        ##self.gpioPowerStatus = gpio.input(self.gpioPowerUp)
        self.gpioPowerStatus = self.swPowerUp.value
        ##gpio.add_interrupt_callback(self.gpioPowerUp, self.gpioCallback, threaded_callback=True, debounce_timeout_ms=100)
        if self.gpioPowerStatus == False:
            isOnText = 'On'
        else:
            isOnText = 'Off'
        print('Module power status: ' + isOnText )
        self.__newStatus('initialized', self.gpioPowerUp)
        if self.gpioPowerStatus == self.gpioPowerAlertStatus:
            self.__setPowerOn()
        else:
            self.__setPowerOff()
        self.swPowerUp.when_activated = self.gpioCallback
        self.swPowerUp.when_deactivated = self.gpioCallback

        return
    def __setPowerOff(self):
        self.swFaultA.when_activated=None
        self.swFaultB.when_activated=None
        # gpio.del_interrupt_calback(self.gpioFaultA)
        # gpio.del_interrupt_calback(self.gpioFaultB)
        msgText = self.descr +' is not connected or its power is OFF.'+ LS +' Switching OFF the error monitor for ' + self.descr + LS +'    at ports:' + LS +self.getGpioDesc(self.id)
        print(msgText)
        emails.sendAlertEmail(msgText, self.descr)
        
    def __setPowerOn(self):
        self.swFaultA.when_activated=self.gpioCallback # self.__setErrorStatusA
        self.swFaultB.when_activated=self.gpioCallback # self.__setErrorStatusB        
        # gpio.add_interrupt_callback(self.gpioFaultA, self.gpioCallback, threaded_callback=True, debounce_timeout_ms=100)
        # gpio.add_interrupt_callback(self.gpioFaultB, self.gpioCallback, threaded_callback=True, debounce_timeout_ms=100)
        msgText = 'Power is ON for module ' + self.descr + '. Error monitor is now ON'
        print(msgText)
        emails.sendAlertEmail(msgText, self.descr)
    
    def __setErrorStatusA(self):
        msgText = 'Module ' + self.descr + ' needs attention due to error type A. \n' + ''
        print(msgText)
        emails.sendAlertEmail(msgText, self.descr)

            
    def gpioCallback(self,iSwitch:Button):
    # def __gpioCallback(self,gpioId, value):
        if iSwitch.pin == self.gpioPowerUp:
            self.gpioPowerStatus = iSwitch.value
            if self.gpioPowerStatus != self.gpioPowerAlertStatus:
                self.__setPowerOn( )
            else:
                self.__setPowerOff( )
        else:
            if iSwitch.pin == self.gpioFaultA:
                if iSwitch.value == 1:
                    print('Error Fault A: ' + self.getGpioDesc(iSwitch.pin))
            else:
                ## self.gpioFaultB
                if iSwitch.value == 1:
                    print('Error Fault B: ' + self.getGpioDesc(iSwitch.pin))
            
        return;
    
# md=moduleList[0]

''' def initializeModule(m):
    oModule=AOMModule.getInstance(m['id'], m['description'], m['gpioPowerUp'], m['gpioFaultA'], m['gpioFaultB'])    
    oModule.start() '''

for md in moduleList:
    oModule=AOMModule.getInstance(md['id'], md['description'], md['gpioPowerUp'], md['gpioFaultA'], md['gpioFaultB'])    
    # oModule.start()
    # threading._start_new_thread = initializeModule(md)
    # threading._start_new_thread = initializeModule(md)

##AOM connector port
# gpioPort  = 16
# gpioPort  = int(gpioport)

##gpio.setup(gpioPort, gpio.IN, pull_up_down = gpio.PUD_UP)

# dtnow = dateNow()
print ('AOM Rangehood alerts application now loaded '  + dateNow() )


    
''' while True:
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
            
 '''
