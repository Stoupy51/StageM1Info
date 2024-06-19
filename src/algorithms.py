
# Imports
from src.utils import *
from src.print import *
from src.resources import Resource
from src.vehicle import Vehicle
from src.task import Task, TaskStates
from src.fog import FogNode
from config import *
import numpy as np
import random
import traci

# Evaluation of the network
def evaluate_network(fogs: set[FogNode]) -> float:
	""" Evaluate the network by calculating the Quality of Service (QoS)\n
	The QoS is defined by:
	- The maximization of the number of completed tasks
	- The minimization of Fog nodes usage
	- The minimization of Fog nodes links load (how used)
	Args:
		fogs	(set[FogNode]):	Set of fog nodes
	Returns:
		float: Quality of Service (QoS) = k1*completed_tasks_ratio - k2*nodes_usage - k3*links_load
	"""
	total_tasks: list[Task] = [task for vehicle in Vehicle.vehicles for task in vehicle.tasks]
	nb_tasks: int = len(total_tasks) if len(total_tasks) > 0 else 1
	completed_tasks_ratio: int = sum([1 for task in total_tasks if task.state == TaskStates.COMPLETED]) / nb_tasks
	nodes_usage: float = sum([fog.get_usage() for fog in fogs])
	links_load: float = sum([fog.get_links_load() for fog in fogs])

	# Calculate the QoS and return it
	qos: float = K1 * completed_tasks_ratio - K2 * nodes_usage - K3 * links_load
	return qos

def get_usage_variance(fogs: set[FogNode]) -> float:
	""" Get the variance of the fog nodes usage
	Args:
		fogs	(set[FogNode]):	Set of fog nodes
	Returns:
		float: Variance of the fog nodes usage
	"""
	usage: list[Resource] = [fog.used_resources / fog.resources for fog in fogs]
	cpu_usage: list[float] = [u.cpu for u in usage]
	ram_usage: list[float] = [u.ram for u in usage]
	cpu_variance: float = np.var(cpu_usage)
	ram_variance: float = np.var(ram_usage)
	return (cpu_variance + ram_variance) / 2


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
			for task in vehicle.tasks:
				if task.state == TaskStates.PENDING:
					task.resolving_time = random.randint(1, 5)	# Random resolving time between 1s and 5s
	
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

