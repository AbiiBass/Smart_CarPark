#DVA Project
#Requirement: Gantry & Car Update to LED Bar Module

import RPi.GPIO as GPIO             #import Raspberry Pi GPIO module
import time                         #import time
from time import sleep
import smbus                        #Open i2c bus 1 and read one byte from address 80
import math                         #To use mathematical fucntions and give acced to underlying C lib functions
GPIO.setwarnings(False)             #Disable warnings
GPIO.setmode(GPIO.BCM)              #set Broadcom SOC Channel

###Inputs###
MS = 26                             #insert Motion Sensor to GPIO 26 
GPIO.setup (MS, GPIO.IN)            #set Motion Sensor as input
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
   



###Outputs###
OpeningMotor = 25                   #insert A-IA(OpeningMotor) pin at GPIO 25
ClosingMotor = 23                   #insert A-IB(ClosingMotor) pin at GPIO 23
GPIO.setup(OpeningMotor, GPIO.OUT)  #set A-IA pin as Output 
GPIO.setup(ClosingMotor, GPIO.OUT)  #set A-IB pin as Output

power_mgmt_1=0x6b   #defube Power Management 1 as 0x6b
power_mgmt_2=0x6c   #Define Power Managenenr 2 as 0x6c

def read_byte(reg):                             #Read byte value from accelerometer 
    return bus.read_byte_data(address, reg)     #Read byte value from the address

def read_word(reg):                             #Read word value from accelerometer
    h=bus.read_byte_data(address, reg)          #Read High Side byte value from address
    l= bus.read_byte_data(address, reg+1)       #Read Low Side byte value from adress
    
    value= (h<<8)+1                             #Shift left high side 8 bits + add Low Side to form 16 bit          
    return value

def read_word_2c(reg):                          #Convert 2s compliment if value is negative          
    val=read_word(reg)
    if(val>=0x8000):                            # Check value is Negative number
        return-((65535 - val)+1)                # convert 2s compliment negative value
    else:
        return val                              # if positive value pass the value

bus= smbus.SMBus(1)                             #System Management Bus
address = 0x68                                  #Address is 0x68
bus.write_byte_data (address, power_mgmt_1, 0)



def Gate_off():                                 #Define Gate_off as...
    GPIO.output(OpeningMotor, False)
    GPIO.output(ClosingMotor, False)
    
def Gate_open():                                #Define Gate_open as...
    Accelerometer_yout = read_word_2c(0x3d)
    while Accelerometer_yout < 10000:           #Motor is ON until accelerometer detects gate is completely open
        Accelerometer_yout = read_word_2c(0x3d) #Y-axis calculation
        GPIO.output(OpeningMotor, True)         #Gate opening
        GPIO.output(ClosingMotor, False)        #^
        print (" Accelerometer_yout: ", ("%6d" % Accelerometer_yout))
    Gate_off()                                  #Motor stops once accelrometer detectd gate is open
    

def Gate_close():                               #Define Gate_close as...
    Accelerometer_yout = read_word_2c(0x3d)
    while Accelerometer_yout > 900:             #Motor is ON until accelerometer detects gate is completely close 
        Accelerometer_yout = read_word_2c(0x3d) #Y-axis calculation
        GPIO.output(OpeningMotor, False)        #Gate closing
        GPIO.output(ClosingMotor, True)         #^
        print (" Accelerometer_yout: ", ("%6d" % Accelerometer_yout))
    Gate_off()                                  #Motor stops once accelrometer detectd gate is closed




Gate_state = 0  #Gate state is officially 0
Gate_off()      #Gate is orignally off

counter = 0                                 #Initialize counter as zero at first
Entrance_Statepre = False                   #Initialize Entrance_Statepre or previous Entrance State as False
Exit_Statepre = False                       #Initialize Exit_Statepre or previous Exit State as False
       
    
while True:
    Mdetected = GPIO.input(MS)        #define Mdetected as Motion Detection
    Ldetected = GPIO.input(Entrance)       #define Ldetected as Light Detection

    Accelerometer_xout = read_word_2c(0x3b)    #X-axis calculation
    Accelerometer_yout = read_word_2c(0x3d)    #Y-axis calculation
    Accelerometer_zout = read_word_2c(0x3f)    #Z-axis calculation
    
    
    if Gate_state==0 and Mdetected == True and Ldetected == False: #if Gate state is 0, and Motion is detected, and Light is covered (by a car)
        Gate_open()                                                #Gate opens to let car in                         
        Gate_state = 1                                             #Gate state will become 0

        
    elif Gate_state==1 and Ldetected == True:                      #if Gate state is 1 and Light is detected, (car has passed through)
        time.sleep(1)                                              #will wait for 1 second
        Gate_close()                                               #Gate will close
        Gate_state = 0                                             #Gate state will become 0


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




        
        
    
