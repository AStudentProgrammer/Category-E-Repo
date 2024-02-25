import time
from djitellopy import Tello
import json
import numpy as np
import cv2

# Flags
Land_Flag = 0 # 0000 0000 0000 0000

land_Flag_mask = {
    "Drone 1" : 1,
    "Drone 2" : 2,
    "Drone 3" : 4,
}

# Drones shared variables/resources
Dist_travelled = 0.0
Speed = 50

# Tello leader parameters
tello_leader = Tello()
json_File_one = open("Plan 1", "r")
Plan_one = json.load(json_File_one)

NO_OF_WAYPOINTS = len(Plan_one)

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

def leader_mission_pad_detection():
    # mission pad detection
    if tello_leader.get_mission_pad_id() == 1:

        # tello.send_control_command("stop") # hover

        # tello.send_command_without_return(f"go 0, 0, -50, {Speed}, 1")
        tello_leader.go_xyz_speed_mid(0,0,-50, Speed,1)
        tello_leader.land()
        # time.sleep(20)
        tello_leader.end()
    else:
        return

# Tello follower parameters
tello_one = Tello()
tello_two = Tello()
tello_three = Tello()

tello_follower_dict = {
    1 : tello_one,
    2 : tello_two,
    3 : tello_three
}

# frame_read = []

def follower_connect():
    number_of_followers = len(tello_follower_dict)

    for follower in range(number_of_followers):
        tello_follower_dict[follower+1].connect()

def follower_takeoff():
    number_of_followers = len(tello_follower_dict)

    for follower in range(number_of_followers):
        tello_follower_dict[follower+1].send_command_without_return("takeoff") # if wait for return, have to wait for everybody

def follower_stop():
    number_of_followers = len(tello_follower_dict)

    for follower in range(number_of_followers):
        tello_follower_dict[follower+1].send_command_without_return('stop')

def follower_movement():
    global Land_Flag

    number_of_followers = len(tello_follower_dict)

    for follower in range(number_of_followers):

        if Land_Flag & land_Flag_mask["Drone {}".format(follower + 1)]:
            continue
        else:
            flight_motion(tello_follower_dict[follower+1]) # use flight plan as a replacement for now
        
def follower_camera_setup():
    number_of_followers = len(tello_follower_dict)

    for follower in range(number_of_followers):
        tello_follower_dict[follower+1].streamoff()
        tello_follower_dict[follower+1].streamoff()
        frame_read.append(tello_follower_dict[follower+1].get_frame_read()) # to be tested

    return frame_read

def follower_mission_pad_detection():

    global prev_timing
    global Land_Flag

    number_of_followers = len(tello_follower_dict)
    # mission pad detection
    for follower in range(number_of_followers):

        tello = tello_follower_dict[follower+1]

        if Land_Flag & land_Flag_mask["Drone {}".format(follower + 1)]:
            continue
        else:
            if tello.get_mission_pad_id() == 1:

                tello_leader.send_command_without_return('stop') 
                follower_stop()

                # tello.send_command_without_return(f"go 0, 0, -50, {Speed}, 1")
                tello.go_xyz_speed_mid(0,0,-50, Speed,1)
                tello.land()
                # time.sleep(20)
                tello.end()

                # drone_number = 0
                # for Tellos in tello_follower_dict.values():
                #     drone_number += 1
                #     if Tellos == tello:
                #         Land_Flag += land_Flag_mask["Drone {}".format(drone_number + 1)]
                #     else:
                #         continue

                Land_Flag += land_Flag_mask["Drone {}".format(follower + 1)]

                flight_motion(tello_leader)
                follower_movement()
                prev_timing = time.time()
            else:
                continue


# Main code starts here #
tello_leader.connect()
tello_leader.takeoff()

for waypoint_index in range(NO_OF_WAYPOINTS):

    waypoint_dist = pixels_To_cm(Plan_one[waypoint_index]["distance"])

    flight_motion(tello_leader)

    prev_timing = time.time()

    while Dist_travelled < waypoint_dist:
        if Land_Flag == 8: # 111, all has landed
            leader_mission_pad_detection()

        else:
            follower_movement()
            follower_mission_pad_detection()

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

