
# Imports
from src.algorithms import simple_algorithm_step
from src.fog import FogNode, add_random_nodes
from src.resources import Resource
from src.task import Task
from src.utils import *
from src.print import *
from matplotlib import pyplot as plt
import traci
import random
random.seed(0)

# Constants
SUMO_CONFIG: str = "Reims/osm.sumocfg"
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
	fog_node.set_resources(Resource.random())
	debug(fog_node)



# While there are vehicles in the simulation
evaluations: list[list[int]] = []
while traci.simulation.getMinExpectedNumber() > 0:

	# Make a step in the simulation
	traci.simulationStep()

	# Simple algorithm step
	evaluation = simple_algorithm_step(fog_list)
	evaluations.append(evaluation)

	# Print evaluation
	debug(evaluation)

	# Make a plot with all evaluations
	plt.clf()
	plt.plot(evaluations)
	plt.legend(Task.STATES)
	plt.title("Task States Evaluation")
	plt.xlabel("Simulation Step")
	plt.ylabel("Number of Tasks")
	plt.pause(0.01)


