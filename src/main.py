# Set simple swarm code for now
from djitellopy import TelloSwarm
import time

# Collated list of Tellos to connect to
swarm = TelloSwarm.fromIps([
    "192.168.1.102",
    "192.168.1.103",
])

# Simulate the dataset retrieved from json
set_of_number = {
    # x, y, z, speed, yaw, mid1(unused), mid2(unused)
    "Set 1" : (0, -100, 50, 25, 90, 1, 2),
    "Set 2" : (100, -100, 50, 25, 90, 1, 2),
    "Set 3" : (100, 0, 50, 25, 90, 1, 2),
    "Set 4" : (0, 0, 50, 25, 90, 1, 2),
}

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

    index = 1

    while index <= len(set_of_number):

        # Pre-assign dictionary with more intuitive names
        x_dirn = set_of_number["Set {number}".format(number = index)][0]
        y_dirn = set_of_number["Set {number}".format(number = index)][1]
        z_dirn = set_of_number["Set {number}".format(number = index)][2]
        speed = set_of_number["Set {number}".format(number = index)][3]
        yaw = set_of_number["Set {number}".format(number = index)][4]
        
        # Fly relative to its current position
        tello.rotate_clockwise(yaw)
        tello.go_xyz_speed(x_dirn, (y_dirn - drone_number*90), z_dirn, speed)
        swarm.sync()

        index += 1

# main code
swarm.connect()
swarm.parallel(lambda drone_number, tello : tello.set_mission_pad_detection_direction(2))
swarm.takeoff()
swarm.parallel(square_movement)
swarm.land()

swarm.end()

# testing of json file
# import json

# json_File = open("waypoint.json", "r")
# sample_load_file = json.load(json_File)
# print(sample_load_file["wp"])
