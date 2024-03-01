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
    # "Drone 3" : 4,
}

# Drones shared variables/resources
Dist_travelled = 0.0
Speed = 50

# Tello leader parameters
tello_leader = Tello()
# tello_leader_two = Tello("192.168.1.106")
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
    global Dist_travelled

    global waypoint_dist
    global Speed

    if Plan_one[waypoint_index]["motion"] == "forward":

        tello.send_rc_control(0, Speed, 0, 0)
        
        # tello.go_xyz_speed(waypoint_dist, 0, 0, Speed)

 
    elif Plan_one[waypoint_index]["motion"] == "backward":
        # time.sleep(1)
        # tello.send_command_without_return("go {x}, 0, 0, {speed}".format(x = waypoint_dist, speed = Speed))
        # time.sleep(1)
        tello.send_rc_control(0, -Speed, 0, 0)
        # tello.go_xyz_speed(waypoint_dist, 0, 0, Speed)

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

def leader_mission_pad_detection(tello, mid):
    # mission pad detection
    if tello.get_mission_pad_id() == mid:

        tello.go_xyz_speed_mid(0,0,-50, Speed,mid)
        tello.land()
        # time.sleep(20)
        tello.end()
    else:
        return

def leader_anchor_point(tello, mid, x):
    global Dist_travelled
    global waypoint_dist

    if tello.get_mission_pad_id() == mid:
        tello.go_xyz_speed_mid(x,0,100,Speed,mid)
        # tello_leader.move_down(50)

        Dist_travelled = waypoint_dist
    else:
        return

# Tello follower parameters
# tello_one = Tello("192.168.1.106")
# tello_two = Tello("192.168.1.108")
# # tello_three = Tello()

# tello_follower_dict = {
#     1 : tello_one,
#     2 : tello_two,
#     # 3 : tello_three
# }

# frame_read = []

def follower_connect():
    number_of_followers = len(tello_follower_dict)

    for follower in range(number_of_followers):
        tello_follower_dict[follower+1].connect()

def follower_takeoff():
    number_of_followers = len(tello_follower_dict)

    for follower in range(number_of_followers):
        tello_follower_dict[follower+1].send_command_without_return("takeoff") # if wait for return, have to wait for everybody
        time.sleep(1)

def follower_stop():
    number_of_followers = len(tello_follower_dict)

    for follower in range(number_of_followers):
        tello_follower_dict[follower+1].send_command_without_return('stop')
        time.sleep(1)

def follower_movement():
    global Land_Flag

    number_of_followers = len(tello_follower_dict)

    for follower in range(number_of_followers):

        if Land_Flag & land_Flag_mask["Drone {}".format(follower + 1)]:
            continue
        else:
            time.sleep(0.5)
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
                time.sleep(1)
                follower_stop()

                # tello.send_command_without_return(f"go 0, 0, -50, {Speed}, 1")
                tello.go_xyz_speed_mid(0,0,-50, Speed,1)
                tello.land()
                # time.sleep(20)
                tello.end()

                Land_Flag += land_Flag_mask["Drone {}".format(follower + 1)]

                flight_motion(tello_leader)
                follower_movement()
                prev_timing = time.time()
            else:
                continue

# for testing only. To be deleted
def pseudo_follower_anchor_point():
    global Land_Flag
    global Dist_travelled
    global waypoint_dist
    number_of_followers = len(tello_follower_dict)

    for follower in range(number_of_followers):

        if Land_Flag & land_Flag_mask["Drone {}".format(follower + 1)]:
            continue
        else:
            if tello_follower_dict[follower+1].get_mission_pad_id() == 3:
                tello_follower_dict[follower+1].go_xyz_speed_mid(0,0,100,Speed,3)
                # tello_follower_dict[follower+1].move_down(50)

                Dist_travelled = waypoint_dist
            else:
                return

# Main code starts here #
tello_leader.connect()
# tello_leader_two.connect()
# follower_connect()

# follower_takeoff()
tello_leader.takeoff()
# tello_leader_two.takeoff()
# tello_leader_two.send_rc_control(0,0,0,0)
time.sleep(2)

for waypoint_index in range(NO_OF_WAYPOINTS):

    waypoint_dist = pixels_To_cm(Plan_one[waypoint_index]["distance"])

    flight_motion(tello_leader)
    # flight_motion(tello_leader_two)
    # follower_movement()

    prev_timing = time.time()

    while Dist_travelled < waypoint_dist:
        # if Land_Flag == 4: # 11, all has landed
        #     leader_mission_pad_detection()

        # else:
        #     follower_mission_pad_detection()
        leader_mission_pad_detection(tello_leader, 2)
        # leader_mission_pad_detection(tello_leader_two, 2)

        current_timing = time.time()
        time_interval = current_timing - prev_timing
        Dist_travelled += Speed * time_interval
        prev_timing = current_timing
        # pseudo_follower_anchor_point()
    tello_leader.send_rc_control(0,0,0,0)
    # tello_leader_two.send_command_without_return('stop')
    # time.sleep(1)
    # follower_stop()
    # time.sleep(3)
    # leader_anchor_point(tello_leader_two, 3, -50)
    leader_anchor_point(tello_leader, 3, 50)
    failSafe(tello_leader)
    time.sleep(2)
    Dist_travelled = 0.0

tello_leader.land()
# tello_leader_two.land()
tello_leader.end()
# tello_leader_two.end()

