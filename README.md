# jetnano_joysticks
Jetson Nano control and vision with 4-Wheel Steering, ROS2 RealSense2, RPlidar, BNO055, Python3, Pygame and ModBus
ROS2, RealSense2, RPLidar and Python code to drive the Jetson Nano using modbus joystick commands

Using:
PC - Ubuntu 20.04 and ROS2 FOXY
   - 2 Joysticks, Thrustmaster HOTAS Joystick and Throttle


Jetson Nano - Ubuntu 18.04 and ROS2 Eloquent
            - Adafruit PCA9685 16 Channel PWM driver board
            - BNO055 gyro
            - USB wifi card
            - RPLidar
            - Realsense D435
            - 4-Wheel Steering

sudo pip3 install adafruit-servokit



Joystick Control - Pygame and Modbus: PyModbus

sudo pip3 install pymodbus

sudo pip3 install pygame

Build the ROS2 packages if needed - realsense2, rplidar, bno055 or use your own camera solution

colcon build --symlink-install

start ROS2 Realsense node

ros2 launch realsense_examples rs_camera.launch.py


Lidar node - Lidar works well in ROS2 but it also has python code unimplemented now

sudo chmod 666 /dev/ttyUSB0

ros2 launch rplidar_ros rplidar.launch.py



Visualization - For the cameras, I keep the subsriptions to a minimum for a faster frame rate for just driving. Nav2 and slamtoolbox create maps and can create pathways but with no control node yet, I'm using Python.

rviz2


*********************************
Python code

I actually need to get all this running in ROS2, but that becomes difficult when I want my PC to run Ubuntu 20.04 which is fine and can run ROS2 Foxy but... The Jetson Nano image only runs Ubuntu 18.04 and that only allows it to run ROS2 Eloquent whis has less features.

Also running all the nodes in ROS2 gets crazy with 8 or more terminals open and although it's well written and distributed, there are many working parts all connected so super easy to break something when coding.

Also would have to build my own ROS2 PCA9658 package as one does not exist. 

There is a Jetson Nano 20.04 image out there which would be great but i couldn't get it to work. There are several revision versions of the Nano so that makes it even harder.


Pygame is the easiest way to get Joystick data from the PC but pygame doenst like to run remotely because it uses a diplay and can't find one through SSH. There are ways around this through Pygame but also around Pygame using ModBus.

I had never heard of ModBus but apparently it's ancient and works great.


I run these scripts in different terminal windows - next step, one PC run script and one Robot run script

sync_server.py

Run on the PC. Starts the ModBus server - Set for IP transfer. You will need to change the IP addresses to the machine running the server. can just use localhost addresses. Must change the settings to use UDP, binary, ASCII or serial transfers - there are async server examples in the documentation at:
https://pymodbus.readthedocs.io/en/v1.3.2/examples/asynchronous-processor.html
The server can be set to only recieve a set number of commands, but is currently set to the maximum number but i dont know what that is, hundreds or thousands id guess even though im only sending 5 right now.


modbus_joy.py

Run on the PC. Starts the Pygame Joystick modules and Modbus client -You will need to set your IP address to the machine running the sync_server. can use localhost addreses if its running on the same machine. Currently set for the Thrustmaster dual joystick setup described above.  Need to set Joystick numbers, axis and buttons so your rig will work if you don't have the Thrustmaster setup. Only 5 axis/buttons transferring to the server now, you coud set up all axis and all buttons if you wanted but I'm keeping it light and only need the 5 to make it work. I'm looking forward to having most of the buttons and hats do something cool like move the camera with servos, make sounds from a speaker or enable the lidar for obstacle avoidance. The PCA9658 can control up to 16 servos or esc's per board and you can daisy-chain 99 boards so thats a lot of servos!


joysticks.py

Joystick Detection Helper - Run this stand alone program on the PC to see what Joysticks pygame sees and all of the axis and button states. Very helpful for setup but not needed to control the robot.


drivenano.py

Run on the Jetson nano with SSH. Starts the robot ModBus listening client and PCA9685 servo/esc PWM driver.
Previous versions used to detect keypresses but commented out the keypress code and adapted to Modbus Joystick. The servo controls are setup for 4-Wheel Steering with the rear wheels turning the opposite direction as the front wheels for better turning radius. The throttle is setup for forward and reverse with no throttle with the throttle joystick in the center.

Of course all code was stolen from somewhere, as is standard practice. Mainly castetsb and the pygame/pymodbus examples.

Nothing is optimized and many of the print statements are still uncommented so I can see whats going on. Commenting those out would make it run smoother.

Next steps: async programs with multithreadding, python lidar obstacle avoidance, tkinter diplay with stats


I got the idea from: https://github.com/castetsb/urJoystickControl

---EDIT 2/2/2020---

ros2_pca9685 package created

ROS2 Package to convert /cmd_vel to PWM signals using a PCA9685

All code was adapted from these two tutorials.

https://index.ros.org/doc/ros2/Tutorials/Creating-Your-First-ROS2-Package/

https://index.ros.org/doc/ros2/Tutorials/Writing-A-Simple-Py-Publisher-And-Subscriber/

-----Changes needed to subscriber_member_function.py------------------

pca.frequency = 100 # I keep reading that 50Hz is good for servos even thought I thought it was 75Hz, but after lots of testing I'm using 100Hz mainly for proper ESC zero

maxr=135 # Max Right servo travel

minl=30 # Max Left servo travel

maxthr=125 # Max Throttle PWM

minthr= 65 # Min Throttle PWM

thrinit = 90 # Throttle Zero

strinit = 85 # Steering Zero

print("Initializing Propulsion System") #

kit.servo[0].angle = thrinit # this Throttle Servo number will need to be set

time.sleep(1) # wait 1 second for the ESC to initialize zero

print("Initializing Steering System")

kit.servo[1].angle = strinit #this Steering Servo number will need to be set

bs1=180-thrinit # reverse the steering number for 4-Wheel steering

kit.servo[2].angle = bs1 #this is the back servo for 4-Wheel Steering Servo- Runs reverse direction - number will need to be set

Also change servo numbers in move_robot() function

Build after all changes made:

cd dev_ws

colcon build --packages-select ros2_pca9685

source ./install/setup.bash

ros2 run ros2_pca9685 listener

use ROS2 package teleop_twist_joy for joystick control - active only while pushing the 'activate' or 'turbo' button

ros2 launch teleop_twist_joy teleop-launch.py

