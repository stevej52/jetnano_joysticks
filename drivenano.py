#!/usr/bin/env python
print("Importing Stuff")
import time
import sys, termios, tty, os
import adafruit_pca9685
from adafruit_servokit import ServoKit
import serial
import board
import busio


from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from pymodbus.compat import iteritems

import logging

logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.INFO)

client = ModbusClient('192.168.50.147', port=502)
client.connect()



#from approxeng.input.selectbinder import ControllerResource

global eyemin, eyemax, eyeval, eyeinit, turninit, turnval, thrval, minl, maxr, maxthr, minthr, thrinit, loopcount, avoid, ax1, ax2, ax3, ax4, bt23

avoid=False

print("Initializing IO System")

kit = ServoKit(channels=16, address=0x40)
print("Initializing IO System - kit")

i2c = busio.I2C(board.SCL, board.SDA)
print("Initializing IO System - board")
pca = adafruit_pca9685.PCA9685(i2c)
print("Initializing IO System - pca")

#kit.set_pwm_freq(50)
#pca.setPWMFreq(50)
pca.frequency = 100
print("Initializing IO System freq")

ax1 = 25600
ax2 = 25600
ax3 = 25600
ax4 = 25600
bt23=0
def getjoy():
    global eyemin, eyemax, eyeval, eyeinit, turninit, turnval, thrval, minl, maxr, maxthr, minthr, thrinit, loopcount, avoid, ax1, ax2, ax3, ax4, bt23
    address = 128
    count   =  5
    result  = client.read_holding_registers(address, count,  unit=1)
    decoder = BinaryPayloadDecoder.fromRegisters(result.registers)
    decoded = { 'AXIS1': decoder.decode_16bit_uint(), 'AXIS2': decoder.decode_16bit_uint(),'AXIS3': decoder.decode_16bit_uint(), 'AXIS4': decoder.decode_16bit_uint(), 'bt23': decoder.decode_16bit_uint()}

    print("-" * 60)
 #   print("Decoded Data")
#    print("-" * 60)
    for name, value in iteritems(decoded):
#        print ("%s\t" % name, value)
        if name=='AXIS1':
            ax1= value
        if name=='AXIS2':
            ax2= value      
        if name=='AXIS3':
            ax3= value
        if name=='AXIS4':
            ax4= value
        if name=='bt23':
            bt23=value
def getch():

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

button_delay = 0.2

minl=40
maxr=120
maxthr=100
minthr=60
turninit = 102
thrinit = 75
turnval=turninit
thrval=thrinit
eyeinit = 80
eyemin = 0
eyemax = 180
eyeval=eyeinit


print("Initializing Throttle")
kit.servo[0].angle = thrinit
time.sleep(2)
print("Initializing Steering")
kit.servo[1].angle = turninit

bs1=180-turnval
kit.servo[2].angle = bs1

#kit.servo[5].angle = turninit
#kit.servo[4].angle = eyeinit



char = 'l'


loopcount = 0
lastchar='k'
newkeypress=True

while bt23<200:
    print("EAC OFF - READY TO ARM")
    getjoy()




while bt23>200:
    print("EAC ARM")
 #   char = getch()
    getjoy()
#    print(ax1)
#    print(ax2)
#    print(ax3)
#    print(ax4)
    loopcount=loopcount+1


    if (ax1 < 25500): 
        print('Joystick Left')

    elif(ax1 > 25700):
        print('Joystick Right')
 
    else:
        print('Joystick Centered')


    if (ax3 < 25500): 
        print('Throttle UP')

    elif(ax3 > 25700):
        print('Throttle DOWN')

    else:
        print('Throttle CENTERED')

    OldjRange = 50944
    NewjRange = (maxr - minl)  
    turnval=(((ax1) * NewjRange) / OldjRange) + minl

    OldtRange = 50944
    NewtRange = (maxthr- minthr)  
    thrval=(((ax3) * NewtRange) / OldtRange) + minthr


    if (char == "Q"):
        print("quit")
        turnval=turninit
        thrval=thrinit
#       kit.servo[3].angle = turnval
#       kit.servo[0].angle = thrval
#       kit.servo[4].angle = eyeval
#
        exit(0)

#       elif (not char):
#           print("No char")
#           continue


    elif (char == "r"):
        print('TURBO ON!')
        maxthr = 150
        minthr = 40
        avoid=True

    elif (char == "e"):
        print('e pressed - STOP and CENTER')
        turnval=turninit
        thrval=thrinit
        eyeval=eyeinit
        kit.servo[0].angle = thrval

    elif (char == "a"):
        print('Left pressed')
        if char==lastchar:
            turnval = turnval-4

        else:
            turnval = turnval-8

        if turnval<minl:
            turnval=minl


    elif (char == "d"):
        print('Right pressed')
        if char==lastchar:
            turnval = turnval+4
        else:
            turnval = turnval+8

        if turnval>maxr:
            turnval=maxr

    elif (char == "w"):
        print('Up pressed')
        if char==lastchar:
            thrval = thrval-1

        else:
            thrval = thrval-2
        if thrval < minthr:
            thrval = minthr
        kit.servo[0].angle = thrval
    elif (char == "s"):
        print('Down pressed')

        if char==lastchar:
            thrval = thrval+1

        else:
            thrval = thrval+2

        if thrval > maxthr:
            thrval = maxthr

        kit.servo[0].angle = thrval

    elif (char == "z"):
            print('Steering Full Left')
            turnval = minl
            kit.servo[1].angle = turnval
            bs1=180-turnval
            kit.servo[2].angle = bs1

    elif (char == "c"):
            print('Steering Full Right')
            turnval = maxr
            kit.servo[1].angle = turnval
            bs1=180-turnval
            kit.servo[2].angle = bs1
    elif (char == "x"):
            print('Center Steering')
            turnval=turninit
            kit.servo[1].angle = turnval
            kit.servo[2].angle = turnval

    elif (char == "t"):
            print('TURBO OFF')
            maxthr = 100
            minthr = 60

    # with ControllerResource() as joystick:
        # print(type(joystick).__name__)
        # while joystick.connected:
            # axis_list = [ 'lx', 'ry' ]
            # for axis_name in axis_list:
                # # desired_angle is in degrees
                # joystick_value = joystick[axis_name]
                # # The joystick value goes from -1.0 ... 1.0 (a range of 2)
                # # Normalize within a range of 180 degrees
                # desired_angle = (joystick_value+1)/2*180
                
                # if  axis_name == 'lx' :
                    # kit.servo[0].angle=desired_angle
                    # bs1=180-desired_angle
                    # kit.servo[1].angle=bs1
                    # # print(axis_name, joystick[axis_name])
                    
                # if axis_name == 'ry' :
                     # kit.continuous_servo[1].throttle=joystick[axis_name]



    lastchar=char
    kit.servo[0].angle = thrval
    kit.servo[1].angle = turnval
    bs1=180-turnval
    kit.servo[2].angle = bs1
    print("lastchar="+lastchar+"  TURN="+str(turnval)+" THROTTLE="+str(thrval)+" EYE="+str(eyeval))

else:
    print("EAC OFF")
    turnval=turninit
    thrval=thrinit
    kit.servo[0].angle = thrval
    kit.servo[1].angle = turnval
    bs1=180-turnval
    kit.servo[2].angle = bs1
