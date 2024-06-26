
# Imports
from src.algorithms import *
from src.fog import FogNode
from src.resources import Resource
from src.utils import *
from src.print import *
from src.evaluations import *
from matplotlib import pyplot as plt
import traci
import random
import time
random.seed(0)

# Constants
SUMO_CONFIG: str = "Reims/osm.sumocfg"
VISUAL_CENTER: tuple[int,int] = (1200, 1600)
FOG_COLOR: tuple = (255, 0, 0, 255)
FOG_SIZE: int = 50
FOG_SHAPE: list[tuple] = [(0, 0), (0, FOG_SIZE), (FOG_SIZE, FOG_SIZE), (FOG_SIZE, 0)]
FOG_LINK_BANDWIDTH_RANGE: tuple[int,int,int] = (100, 1000, 10)
NB_FOG_NODES: int = 10
RANDOM_DIVIDER: int = 3
PLOT_INTERVAL: int = 1
DEBUG_PERF: bool = False

# Start sumo
traci.start(["sumo-gui", "-c", SUMO_CONFIG])

# Calculated constants
(MIN_X, MIN_Y), (MAX_X, MAX_Y) = traci.simulation.getNetBoundary()
OFFSET_X = int((MAX_X - MIN_X) / 2)
OFFSET_Y = int((MAX_Y - MIN_Y) / 2)

# Add multiple fog nodes at random positions
fog_list: set[FogNode] = FogNode.random_nodes(NB_FOG_NODES, (OFFSET_X, OFFSET_Y), VISUAL_CENTER, RANDOM_DIVIDER, FOG_SHAPE, FOG_COLOR)

# Setup random resources for fog nodes
for fog_node in fog_list:
	fog_node.set_resources(Resource.random())
	fog_node.set_neighbours(nodes = fog_list, bandwidth_range = FOG_LINK_BANDWIDTH_RANGE)
	debug(fog_node)

# Evaluations
evaluations: list[float] = []

# While there are vehicles in the simulation
step: int = 0
while traci.simulation.getMinExpectedNumber() > 0:

	# Make a step in the simulation
	traci.simulationStep()

	# Algorithm step
	time_taken = solution_algorithm_step(fog_list)
	if DEBUG_PERF:
		debug(f"Time taken for step #{step}: {time_taken:.5f}s")

	# Evaluate the network
	evaluation = evaluate_network(fog_list)
	evaluations.append(evaluation)

	# Make a plot with all evaluations
	if step % PLOT_INTERVAL == 0:
		time_taken = time.perf_counter()
		plt.clf()
		plt.plot(evaluations)
		plt.title("Quality of Service (QoS) over time")
		plt.xlabel("Simulation Step")
		plt.ylabel("Quality of Service (QoS)")
		plt.pause(0.0001)
		time_taken = time.perf_counter() - time_taken
		if DEBUG_PERF:
			debug(f"Plotting time: {time_taken:.5f}s")

	# Increment the step
	step += 1


# Save the last plot
plt.savefig("task_states_evaluation.png")
info("Plot saved in 'task_states_evaluation.png'")


# Save in a JSON file the evaluations
import json
with open("task_states_evaluation.json", "w") as file:
	file.write(json.dumps(evaluations, indent = '\t'))
info("Evaluations saved in 'task_states_evaluation.json'")

# Analyse values in "analyse.txt"
content = ""
total: int = sum([e for e in evaluations])
average: float = total / len(evaluations)
median: float = sorted([e for e in evaluations])[len(evaluations) // 2]
maximum: int = max([e for e in evaluations])
content += f"Quality of Service:\n"
content += f"\tTotal: {total}\n"
content += f"\tAverage: {average:.2f}\n"
content += f"\tMedian: {median}\n"
content += f"\tMaximum: {maximum}\n"
content += "\n"
with open("analyse.txt", "w") as file:
	file.write(content)
info("Analysis saved in 'analyse.txt'")

# Close the simulation
traci.close()
info("Simulation closed")

