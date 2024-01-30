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
    # "192.168.10.1",
    # "192.168.1.102",
    # "192.168.1.103",
])

NO_OF_WAYPOINTS = len(Plan_one)

# Flags
Land_Flag = 0 # 0000 0000 0000 0000

# Drones shared variables/resources
Dist_travelled = 0.0
Speed = 20

land_Flag_mask = {
    "Drone 1" : 1,
    "Drone 2" : 2,
    "Drone 3" : 4,
    "Drone 4" : 8,
    "Drone 5" : 16,
    "Drone 6" : 32,
    "Drone 7" : 64,
    "Drone 8" : 128,
    "Drone 9" : 256,
    "Drone 10" : 512,
    "Drone 11" : 1024,
    "Drone 12" : 2048,
    "Drone 13" : 4096,
    "Drone 14" : 8192,
    "Drone 15" : 16384,
    "Drone 16" : 32768,
}

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

def hovering(drone_number, tello):

    global Land_Flag

    if Land_Flag & land_Flag_mask["Drone {}".format(drone_number + 1)]:
        swarm.sync()
    else:
        tello.send_control_command("stop")
        swarm.sync()

def new_mission_pad_detection(drone_number, tello):

    global Land_Flag
    global prev_timing

    if tello.get_mission_pad_id() != -1:
        m_id = tello.get_mission_pad_id()

        swarm.parallel(hovering)
        tello.go_xyz_speed(20, 20, 25, 20) # lower altitude first
        tello.go_xyz_speed_mid(20, 20, 25, 20, m_id) # land 50cm to the left of marker
        tello.land()
        tello.end()
        Land_Flag += land_Flag_mask["Drone {}".format(drone_number + 1)]

        # Repeat of main code
        swarm.parallel(flight_motion)
        prev_timing = time.time()
    else:
        return

def waypoint_flight(drone_number, tello):

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

def flight_motion(drone_number, tello):

    global Land_Flag
    global waypoint_index

    global Speed

    if Land_Flag & land_Flag_mask["Drone {}".format(drone_number + 1)]:
        return
    else:
        if Plan_one[waypoint_index]["motion"] == "forward":
            tello.send_rc_control(0, Speed, 0, 0)

        elif Plan_one[waypoint_index]["motion"] == "backward":
            tello.send_rc_control(0, -Speed, 0, 0)

        elif Plan_one[waypoint_index]["motion"] == "rotate_right":
            tello.rotate_clockwise(Plan_one[waypoint_index]["distance"])

        elif Plan_one[waypoint_index]["motion"] == "rotate_left":
            tello.rotate_counter_clockwise(Plan_one[waypoint_index]["distance"])     

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
                tello.send_rc_control(0, 20, 0, 0)

                # Safety measure func
                # register tof value as int
                tof_value = tello.send_read_command("EXT tof?") # its in string initially
                tof_value = int(tof_value[4:])

                while tof_value < 1000: # less than 1000mm
                    tello.send_rc_control(0, -20, 0, 0)
                    swarm.sync()

                    # reregister tof value as int
                    tof_value = tello.send_read_command("EXT tof?") # its in string initially
                    tof_value = int(tof_value[4:])
                # Safety measure func

                else:
                    continue

            elif keyboard.is_pressed('down'):
                tello.send_rc_control(0, -20, 0, 0)
          
            elif keyboard.is_pressed('left'):
                tello.move_left(20)

            elif keyboard.is_pressed('right'):
                tello.move_right(20)

            else:
                continue

# main code
swarm.connect()
swarm.parallel(lambda drone_number, tello : tello.set_mission_pad_detection_direction(2))
swarm.takeoff()
for waypoint_index in range(NO_OF_WAYPOINTS):

    waypoint_dist = pixels_To_cm(Plan_one[waypoint_index]["distance"])

    swarm.parallel(flight_motion)

    prev_timing = time.time()

    while Dist_travelled < waypoint_dist:
        swarm.sequential(new_mission_pad_detection)
        current_timing = time.time()
        time_interval = current_timing - prev_timing
        Dist_travelled += Speed * time_interval
        prev_timing = current_timing

    # swarm.parallel(failsafe)
    Dist_travelled = 0.0
    swarm.parallel(hovering)
    time.sleep(7)
    
# swarm.parallel(move_with_keyboard)
swarm.land()

swarm.end()

