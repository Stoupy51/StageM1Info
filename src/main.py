
# Imports
from src.algorithms import *
from src.fog import FogNode
from src.resources import Resource
from src.utils import *
from src.print import *
from src.evaluations import *
from config import *
from matplotlib import pyplot as plt
import traci
import random
import time

def run_simulation(
		simulation_name: str,
		assign_mode: AssignMode,
		sumo_config: str,
		visual_center: tuple[int,int],
		seed: int = 0,
		debug_perf: bool = False,
		auto_start: bool = True,
		auto_quit: bool = True,
		open_gui: bool = True,
		fog_resources: tuple = Resource.HIGH_RANDOM_RESOURCE_ARGS
	) -> dict:
	""" Run a simulation with the given parameters\n
	It will generates multiple plots such as the QoS over time, the fog nodes resources, etc.\n
	Args:
		simulation_name	(str):			Name of the simulation (used for the output files)
		assign_mode		(AssignMode):	Assign mode to use for the simulation steps
		sumo_config		(str):			Sumo configuration file to use
		seed			(int):			Seed to use for the simulation (default: 0)
		debug_perf		(bool):			Whether to debug the performance of the simulation (default: False)
		auto_start		(bool):			Whether to start the simulation automatically (default: True)	(adding '--start')
		auto_quit		(bool):			Whether to quit the simulation automatically (default: True)	(adding '--quit-on-end')
		open_gui		(bool):			Whether to run traci command "sumo-gui" or "sumo" (default: True)
		fog_resources	(tuple):		Resources to use for the fog nodes (default: Resource.HIGH_RANDOM_RESOURCE_ARGS)
	Returns:
		dict: Dictionnary of evaluations over time
	"""

	# Start sumo
	random.seed(seed)
	executable: str = "sumo-gui" if open_gui else "sumo"
	command: list[str] = [executable, "-c", sumo_config, "--seed", str(seed)]
	if auto_start:
		command.append("--start")
	if auto_quit:
		command.append("--quit-on-end")
	simplified_name: str = simulation_name.split("/")[-1]
	traci.start(command, label = simplified_name)

	# Calculated constants
	(MIN_X, MIN_Y), (MAX_X, MAX_Y) = traci.simulation.getNetBoundary()
	OFFSET_X = int((MAX_X - MIN_X) / 2)
	OFFSET_Y = int((MAX_Y - MIN_Y) / 2)

	# Add multiple fog nodes at random positions
	fog_list: set[FogNode] = FogNode.random_nodes(NB_FOG_NODES, (OFFSET_X, OFFSET_Y), visual_center, RANDOM_DIVIDER, FOG_SHAPE, FOG_COLOR)

	# Setup random resources for fog nodes
	fog_link_bandwidth_range: tuple[int,int,int] = tuple([x // 5 for x in fog_resources[0]])	# Bandwidth = (cpu resource / 5) to scale with it.
	for fog_node in fog_list:
		fog_node.set_resources(Resource.random(*fog_resources))
		fog_node.set_neighbours(nodes = fog_list, bandwidth_range = fog_link_bandwidth_range)
		info(fog_node)
	
	# Evaluations
	qos_history: list[float] = []
	allocated_tasks_history: list[int] = []
	nodes_usage_history: list[float] = []
	links_load_history: list[float] = []

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
		qos = Evaluator.calculate_qos(fog_list)
		allocated_tasks, nodes_usage, links_load = Evaluator.get_splitted_qos(fog_list)
		qos_history.append(qos)
		allocated_tasks_history.append(allocated_tasks)
		nodes_usage_history.append(nodes_usage)
		links_load_history.append(links_load)

		# Make a plot with all evaluations
		if step % PLOT_INTERVAL == 0:
			time_taken = time.perf_counter()
			plt.clf()
			plt.plot(qos_history)
			plt.title(f"Quality of Service (QoS) over time - {simplified_name}")
			plt.xlabel("Simulation Step")
			plt.ylabel("Quality of Service (QoS)")
			plt.pause(0.0001)
			time_taken = time.perf_counter() - time_taken
			if debug_perf:
				debug(f"Plotting time: {time_taken:.5f}s")

		# Increment the step
		step += 1

	# Close the simulation
	traci.close()
	info("Simulation closed")

	# Prepeare the return dictionnary
	r_dict = {
		"folder": simulation_name,
		"name": simplified_name,
		"QoS Evaluations": qos_history,
		"Allocated Tasks": allocated_tasks_history,
		"Nodes Usage": nodes_usage_history,
		"Links Load": links_load_history,
	}

	# Add cumulative arrays
	r_dict["Cumulative QoS"] = [sum(qos_history[:i]) for i in range(len(qos_history))]
	r_dict["Cumulative Allocated Tasks"] = [sum(allocated_tasks_history[:i]) for i in range(len(allocated_tasks_history))]
	r_dict["Cumulative Nodes Usage"] = [sum(nodes_usage_history[:i]) for i in range(len(nodes_usage_history))]
	r_dict["Cumulative Links Load"] = [sum(links_load_history[:i]) for i in range(len(links_load_history))]

	# Return the dict
	return r_dict

