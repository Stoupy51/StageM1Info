
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

# Constants
FOG_COLOR: tuple = (255, 0, 0, 255)
FOG_SIZE: int = 50
FOG_SHAPE: list[tuple] = [(0, 0), (0, FOG_SIZE), (FOG_SIZE, FOG_SIZE), (FOG_SIZE, 0)]
FOG_LINK_BANDWIDTH_RANGE: tuple[int,int,int] = (100, 1000, 10)
NB_FOG_NODES: int = 10
RANDOM_DIVIDER: int = 3
PLOT_INTERVAL: int = 1

def run_simulation(simulation_name: str, assign_mode: AssignMode, sumo_config: str, visual_center: tuple[int,int], seed: int = 0, debug_perf: bool = False) -> None:
	""" Run a simulation with the given parameters\n
	It will generates multiple plots such as the QoS over time, the fog nodes resources, etc.\n
	Args:
		simulation_name	(str):			Name of the simulation (used for the output files)
		assign_mode		(AssignMode):	Assign mode to use for the simulation steps
		sumo_config		(str):			Sumo configuration file to use
		seed			(int):			Seed to use for the simulation (default: 0)
		debug_perf		(bool):			Whether to debug the performance of the simulation (default: False)
	"""

	# Start sumo
	random.seed(seed)
	traci.start(["sumo-gui", "-c", sumo_config, "--seed", str(seed)])

	# Calculated constants
	(MIN_X, MIN_Y), (MAX_X, MAX_Y) = traci.simulation.getNetBoundary()
	OFFSET_X = int((MAX_X - MIN_X) / 2)
	OFFSET_Y = int((MAX_Y - MIN_Y) / 2)

	# Add multiple fog nodes at random positions
	fog_list: set[FogNode] = FogNode.random_nodes(NB_FOG_NODES, (OFFSET_X, OFFSET_Y), visual_center, RANDOM_DIVIDER, FOG_SHAPE, FOG_COLOR)

	# Setup random resources for fog nodes
	for fog_node in fog_list:
		fog_node.set_resources(Resource.random())
		fog_node.set_neighbours(nodes = fog_list, bandwidth_range = FOG_LINK_BANDWIDTH_RANGE)
		info(fog_node)
	
	# Evaluations
	evaluations: list[float] = []

	# While there are vehicles in the simulation
	step: int = 0
	while traci.simulation.getMinExpectedNumber() > 0:

		# Make a step in the simulation
		traci.simulationStep()

		# Algorithm step
		time_taken = solution_algorithm_step(fog_list, assign_mode)
		if debug_perf:
			debug(f"Time taken for step #{step}: {time_taken:.5f}s")

		# Evaluate the network
		evaluation = Evaluator.calculate_qos(fog_list)
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
			if debug_perf:
				debug(f"Plotting time: {time_taken:.5f}s")

		# Increment the step
		step += 1

	# Make folder if it doesn't exist
	import os
	if not os.path.exists(simulation_name):
		os.mkdir(simulation_name)

	# Save the last plot
	path: str = f"{simulation_name}/task_states_evaluation.png"
	plt.savefig(path)
	info(f"Plot saved in '{path}'")

	# Save in a JSON file the evaluations
	import json
	path: str = f"{simulation_name}/task_states_evaluation.json"
	with open(path, "w") as file:
		file.write(json.dumps(evaluations))
	info(f"Evaluations saved in '{path}'")

	# Additional values in "additional.txt"
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
	path: str = f"{simulation_name}/additional.txt"
	with open(path, "w") as file:
		file.write(content)
	info(f"Analysis saved in '{path}'")

	# Close the simulation
	traci.close()
	info("Simulation closed")


