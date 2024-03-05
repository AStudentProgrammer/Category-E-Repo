import time
from djitellopy import Tello
import json
import numpy as np
import cv2

# Tello leader parameters
tello_leader = Tello()

# Main code starts here #
tello_leader.connect()
tello_leader.takeoff()
tello_leader.land()
tello_leader.end()

