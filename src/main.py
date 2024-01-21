import time
import json

json_File = open("Plan 1", "r")
sample_load_file = json.load(json_File)
print(sample_load_file[0]["motion"])
print(sample_load_file[0]["distance"]) # in pixels

def pixels_To_cm(pixels):
    
    real_map = 2000 # 2000cm
    picture_map = 500 # 500 pixels

    cm = (real_map/picture_map) * pixels
    return cm