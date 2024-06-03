
# Imports
from src.algorithms import evaluate_network, simple_algorithm_step
from src.fog import FogNode, add_random_nodes
from src.resources import Resource
from src.vehicle import Vehicle
from src.task import Task
from src.utils import *
from src.print import *
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
NB_FOG_NODES: int = 10
RANDOM_DIVIDER: int = 3
PLOT_INTERVAL: int = 10

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

# Evaluations filters
evaluations: list[list[int]] = []
filtered_evaluations: list[list[int]] = []
black_list = ["Completed", "Failed"]
filtered_tasks = [Task.STATES.index(state) for state in Task.STATES if state not in black_list]
legend = [state for state in Task.STATES if state not in black_list]

# While there are vehicles in the simulation
step: int = 0
while traci.simulation.getMinExpectedNumber() > 0:

	# Make a step in the simulation
	traci.simulationStep()

	# Simple algorithm step
	time_taken = simple_algorithm_step(fog_list)
	debug(f"Time taken for step #{step}: {time_taken:.5f}s")

	# Evaluate the network
	evaluation = evaluate_network()
	evaluations.append(evaluation)

	# Append the filtered evaluation
	filtered_evaluations.append([evaluation[i] for i in filtered_tasks])

	# Make a plot with all evaluations
	if step % PLOT_INTERVAL == 0:
		time_taken = time.time()
		plt.clf()
		plt.plot(filtered_evaluations)
		plt.legend(legend)
		plt.title("Task States Evaluation")
		plt.xlabel("Simulation Step")
		plt.ylabel("Number of Tasks per vehicle (%)")
		plt.pause(0.0001)
		time_taken = time.time() - time_taken
		warning(f"Time taken to plot: {time_taken:.5f}s")

	# Increment the step
	step += 1


# Save the last plot
plt.savefig("task_states_evaluation.png")

# Save in a JSON file the evaluations
import json
with open("task_states_evaluation.json", "w") as file:
	file.write(json.dumps(evaluations, indent = '\t'))


