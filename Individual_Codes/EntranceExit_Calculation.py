#DVA Project
#Requirement: Car Update to LED Bar Module

import RPi.GPIO as GPIO             #import Raspberry Pi GPIO module
from time import sleep
GPIO.setmode(GPIO.BCM)              #set Broadcom SOC Channel
GPIO.setwarnings(False)             #Disable warnings


Entrance = 17                       #Insert LDR at Entrance to GPIO 17         
GPIO.setup(Entrance, GPIO.IN)       #Set LDR at Entrance as Input
Exit = 27                           #Insert LDR at Exit to GPIO 27
GPIO.setup(Exit, GPIO.IN)           #Set LDR at Exit as Input

LED_CLK = 21                        #Insert SCL pin of LED BAR MODULE to GPIO 21
LED_DATA = 20                       #Insert SDA pin of LED BAR MODULE to GPIO 20
GPIO.setup(LED_CLK, GPIO.OUT)       #||Set SCL PIN as output
GPIO.setup(LED_DATA, GPIO.OUT)      #||Set SDA PIN as output
GPIO.output(LED_CLK, GPIO.HIGH)     #||Set SCL output initial value as HIGH
GPIO.output(LED_DATA, GPIO.HIGH)    #||Set SDA output initial value as HIGH

_state = 10 * [0]                   #Define array of 10 memory as _state and initial value as OFF for all 10 bars in LED_BAR module


def setBits(count):                 #Function to Set LED ON value 0x20 and OFF value 0x00 in _state array of memory
    global _state

    for i in range(10):             #
        if (count>i):               #if _state memory array address < count value 
            _state[i] = 0x20        #Set Led bar is ON   
        else:                       #if not...
            _state[i] = 0x00        #Set Led bar is OFF

    setData()                       #Call I2C function to output the _state memory array value to LED_BAR
    

def setData():                      #Function to output _state memory content to LED bar through I2C ommunication
    global _state
    sendData(0)

    for i in range(10):
        sendData(_state[10 - i - 1])        #Last memory value to first output to match the LED_BAR requirement 

    sendData(0)
    sendData(0)
    GPIO.output(LED_DATA, GPIO.LOW)         #Stop Condition of I2C
    sleep(0.01)                             #sleep 10 millisecond     
    for i in range(4):
        GPIO.output(LED_DATA, GPIO.HIGH)
        GPIO.output(LED_DATA, GPIO.LOW)
        

def sendData(data):                         #Send data to LED_BAR using I2C communication protocol  
    state=GPIO.LOW
    state1=GPIO.LOW
    
    for i in range(16):
        if (data & 0x8000):                 # Check MSB of the value in data
            state1 = GPIO.HIGH              # If MSB high set SDA value as High
        GPIO.output(LED_DATA, state1)       # set SDA pin output to SDA value 
        state = 1 - state                   # Togle SCL value
        GPIO.output(LED_CLK, state)         # set SCL pin output to SCL value 
        data = data << 1                    # bitwise shift left 1 bit to update MSB in data
        #print(data)
   

counter = 0                                 #Initialize counter as zero at first
Entrance_Statepre = False                   #Initialize Entrance_Statepre or previous Entrance State as False
Exit_Statepre = False                       #Initialize Exit_Statepre or previous Exit State as False

while True:
    Entrance_State = GPIO.input(Entrance)   #set Entrance_State
    Exit_State = GPIO.input(Exit)

    if Entrance_Statepre == True and Entrance_State == False:   #if car begin to block the LDR at Entrance ...
        counter += 1                                            #increment counter
        if counter >10:                                         #if number of cars inside is above 10...
            counter = 10                                        #counter will remain 10 
            
        setBits(counter) 
        
    elif Exit_Statepre == True and Exit_State == False:         #if car about to clear LDR at Exit 
        counter -= 1                                            #decrement counter
        if counter <0:                                          #if count value is calculated to be below 0
            counter = 0                                         #counter will remain 0 in Led Bar Module
            
        setBits(counter)
        
    Entrance_Statepre = Entrance_State  #as it goes as a loop, update "Entrance_Statepre" as equal to current Entrance LDR state
    Exit_Statepre = Exit_State          #as it goes as a loop, update "Exit_Statepre" as equal to current Exit LDR state



        
        


     

