Python code to drive the Jetson Nano using modbus joystick commands

Using:
PC - Ubuntu 20.04 and ROS2 FOXY
   - 2 Joysticks, Thrustmaster HOTAS Joystick and Throttle


Jetson Nano - Ubuntu 18.04 and ROS2 Eloquent
            - Adafruit PCA9685 16 Channel PWM driver board
            - BNO055 gyro
            - USB wifi card
            - RPLidar
            - Realsense D435
sudo pip3 install adafruit-servokit



Joystick Control - Pygame and Modbus: PyModbus
sudo pip3 install pymodbus
sudo pip3 install pygame

Build the ROS2 packages if needed - realsense2, rplidar, bno055 or use your own camera solution
colcon build --symlink-install

start ROS2 Realsense node
ros2 launch realsense_examples rs_camera.launch.py


Lidar node
sudo chmod 666 /dev/ttyUSB0
ros2 launch rplidar_ros rplidar.launch.py


Visualization - For the cameras, I keep the subsriptions to a minimum for a faster frame rate
rviz2


*******************************
Python code

I actually need to get all this running in ROS2, but that becomes difficult when I want my PC to run Ubuntu 20.04 which is fine and can run ROS2 Foxy but... The Jetson Nano image only runs Ubuntu 18.04 and that only allows it to run ROS2 Eloquent whis has less features.

There is a Jetson Nano 20.04 image out there but i couldn't get it to work. There are several revision versions of the Nano so that makes it even harder.


Pygame is the easiest way to get Joystick data but pygame doenst like to run remotely because it uses a diplay. Theres ways around this through Pygame but also around Pygame using ModBus.


I run these in different terminal windows - next step, one PC run script and one Robot run script

sync_server.py

Run on the PC. Starts the ModBus server - Set for IP transfer. You will need to change the IP addresses to the machine running the server. can just use localhost addresses. Must change the settings to use UDP, binary, ASCII or serial transfers - there are async server examples in the documentation at:
https://pymodbus.readthedocs.io/en/v1.3.2/examples/asynchronous-processor.html
The server can be set to only recieve a set number of commands, but is currently set to the maximum number but i dont know what that is, hundreds or thousands id guess even though im only sending 5 right now.


modbus_joy.py

Run on the PC. Starts the Pygame Joystick modules and Modbus client -You will need to set your IP address to the machine running the server. can use localhost addreses. Currently set for the Thrustmaster dual joystick setup described above.  Need to set Joystick numbers, axis and buttons. Only 5 axis/buttons transferring now, you coud set up all axis and all buttons if you wanted but I'm keeping it light.


joysticks.py

Joystick Detection Helper - Run this program on the PC to see what Joysticks pygame sees and all of the axis and button states. Very helpful.


drivenano.py

Run on the Jetson nano. Starts the robot ModBus listening client and PCA9685 servo/esc PWM driver.

All code was stolen from somewhere, as is standard practice.

I got the idea from: https://github.com/castetsb/urJoystickControl





