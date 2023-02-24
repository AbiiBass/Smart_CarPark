#DVA Project
#Requirement: Parking Permit Sticker

import smbus            # Open SystemManagement(i2c) bus           
bus = smbus.SMBus(1)    # Open i2c bus 1 and read one byte from address 80
from signal import signal, SIGTERM, SIGHUP, pause
from rpi_lcd import LCD #import LCD, adress is 7x27
lcd = LCD()
import  RPi.GPIO as GPIO                        #import RPi.GPIO moduole
from time import sleep
import time                                     #import time
GPIO.setmode(GPIO.BCM)                          #set Broadcom SOC Channel
GPIO.setwarnings(False)

#LED Bar Module
LED_CLK = 21                                    #set SCL to GPIO21
LED_DATA = 20                                   #set SDA to GPIO20

#Ultrasonic 1
trig = 17                                       #set trig pin to GPIO17
echo = 27                                       #set echo pin to GPIO27
led = 22                                        #set LED to GPIO22

#Ultrasonic 2
TRIG = 26                                       #set TRIG pin to GPIO26
ECHO = 19                                       #set ECHO pin to GPIO19
Red = 13                                        #set Red LED to GPIO13

#LED Bar Module
GPIO.setup(LED_CLK, GPIO.OUT)                   #set SCL as output
GPIO.setup(LED_DATA, GPIO.OUT)                  #set SDA as output

#Ultrasonic 1
GPIO.setup(trig, GPIO.OUT)                      #set trig pin as output 
GPIO.setup(echo, GPIO.IN)                       #set echo pin as input
GPIO.setup(led, GPIO.OUT)                       #set LED as output

#Ultrasonic 2
GPIO.setup(TRIG, GPIO.OUT)                      #set TRIG pin as output
GPIO.setup(ECHO, GPIO.IN)                       #set ECHO pin as input
GPIO.setup(Red, GPIO.OUT)                       #set Red LED as output

GPIO.output(LED_CLK, GPIO.HIGH)                 #SCL on
GPIO.output(LED_DATA, GPIO.HIGH)                #SDA on
_state = 10 * [0x20]                            #all LED in LED Bar Module is on

temp = 16                                           #set Temperature sensor to GPIO22
Norm = 19                                           #set Yellow LED to GPIO19
Hot = 12                                            #set Red LED to GPIO26

GPIO.setup(temp, GPIO.IN)                           #set Temperature sensor as input
GPIO.setup(Norm, GPIO.OUT)                          #set Yellow LED as output
GPIO.setup(Hot, GPIO.OUT)                           #set Red LED as output


# I2C address 0x29
# Register 0x12 has device ver. 
# Register addresses must be OR'ed with 0x80

bus.write_byte(0x29,0x80|0x12)  #for RGB sensor
ver = bus.read_byte(0x29)       #for RGB sensor
# version # should be 0x44

def safe_exit(signum, frame):   #point to the frame that was interrupted by the signal
    exit(1)

def setData():
    global _state
    sendData(0)

    for i in range(10):
        sendData(_state[10 - i - 1])            #last memory value to first output to match  the LED bar module requirement

    sendData(0)
    sendData(0)
    GPIO.output(LED_DATA, GPIO.LOW)             
    sleep(0.01)                                 #sleep 10 millisecond              
    for i in range(4):
        GPIO.output(LED_DATA, GPIO.HIGH)        
        GPIO.output(LED_DATA, GPIO.LOW)         

def sendData(data):
    state=GPIO.LOW
    state1=GPIO.LOW

    for i in range(16):
        if (data & 0x8000):                     #check MSB of the value in data
            state1 = GPIO.HIGH                  #if MSB high, set SDA value as HIGH
        GPIO.output(LED_DATA, state1)           #set SDA pin output to SDA value
        state = 1 - state                       #togle SCL value
        GPIO.output(LED_CLK, state)             #set SCL pin output to SCL value
        data = data << 1                        #bitwise shift left 1 bit to update MSB in data

def c():
    GPIO.output(led, 0)                         #LED off
    GPIO.output(Red, 1)                         #Red LED on
    global _state
    _state[2] = 0x00                            #2nd LED in Bar Module off
    _state[7] = 0x20                            #7th LED in Bar Module on
    setData()

def u():
    GPIO.output(led, 1)                         #LED on
    GPIO.output(Red, 0)                         #Red LED off
    global _state
    _state[2] = 0x20                            #2nd LED in Bar Module on
    _state[7] = 0x00                            #7th LED in Bar Module off
    setData()

def both():
    GPIO.output(led, 0)                         #LED off
    GPIO.output(Red, 0)                         #Red LED off
    global _state
    _state[2] = 0x00                            #2nd LED in Bar Module off
    _state[7] = 0x00                            #7th LED in Bar Module off
    setData()

def gone():
    GPIO.output(led, 1)                         #LED on
    GPIO.output(Red, 1)                         #Red LED on
    global _state
    _state[2] = 0x20                            #2nd LED in Bar Module on
    _state[7] = 0x20                            #7th LED in Bar Module on
    setData()

