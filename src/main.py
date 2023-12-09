# Set simple swarm code for now
from djitellopy import TelloSwarm
import time

# Collated list of Tellos to connect to
swarm = TelloSwarm.fromIps([
    "192.168.1.101",
    "192.168.1.102",
])

def battery_checker(drone, tello):
    tello.query_battery()

# main code
swarm.connect()
swarm.parallel(battery_checker)
time.sleep(10)
swarm.parallel(battery_checker)

swarm.end()