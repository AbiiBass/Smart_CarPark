#DVA Project
#Requirement: Parking Permit Sticker

import smbus            # Open SystemManagement(i2c) bus 
import time            
bus = smbus.SMBus(1)    # Open i2c bus 1 and read one byte from address 80
from signal import signal, SIGTERM, SIGHUP, pause
from rpi_lcd import LCD #import LCD, adress is 7x27
lcd = LCD()

# I2C address 0x29
# Register 0x12 has device ver. 
# Register addresses must be OR'ed with 0x80

bus.write_byte(0x29,0x80|0x12)  #for RGB sensor
ver = bus.read_byte(0x29)       #for RGB sensor
# version # should be 0x44

def safe_exit(signum, frame):   #point to the frame that was interrupted by the signal
    exit(1)

signal(SIGTERM, safe_exit)      #for LCD screen
signal(SIGHUP, safe_exit)       #for LCD screen

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
        
        if red < green > blue:  #if green color is detected     ###############################
            lcd.text("Hello Member,", 1) #LINE 1                ##| LCD display will say    |##
            lcd.text("free parking", 2)  #LINE 2                ##|    "free parking"       |##
            print("Member") #print update for checking purpose  ###############################

        else:               #if green color not detected        ###############################
            lcd.text("Hello visitor,", 1)  #LINE 1              ##| LCD display will say    |##
            lcd.text("please pay $2.30", 2)#LINE 2              ##|  "Parking Payment"      |##
            print("Visitor")#print update for checking purpose  ###############################
        time.sleep(2)
else: 
    print ("Device not found\n")
