# Set simple swarm code for now
from djitellopy import TelloSwarm
import time
import cv2

# Collated list of Tellos to connect to
swarm = TelloSwarm.fromIps([
    "192.168.1.101"
])

# def battery_checker(drone_number, tello):
#     tello.query_battery()

def left_movement(drone_number, tello):
    if drone_number <= 1:               # drone_number start from 0
        tello.move_left(100) 

def right_movement(drone_number, tello):
    if drone_number > 1:
        tello.move_right(100)

def forward_movement(drone_number, tello):
    tello.move_forward(50)
    swarm.sync()

def up_movement(drone_number, tello):
    tello.move_up(25)
    swarm.sync()

# main code
swarm.connect()
# swarm.parallel(up_movement)
# time.sleep(10)
# swarm.parallel(up_movement)
# swarm.land()
swarm.sequential(lambda i, tello: tello.streamon())
while True:
    img = swarm.sequential(lambda i, tello: tello.get_frame_read().frame)
    img = cv2.resize(img, (360,240))
    cv2.imshow("frame", img)
    cv2.waitKey(1)

swarm.end()