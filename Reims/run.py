
# Imports
import os
import traci
import time
import math

# Utils function for rainbow
def get_rainbow_color():
	current = time.time()
	red = int((1 + math.sin(current)) * 127)
	green = int((1 + math.sin(current + 2)) * 127)
	blue = int((1 + math.sin(current + 4)) * 127)
	return (red, green, blue, 255)

# Start sumo
sumo_command = ["sumo-gui", "-c", "osm.sumocfg"]
traci.start(sumo_command)

# While there are vehicles in the simulation
while traci.simulation.getMinExpectedNumber() > 0:

	# Make a step
	traci.simulationStep()

	# Change color of every vehicles
	for vehicle_id in traci.vehicle.getIDList():
		traci.vehicle.setColor(vehicle_id, get_rainbow_color())




