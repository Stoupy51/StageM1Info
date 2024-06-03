
# Imports
from src.utils import *
from src.print import *
from src.resources import Resource
from src.vehicle import Vehicle
from src.task import Task, TaskStates
from src.fog import FogNode
import traci

# Get number of tasks per task state
def evaluate_network() -> list[int]:
	""" Evaluate the network by returning the number of tasks for each state
	Returns:
		list[int]: Number of tasks for each state
	"""
	all_tasks: list[Task] = [task for vehicle in Vehicle.vehicles for task in vehicle.tasks]
	nb_states: list[int] = [
		sum([1 for task in all_tasks if task.state == state])
		for state in TaskStates
	]

	if len(Vehicle.vehicles) == 0:
		return nb_states
	else:
		normalized: list[float] = [100 * (nb / len(Vehicle.vehicles)) for nb in nb_states]
		return normalized


# Simple Algortihm
def simple_algorithm_step(fogs: set[FogNode]) -> float:
	""" Simple algorithm step. Here are the steps:
	- For each vehicle
	  - If no tasks, generate tasks
	  - For each not assigned task
	    - Ask the nearest fog node to resolve the task
		- If the fog node has enough resources, assign the task and send confirmation to the vehicle so it can change the task state
		- Else, the fog node will ask their neighbors to resolve the task
		- If no fog node can resolve the task, a failure message is sent to the vehicle
	- For each fog node
	  - If tasks are assigned, progress them
	  - For each completed task, send the result to the vehicle and remove the task

	Args:
		fogs	(set):	Set of fog nodes
	Returns:
		float: Time taken to progress the algorithm
	"""
	start_time: float = time.perf_counter()

	# Delete all vehicles that are not in the simulation anymore
	Vehicle.acknowledge_removed_vehicles()

	# Create all vehicles that are not created yet
	Vehicle.acknowledge_new_vehicles()
	
	# Generate tasks for each vehicle that has no tasks
	for vehicle in Vehicle.vehicles:
		if vehicle.not_finished_tasks == 0:
			Vehicle.generate_tasks(vehicle, nb_tasks = (1, 3), random_resource_args = Resource.LOW_RANDOM_RESOURCE_ARGS)
	
	# For each not assigned task, ask the nearest fog node to resolve the task
	pending_vehicles: list[Vehicle] = [vehicle for vehicle in Vehicle.vehicles if vehicle.not_finished_tasks > 0]
	for vehicle in pending_vehicles:
		vehicle.assign_tasks_to_nearest_fog(fogs)
	
	# Change fog color depending on their resources
	FogNode.color_usage(fogs)
	
	# For each fog node, progress the tasks
	for fog_node in fogs:
		fog_node.progress_tasks()
	
	# Return the time taken to progress the algorithm
	return time.perf_counter() - start_time

