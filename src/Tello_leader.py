import time
from djitellopy import Tello
import json
import numpy as np
import cv2

# Flags
Land_Flag = 0 # 0000 0000 0000 0000

# Drones shared variables/resources
Dist_travelled = 0.0
Speed = 50

# Tello leader parameters
tello_leader = Tello(host = "192.168.1.29")
json_File_one = open("Plan 1", "r")
Plan_one = json.load(json_File_one)

NO_OF_WAYPOINTS = len(Plan_one)

# Tello follower parameters
tello_one = Tello()
tello_two = Tello()
tello_three = Tello()

def pixels_To_cm(pixels):
    
    real_map = 2000 # 2000cm
    picture_map = 500 # 500 pixels

    cm = (real_map/picture_map) * pixels
    return int(cm)

def flight_motion(tello):
    global Land_Flag
    global waypoint_index

    global Speed

    if Plan_one[waypoint_index]["motion"] == "forward":
        tello.send_rc_control(0, Speed, 0, 0)

    elif Plan_one[waypoint_index]["motion"] == "backward":
        tello.send_rc_control(0, -Speed, 0, 0)

    elif Plan_one[waypoint_index]["motion"] == "rotate_right":
        tello.rotate_clockwise(Plan_one[waypoint_index]["distance"])

    elif Plan_one[waypoint_index]["motion"] == "rotate_left":
        tello.rotate_counter_clockwise(Plan_one[waypoint_index]["distance"])     

def failSafe(tello):
    # Safety measure func
    # register tof value as int
    max_retries = 4

    for retry in range(max_retries):
        try:

            tof_value = tello.send_read_command("EXT tof?") # its in string initially
            tof_value = int(tof_value[4:]) # attempt to convert to int
            break
        
        except:
            continue

    while tof_value < 1000: # less than 1000mm
        tello.go_xyz_speed(-20, 0, 0, 10)

        # reregister tof value as int
        for retry in range(max_retries):
            try:

                tof_value = tello.send_read_command("EXT tof?") # its in string initially
                tof_value = int(tof_value[4:]) # attempt to convert to int
                break
        
            except:
                continue

        if retry == (max_retries - 1):
            return

tello_leader.connect()
tello_leader.takeoff()

for waypoint_index in range(NO_OF_WAYPOINTS):

    waypoint_dist = pixels_To_cm(Plan_one[waypoint_index]["distance"])

    flight_motion(tello_leader)

    prev_timing = time.time()

    while Dist_travelled < waypoint_dist:
        # swarm.sequential(new_mission_pad_detection)
        current_timing = time.time()
        time_interval = current_timing - prev_timing
        Dist_travelled += Speed * time_interval
        prev_timing = current_timing

    tello_leader.send_command_without_return('stop')
    time.sleep(3)
    failSafe(tello_leader)
    Dist_travelled = 0.0

tello_leader.land()
tello_leader.end()