def NormalWeather():
    GPIO.output(Hot, False)                         #Red LED off
    GPIO.output(Norm, True)                         #Yellow LED on

def HotWeather():
    GPIO.output(Hot, True)                          #Red LED on
    GPIO.output(Norm, False)                        #Yellow LED off

def Off():
    GPIO.output(Hot, False)                         #Red LED off
    GPIO.output(Norm, False)                        #Yellow LED off




signal(SIGTERM, safe_exit)      #for LCD screen
signal(SIGHUP, safe_exit)       #for LCD screen
WeatherState = 0                                    #Initialize WeatherState to 0 at first


if ver == 0x44:
    print ("Device found\n")
    bus.write_byte(0x29, 0x80|0x00) # 0x00 = ENABLE register
    bus.write_byte(0x29, 0x01|0x02) # 0x01 = Power on, 0x02 RGB sensors enabled
    bus.write_byte(0x29, 0x80|0x14) # Reading results start register 14, LSB then MSB
    while True:
        data = bus.read_i2c_block_data(0x29, 0)
       # clear = clear = data[1] << 8 | data[0]
        red = data[3] << 8 | data[2]            #Calculation for Red Color
        green = data[5] << 8 | data[4]          #Calculation for Green Color
        blue = data[7] << 8 | data[6]           #Calculation for Blue Color
        rgb = (" R: %s, G: %s, B: %s\n") % (red, green, blue) #print values for checking purpose
      #  print (crgb)
        print (rgb)

        #Ultasonic 1
        GPIO.output(trig, True)                     #trig on
        time.sleep(0.00002)                         #delay for 0.02 millisecond
        GPIO.output(trig, False)                    #trig off

        while GPIO.input(echo)==0:                  #when echo does not receive any signal
            pulse_start = time.time()               #record time

        while GPIO.input(echo)==1:                  #when echo receives signal
            pulse_end = time.time()                 #record time

        pulse_duration = pulse_end - pulse_start    #duration between the time recorded
        d = pulse_duration *17150                   #find distance
        d = round(d, 2)                             #round distance to 2 decimal places
        print("Lot 1: ", d, " cm")                  #print distance from car to Ultrasonic 1
        
        #Ultrasonic 2
        GPIO.output(TRIG, True)                     #TRIG on
        time.sleep(0.00002)                         #delay for 0.02 millisecond
        GPIO.output(TRIG, False)                    #TRIG off

        while GPIO.input(ECHO)==0:                  #when ECHO does not receive any signal
            pulse_star = time.time()                #record time 

        while GPIO.input(ECHO)==1:                  #when ECHO receive signal
            pulse_en = time.time()                  #record time 

        pulse_duratio = pulse_en - pulse_star       #duration between the time recorded
        D = pulse_duratio *17150                    #find distance
        D = round(D, 2)                             #round distance to 2 decimal places
        print("Lot 2: ", D, " cm")                  #print distance from car to Ultrasonic 2

        if d < 20 and D > 20:                       #car parked under Ultrasonic 1
            c() 
            print("Lot 1 is taken")                 #print
        elif d > 20 and D < 20:                     #car parked under Ultrasonic 2
            u()
            print("Lot 2 is taken")                 #print
        elif d < 20 and D < 20:                     #cars parked under both Ultrasonic
            both()
            print("Both lots are taken")            #print
        elif d > 20 and D > 20:                     #no cars parked under both Ultrasonic
            gone()
            print("All lots are empty")             #print

        
        if red < green > blue:  #if green color is detected     ###############################
            lcd.text("Hello Member,", 1) #LINE 1                ##| LCD display will say    |##
            lcd.text("free parking", 2)  #LINE 2                ##|    "free parking"       |##
            print("Member") #print update for checking purpose  ###############################

        elif red > green < blue:               #if green color not detected        ###############################
            lcd.text("Hello visitor,", 1)  #LINE 1              ##| LCD display will say    |##
            lcd.text("please pay $2.30", 2)#LINE 2              ##|  "Parking Payment"      |##
            print("Visitor")#print update for checking purpose  ###############################
        time.sleep(2)

        tempstate = GPIO.input(temp)                    #set Temperature sensor as tempstate

        #Hot Weather
        if WeatherState == 0 and tempstate == False:    #when WeatherState is 0 and temperature is hot
            HotWeather()                                #Red LED on
            time.sleep(5)                               #delay 5 seconds
            Off()                                       #Both LED off
            WeatherState = 1                            #set WeahterState to 1

        elif WeatherState == 1 and tempstate == False:  #when WeatherState is 1 and temperature is hot
            Off()                                       #Both LED off
            WeatherState = 1                            #set WeahterState to 1

        #Normal Weather
        elif WeatherState == 1 and tempstate == True:   #when WeatherState is 1 and temperature is normal
            NormalWeather()                             #Yellow LED on
            time.sleep(5)                               #delay 5 seconds
            Off()                                       #Both LED off
            WeatherState = 0                            #set WeatherState to 0

        elif WeatherState == 0 and tempstate == True:   #when WeatherState is 0 and temperature is normal
            Off()                                       #Both LED off
            WeatherState = 0                            #set WeatherState to 0


else: 
    print ("Device not found\n")
