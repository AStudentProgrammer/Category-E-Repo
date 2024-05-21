import time
from djitellopy import Tello
import json
import numpy as np
import cv2

json_File_one = open("Plan 1", "r")
Plan_one = json.load(json_File_one)

tello_normal = Tello(host="192.168.1.105", vs_udp=11111)
tello_normal_six = Tello(host="192.168.1.106", vs_udp=11112)

tello_normal.connect()
tello_normal_six.connect()

tello_normal.send_command_with_return("port 8890 11111")
tello_normal_six.send_command_with_return("port 8890 11112")

tello_normal.streamoff()
tello_normal.streamon()

tello_normal_six.streamoff()
tello_normal_six.streamon()

frame_read = tello_normal.get_frame_read()
frame_read_six = tello_normal_six.get_frame_read()

# tello.takeoff()

while True:

    img = frame_read.frame
    img_six = frame_read_six.frame
    cv2.imshow("drone", img)
    cv2.imshow("drone 6 ", img_six)

    key = cv2.waitKey(1) & 0xff
    if key == 27: # ESC
        break

