import time
from djitellopy import TelloSwarm
import json
# from queue import Queue
import keyboard

# Simulate the dataset retrieved from json
set_of_number = {
    # x, y, z, speed, yaw, mid1(unused), mid2(unused)
    "Set 1" : (0, -100, 50, 25, 90, 1, 2),
    "Set 2" : (100, -100, 50, 25, 90, 1, 2),
    "Set 3" : (100, 0, 50, 25, 90, 1, 2),
    "Set 4" : (0, 0, 50, 25, 90, 1, 2),
}

json_File_one = open("Plan 1", "r")
Plan_one = json.load(json_File_one)

# Collated list of Tellos to connect to
swarm = TelloSwarm.fromIps([
    "192.168.1.102",
    # "192.168.1.103",
])

NO_OF_WAYPOINTS = len(Plan_one)

# Flags
Land_Flag = 0 # 0000 0000 0000 0000

# leader_values = Queue(maxsize=1)

def pixels_To_cm(pixels):
    
    real_map = 2000 # 2000cm
    picture_map = 500 # 500 pixels

    cm = (real_map/picture_map) * pixels
    return int(cm)

def battery_checker(drone_number, tello):
    tello.query_battery()

def distance_checker(drone_number, tello):
    distance = 0.0
    speed = 0.0
    prev_time = time.time()

    while True:
        acceleration_x = tello.get_acceleration_x()
        if (acceleration_x < 100.0) and (acceleration_x > -100.0):
            acceleration_x = 0.0
        else:
            acceleration_x = tello.get_acceleration_x()
        current_time = time.time()
        time_increment = current_time - prev_time
        speed += acceleration_x * time_increment
        distance += speed * time_increment
        print(distance)
        prev_time = current_time

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

def failsafe(drone_number, tello):
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

def mission_pad_detection(drone_number, tello):
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



def move_with_keyboard(drone_number, tello):
    Takeoff_flag = False

    while True:
        if keyboard.is_pressed('t'):
            tello.takeoff()
            Takeoff_flag = True

        elif keyboard.is_pressed('l'):
            tello.land()
            Takeoff_flag = False

        elif Takeoff_flag:
            if keyboard.is_pressed('up'):
                tello.move_forward(20)

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

                else:
                    continue

            elif keyboard.is_pressed('down'):
                tello.move_back(20)
          
            elif keyboard.is_pressed('left'):
                tello.move_left(20)

            elif keyboard.is_pressed('right'):
                tello.move_right(20)

            else:
                continue

# main code
swarm.connect()
# swarm.parallel(lambda drone_number, tello : tello.set_mission_pad_detection_direction(2))
# swarm.takeoff()
# swarm.parallel(distance_checker)
# swarm.land()

swarm.end()

