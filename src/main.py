import time
from djitellopy import Tello
import json
import numpy as np
import cv2

json_File_one = open("Plan 1", "r")
Plan_one = json.load(json_File_one)

def waypoint_flight(drone_number, tello):

    # global leader_values
    # leader_values.put('a')

    number_of_waypoints = len(Plan_one)

    for waypoint_index in range(number_of_waypoints):

        if Plan_one[waypoint_index]["motion"] == "forward":
            distance = pixels_To_cm(Plan_one[waypoint_index]["distance"])
            # tello.move_forward(distance)
            tello.go_xyz_speed(distance, 0, 0, 50)

        elif Plan_one[waypoint_index]["motion"] == "backward":
            distance = - pixels_To_cm(Plan_one[waypoint_index]["distance"])
            # tello.move_backward(distance)
            tello.go_xyz_speed(distance, 0, 0, 50)

        elif Plan_one[waypoint_index]["motion"] == "rotate_right":
            tello.rotate_clockwise(Plan_one[waypoint_index]["distance"])

        elif Plan_one[waypoint_index]["motion"] == "rotate_left":
            tello.rotate_counter_clockwise(Plan_one[waypoint_index]["distance"])

        swarm.sync()  

        # Safety measure func
        # register tof value as int
        tof_value = tello.send_read_command("EXT tof?") # its in string initially
        tof_value = int(tof_value[4:])

        while tof_value < 1000: # less than 1000mm
            tello.go_xyz_speed(-20, 0, 0, 10) # go back by 10cm
            swarm.sync()

            # reregister tof value as int
            tof_value = tello.send_read_command("EXT tof?") # its in string initially
            tof_value = int(tof_value[4:])
        # Safety measure func

        # mission pad detection
        if tello.get_mission_pad_id() != -1:

            m_id = 1

            tello.send_control_command("stop") # hover
            swarm.sync()

            while m_id <= 4:
                # Link m_id 1 to drone 1, and so on
                # drone index starts from 0, so 
                if drone_number == (m_id - 1):
                    tello.go_xyz_speed(0, 0, 25, 0) # lower altitude first
                    tello.go_xyz_speed_mid(0, 50, 25, 50, m_id) # land 50cm to the left of marker
                    if tello.get_mission_pad_id() == m_id:
                        tello.land()
                    else:
                        tello.go_xyz_speed(0, 0, 50, 0)

                tello.send_keepalive()
                m_id += 1

tello = Tello()
tello.connect()

tello.streamoff()
tello.streamon()
frame_read = tello.get_frame_read()

# tello.takeoff()

while True:

    img = frame_read.frame
    cv2.imshow("drone", img)

    key = cv2.waitKey(1) & 0xff
    if key == 27: # ESC
        break

