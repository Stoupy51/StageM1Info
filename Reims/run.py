
# Imports
from src.functions import *
import os
import traci

# Constants
SUMO_CONFIG: str = "osm.sumocfg"
FOG_COLOR: tuple = (255, 0, 0, 255)
FOG_SIZE: int = 50
FOG_SHAPE: list[tuple] = [(0, 0), (0, FOG_SIZE), (FOG_SIZE, FOG_SIZE), (FOG_SIZE, 0)]
NB_FOG_NODES: int = 10
RANDOM_DIVIDER: int = 3

# Start sumo
sumo_command: list = ["sumo-gui", "-c", SUMO_CONFIG]
traci.start(sumo_command)

# Calculated constants
(MIN_X, MIN_Y), (MAX_X, MAX_Y) = traci.simulation.getNetBoundary()
OFFSET_X = int((MAX_X - MIN_X) / 2)
OFFSET_Y = int((MAX_Y - MIN_Y) / 2)
VISUAL_CENTER: tuple[int,int] = (1200, 1600)

# Add multiple fog nodes at random positions
fog_list: list = add_random_nodes(NB_FOG_NODES, (OFFSET_X, OFFSET_Y), VISUAL_CENTER, RANDOM_DIVIDER, FOG_SHAPE, FOG_COLOR)

# While there are vehicles in the simulation
while traci.simulation.getMinExpectedNumber() > 0:

	# Make a step
	traci.simulationStep()

	# Change color of every vehicles
	for vehicle_id in traci.vehicle.getIDList():
		traci.vehicle.setColor(vehicle_id, get_rainbow_color())
	
	# Change color of each fog
	for fog_id, position in fog_list:
		traci.polygon.setColor(fog_id, get_rainbow_color(0.25))

