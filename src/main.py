# Set simple swarm code for now
from djitellopy import TelloSwarm
import time

# Collated list of Tellos to connect to
swarm = TelloSwarm.fromIps([
    "192.168.1.101",
    "192.168.1.102",
])

# def battery_checker(drone_number, tello):
#     tello.query_battery()

def left_movement(drone_number, tello):
    if drone_number <= 1:               # drone_number start from 0
        tello.move_left(100) 

def right_movement(drone_number, tello):
    if drone_number > 1:
        tello.move_right(100)

# main code
swarm.connect()
swarm.parallel(left_movement)
time.sleep(10)
swarm.parallel(right_movement)

swarm.end()