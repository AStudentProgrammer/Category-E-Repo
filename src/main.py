# Set simple swarm code for now
from djitellopy import TelloSwarm
import time

# Collated list of Tellos to connect to
swarm = TelloSwarm.fromIps([
    "192.168.1.102",
    "192.168.1.103",
])

def battery_checker(drone_number, tello):
    tello.query_battery()

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

def square_movement(drone_number, tello):

    # Fly relative to its current position
    tello.go_xyz_speed(0, -25, 0, 25)
    swarm.sync()
    tello.go_xyz_speed(25, 0, 0, 25)
    swarm.sync()
    tello.go_xyz_speed(0, 25, 0, 25)
    swarm.sync()
    tello.go_xyz_speed(-25, 0, 0, 25)
    swarm.sync()

# main code
swarm.connect()
swarm.takeoff()
swarm.parallel(square_movement)
swarm.land()

swarm.end()

# testing of json file
# import json

# json_File = open("waypoint.json", "r")
# sample_load_file = json.load(json_File)
# print(sample_load_file["wp"])
