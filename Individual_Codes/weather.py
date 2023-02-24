#DVA project
#Requirement: Shelter & Weather Conditions

import RPi.GPIO as GPIO                             #import Raspberry Pi GPIO module
import time                                         #import time
GPIO.setwarnings(False)                             #Disable warnings
GPIO.setmode(GPIO.BCM)                              #set Broadcom SOC Channel

TempSensor = 16                                     #insert TempSensor at GPIO 16
HotWeather = 17                                     #insert LED(red clr) alert for HotWeather at GPIO 17
BackToNormal = 22                                   #insert LED(yellow clr) alert for BackRToNormal at GPIO 22

GPIO.setup(TempSensor, GPIO.IN)                     #set TempSensor as input
GPIO.setup(HotWeather, GPIO.OUT)                    #set HotWeather as output
GPIO.setup(BackToNormal, GPIO.OUT)                  #set BackToNormal as output

def HotWeather():                                   #define HotWeather condition as...
    GPIO.output(HotWeather, True)                   #Red Led On
    GPIO.output(BackToNormal, False)                #Yellow Led Off

def NormalWeather():                                #define NormalWeather condition as...
    GPIO.output(HotWeather, False)                  #Red Led Off
    GPIO.output(BackToNormal, True)                 #Yellow Led On

def All_off():                                      #define All_off condition as...
    GPIO.output(HotWeather, False)                  #Red Led Off      
    GPIO.output(BackToNormal, False)                #Yellow Led Off

WeatherState = 0                                    #WeatherState is originally 0

while True:
    tempstate = GPIO.input(TempSensor)              #define input value of TempSensor as tempstate 

    #Temperatue sensor detecting HOT weather
    if WeatherState == 0 and tempstate == False:   #if temperature sense HOT,
        HotWeather()                               #Led for "Hot Weather" turns ON
        time.sleep(5)                              #Led remains ON for 5 seconds
        All_off()                                  #All Leds will turn OFF
        WeatherState == 1                          #WeatherState will become 1, once HOT temperature is detected and LED has given alert 

    elif WeatherState == 1 and tempstate == False: #if temperature sense hot *again*
        All_off()                                  #nothing will happen, Leds will remain OFF
        WeatherState = 1                           #WeatherState remains 1
        

    
    #Temperatue sensor detecting NORMAL weather
    elif WeatherState == 1 and tempstate == True:  #if temperature sense normal *after sensing HOT*
        NormalWeather()                            #Led for "Back to Normal Weather" turns ON               
        time.sleep(5)                              #Led remains ON for 5 seconds
        All_off()                                  #All Leds will turn OFF
        WeatherState = 0                           #WeatherState will be back to 0, once Normal temperature is detected after a Hot weather.                                                            
        

    elif WeatherState == 0 and tempstate == True:  #if temperature sense NORMAL *again* or is *orginally* NORMAL           
        All_off()                                  #nothing happens, Leds remain OFF
        WeatherState = 0                           #WeatherState remains 0

        ##Goes as a loop
