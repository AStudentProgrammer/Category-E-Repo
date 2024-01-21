import time
import json

json_File = open("Plan 1", "r")
sample_load_file = json.load(json_File)
print(sample_load_file[0]["motion"])
print(sample_load_file[0]["distance"])
