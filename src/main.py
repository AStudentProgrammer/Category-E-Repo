# Set simple swarm code for now
from djitellopy import TelloSwarm
import time

# Collated list of Tellos to connect to
swarm = TelloSwarm.fromIps([
    "192.168.1.101",
    "192.168.1.102",
    "192.168.1.103",
    "192.168.1.104",
    "192.168.1.105",
    "192.168.1.106",
    "192.168.1.107",
    "192.168.1.108",
    "192.168.1.109",
    "192.168.1.110",
    "192.168.1.111",
    "192.168.1.112",
    "192.168.1.113",
    "192.168.1.114",
    "192.168.1.115",
    "192.168.1.116"
])

# def battery_checker(drone_number, tello):
#     tello.query_battery()

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
    time.sleep(5)
    tello.go_xyz_speed(25, 0, 0, 25)
    time.sleep(5)
    tello.go_xyz_speed(0, 25, 0, 25)
    time.sleep(5)
    tello.go_xyz_speed(-25, 0, 0, 25)
    time.sleep(5)

# main code
swarm.connect()
swarm.takeoff()
swarm.parallel(square_movement)
swarm.land()

swarm.end()