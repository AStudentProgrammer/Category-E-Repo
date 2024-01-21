import time
import json

json_File = open("waypoint.json", "r")
sample_load_file = json.load(json_File)
print(sample_load_file["wp"])
