import time
from djitellopy import TelloSwarm
import json

json_File_one = open("Plan 1", "r")
Plan_one = json.load(json_File_one)
# print(Plan_one[0]["motion"])
# print(Plan_one[0]["distance"]) # in pixels
# print(len(Plan_one))

# Collated list of Tellos to connect to
swarm = TelloSwarm.fromIps([
    "192.168.1.102",
    "192.168.1.103",
])

def pixels_To_cm(pixels):
    
    real_map = 2000 # 2000cm
    picture_map = 500 # 500 pixels

    cm = (real_map/picture_map) * pixels
    return cm

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

def waypoint_flight(drone_number, tello):

    number_of_waypoints = len(Plan_one) - 1

    for waypoint_index in number_of_waypoints:

        if Plan_one[waypoint_index]["motion"] == "forward":
            distance = pixels_To_cm(Plan_one[waypoint_index]["distance"])
            # tello.move_forward(distance)
            tello.go_xyz_speed(distance, 0, 50, 50)

        elif Plan_one[waypoint_index]["motion"] == "backward":
            distance = pixels_To_cm(Plan_one[waypoint_index]["distance"])
            # tello.move_backward(distance)
            tello.go_xyz_speed(distance, 0, 50, 50)

        elif Plan_one[waypoint_index]["motion"] == "rotate_right":
            tello.rotate_clockwise(Plan_one[waypoint_index]["distance"])

        elif Plan_one[waypoint_index]["motion"] == "rotate_left":
            tello.rotate_counter_clockwise(Plan_one[waypoint_index]["distance"])

        swarm.sync()  


# main code
swarm.connect()
swarm.parallel(lambda drone_number, tello : tello.set_mission_pad_detection_direction(2))
swarm.takeoff()
swarm.parallel(waypoint_flight)
swarm.land()

swarm.end()

