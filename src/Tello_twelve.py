import time
from djitellopy import Tello
import json
import numpy as np
import cv2

# Drones shared variables/resources
Dist_travelled = 0.0
Speed = 30
Wake_up_time = 0

# Tello leader parameters
tello_leader = Tello()
json_File_one = open("Plan 4", "r")
Plan_one = json.load(json_File_one)

NO_OF_WAYPOINTS = len(Plan_one)

def pixels_To_cm(pixels):
    
    real_map = 2000 # 2000cm
    picture_map = 500 # 500 pixels

    cm = (real_map/picture_map) * pixels
    return int(cm)

def flight_motion(tello):
    global waypoint_index
    global Dist_travelled

    global Speed

    if Plan_one[waypoint_index]["motion"] == "forward":
        tello.send_rc_control(0, Speed, 0, 0)
 
    elif Plan_one[waypoint_index]["motion"] == "backward":
        tello.send_rc_control(0, -Speed, 0, 0)

    elif Plan_one[waypoint_index]["motion"] == "rotate_right":
        tello.rotate_clockwise(Plan_one[waypoint_index]["distance"])
        Dist_travelled = 90

    elif Plan_one[waypoint_index]["motion"] == "rotate_left":
        tello.rotate_counter_clockwise(Plan_one[waypoint_index]["distance"])   
        Dist_travelled = 90

def failSafe(tello):
    # Safety measure func
    # register tof value as int
    max_retries = 1

    for retry in range(max_retries):
        try:

            tof_value = tello.send_read_command("EXT tof?") # its in string initially
            tof_value = int(tof_value[4:]) # attempt to convert to int
            break
        
        except:
            continue
    
    try:
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
    except:
        return

    if retry == (max_retries - 1):
        return

def leader_mission_pad_detection(tello):
    # mission pad detection
    if tello.get_mission_pad_id() == 1:

        tello.go_xyz_speed_mid(0,0,-50, Speed, 1)
        tello.land()
        tello.end()

    elif tello.get_mission_pad_id() == 2:

        tello.go_xyz_speed_mid(0,0,-50, Speed, 2)
        tello.land()
        tello.end() 

    else:
        return

def leader_anchor_point(tello, mid, x):
    global Dist_travelled
    global waypoint_dist

    if tello.get_mission_pad_id() == mid:
        tello.go_xyz_speed_mid(x,0,120,Speed,mid)

        Dist_travelled = waypoint_dist
    else:
        return

# Main code starts here #
tello_leader.connect()
tello_leader.takeoff()
tello_leader.go_xyz_speed_mid(0,0,120,Speed,8)
tello_leader.disable_mission_pads()
tello_leader.enable_mission_pads()
time.sleep(2)

for waypoint_index in range(NO_OF_WAYPOINTS):

    waypoint_dist = pixels_To_cm(Plan_one[waypoint_index]["distance"])

    flight_motion(tello_leader)

    prev_timing = time.time()

    while Dist_travelled < waypoint_dist:

        leader_mission_pad_detection(tello_leader)

        current_timing = time.time()
        time_interval = current_timing - prev_timing
        Wake_up_time += time_interval
        if Wake_up_time > 5.0:
            try:
                tello_leader.query_battery()
                Wake_up_time = 0.0

            except:
                Wake_up_time = Wake_up_time
        Dist_travelled += Speed * time_interval
        prev_timing = current_timing

    tello_leader.send_rc_control(0,0,0,0) # Stop the drone after command from flight motion
    tello_leader.disable_mission_pads()
    tello_leader.enable_mission_pads()
    time.sleep(2)
    leader_anchor_point(tello_leader, 4, 0)
    failSafe(tello_leader)
    Dist_travelled = 0.0

tello_leader.land()
tello_leader.end()

