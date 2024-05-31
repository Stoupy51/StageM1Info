
# Imports
from src.functions import *
from src.print import *
import traci
import traci.exceptions

# Constants
SUMO_CONFIG: str = "osm.sumocfg"
VISUAL_CENTER: tuple[int,int] = (1200, 1600)
FOG_COLOR: tuple = (255, 0, 0, 255)
FOG_SIZE: int = 50
FOG_SHAPE: list[tuple] = [(0, 0), (0, FOG_SIZE), (FOG_SIZE, FOG_SIZE), (FOG_SIZE, 0)]
NB_FOG_NODES: int = 10
RANDOM_DIVIDER: int = 3

# Start sumo
traci.start(["sumo-gui", "-c", SUMO_CONFIG])

# Calculated constants
(MIN_X, MIN_Y), (MAX_X, MAX_Y) = traci.simulation.getNetBoundary()
OFFSET_X = int((MAX_X - MIN_X) / 2)
OFFSET_Y = int((MAX_Y - MIN_Y) / 2)

# Add multiple fog nodes at random positions
fog_list: list[FogNode] = add_random_nodes(NB_FOG_NODES, (OFFSET_X, OFFSET_Y), VISUAL_CENTER, RANDOM_DIVIDER, FOG_SHAPE, FOG_COLOR)

# Setup random resources for fog nodes
for fog_node in fog_list:
	cpu: int = random.randint(2, 8) * 25		# Percentage
	ram: int = random.randint(1, 16) * 1024		# MB
	fog_node.set_resources(Resources(cpu, ram))
	debug(fog_node)



# While there are vehicles in the simulation
while traci.simulation.getMinExpectedNumber() > 0:

	# Make a step
	traci.simulationStep()

	# Change color of every vehicles
	for vehicle_id in traci.vehicle.getIDList():
		traci.vehicle.setColor(vehicle_id, get_rainbow_color())
	
	# Change color of each fog
	for fog_node in fog_list:
		fog_node.set_color(get_rainbow_color(0.25))

