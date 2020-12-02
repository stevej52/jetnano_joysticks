# Copyright 2016 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import rclpy
from rclpy.node import Node

from std_msgs.msg import String
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Joy

print("Initializing IO System - import")
import time
import adafruit_pca9685
from adafruit_servokit import ServoKit
import serial
import board
import busio

global thrinit, strinit, maxr, minl, maxthr, minthr

kit = ServoKit(channels=16, address=0x40)
print("Initializing IO System - kit")

i2c = busio.I2C(board.SCL, board.SDA)
print("Initializing IO System - board")
pca = adafruit_pca9685.PCA9685(i2c)
print("Initializing IO System - pca")

#kit.set_pwm_freq(50)
#pca.setPWMFreq(50)
print("Initializing IO System - freq")
pca.frequency = 100


maxr=135
minl=30
maxthr=125
minthr= 65
thrinit = 90
strinit = 85

print("Initializing Propulsion System")
kit.servo[0].angle = thrinit
time.sleep(1)

print("Initializing Steering System")
kit.servo[1].angle = strinit

bs1=180-thrinit
kit.servo[2].angle = bs1

print("Listener Node Started...")


class MinimalSubscriber(Node):

    def __init__(self):
        super().__init__('minimal_subscriber')
        self.subscription = self.create_subscription(
            Twist,
            'cmd_vel',
            self.listener_callback,
            10)
        self.subscription  # prevent unused variable warning

    def listener_callback(self, msg):
        throttle=msg.linear.x
        steering=msg.angular.z
  #      self.get_logger().info('Y AXIS: "%s"' % yaxis)
 #       self.get_logger().info('X AXIS: "%s"' % xaxis)
        self.get_logger().info('Throttle: "%s"' % throttle)
        self.get_logger().info('Steering: "%s"' % steering)
        
        oldstrvalue = float(steering)
        
        
        oldthrvalue = float(throttle)

        if oldstrvalue <0:
            oldstrvalue = -oldstrvalue
            
            newstrvalue=int(strinit+(oldstrvalue*((maxr-strinit)/3)))
        else:
            newstrvalue=int(strinit-(oldstrvalue*((strinit-minl)/3)))
            
 #       if oldthrvalue <0:
  #          oldthrvalue = oldthrvalue + 1

        if newstrvalue >maxr:
            newstrvalue = maxr
        if newstrvalue <minl:
            newstrvalue = minl           
       
       
        oldthrrange = 2
        newthrrange = maxthr-minthr
        newthrvalue = int(((oldthrvalue) * (newthrrange)+90))

        if newthrvalue >maxthr:
            newthrvalue = maxthr 

        if newthrvalue <minthr:
            newthrvalue = minthr 

        move_robot(newthrvalue, newstrvalue)
        
    def convertscales(oldvalue, oldmax, oldmin, newmax, newmin):
        oldrange = (oldmax - oldmin)  
        newrange = (newmax - newmin)  
        newvalue = (((oldvalue - oldmin) * newrange) / oldrange) + newmin
        return(newvalue)

        
def move_robot(thrnum,strnum):
    print("Moving Robot:  Throttle="+str(thrnum)+" ,  Steering="+str(strnum))
    kit.servo[0].angle = thrnum

    kit.servo[1].angle = strnum
    if strnum>strinit:
        bs1=strinit-(strnum-strinit)
    else:
        bs1= strinit+(strinit-strnum)

    print(bs1)
    kit.servo[2].angle = bs1        

def main(args=None):
    rclpy.init(args=args)

    minimal_subscriber = MinimalSubscriber()

    rclpy.spin(minimal_subscriber)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    minimal_subscriber.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
