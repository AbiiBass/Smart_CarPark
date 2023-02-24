#DVA Project
#Requirement: Gantry

import RPi.GPIO as GPIO             #import Raspberry Pi GPIO module
import time                         #import time
import smbus                        #Open i2c bus 1 and read one byte from address 80
import math                         #To use mathematical fucntions and give acced to underlying C lib functions
GPIO.setwarnings(False)             #Disable warnings
GPIO.setmode(GPIO.BCM)              #set Broadcom SOC Channel

###Inputs###
MS = 26                             #insert Motion Sensor to GPIO 26 
GPIO.setup (MS, GPIO.IN)            #set Motion Sensor as input
LDR = 22                            #insert LDR to GPIO 22
GPIO.setup(LDR, GPIO.IN)            #set Motion Sensor as input

###Outputs###
OpeningMotor = 25                   #insert A-IA(OpeningMotor) pin at GPIO 25
ClosingMotor = 23                   #insert A-IB(ClosingMotor) pin at GPIO 23
GPIO.setup(OpeningMotor, GPIO.OUT)  #set A-IA pin as Output 
GPIO.setup(ClosingMotor, GPIO.OUT)  #set A-IB pin as Output

power_mgmt_1=0x6b   #Define Power Management 1 as 0x6b
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
        
    
while True:
    Mdetected = GPIO.input(MS)        #define Mdetected as Motion Detection
    Ldetected = GPIO.input(LDR)       #define Ldetected as Light Detection

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




        
        
    
