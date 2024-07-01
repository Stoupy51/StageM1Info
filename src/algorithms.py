
# Imports
from src.utils import *
from src.print import *
from src.resources import Resource
from src.vehicle import Vehicle
from src.task import Task, TaskStates
from src.fog import FogNode, FogNodesLink
from config import *
import numpy as np
import random
import traci

# Simple Algortihm
def simple_algorithm_step(fogs: set[FogNode]) -> float:
	""" Simple algorithm step. Here are the steps:
	- For each vehicle
	  - If no tasks, generate tasks
	  - For each not assigned task
	    - Ask the nearest fog node to resolve the task
		- If the fog node has enough resources, assign the task and send confirmation to the vehicle so it can change the task state
		- Else, a failure message is sent to the vehicle
	- For each fog node
	  - If tasks are assigned, progress them
	  - For each allocated task, send the result to the vehicle and remove the task

	Args:
		fogs	(set):	Set of fog nodes
	Returns:
		float: Time taken to progress the algorithm
	"""
	start_time: float = time.perf_counter()

	# Reset fog links charge
	if FogNode.reset_links_charges(fogs):
		print()	# Add a new line for better readability

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
		vehicle.assign_tasks(fogs)
	
	# Change fog color depending on their resources
	FogNode.color_usage(fogs)
	
	# For each fog node, progress the tasks
	for fog_node in fogs:
		fog_node.progress_tasks()
	
	# Return the time taken to progress the algorithm
	return time.perf_counter() - start_time



# Solution Algortihm
def solution_algorithm_step(fogs: set[FogNode], assign_mode: AssignMode) -> float:
	""" Solution algorithm step. Here are the steps:
	- For each vehicle
	  - If no tasks, generate tasks
	  - For each not assigned task
	    - Ask the nearest fog node to resolve the task
		- If the fog node is willing to accept (QoS), assign the task and send confirmation to the vehicle so it can change the task state
		- Else, the fog node will ask their neighbors to resolve the task
		- If no fog node can accept, a failure message is sent to the vehicle
	- For each fog node
	  - If tasks are assigned, progress them
	  - For each allocated task, send the result to the vehicle and remove the task

	Args:
		fogs		(set):			Set of fog nodes
		assign_mode	(AssignMode):	Configuration of how the tasks are assigned
	Returns:
		float: Time taken to progress the algorithm
	"""
	start_time: float = time.perf_counter()

	# Reset fog links charge
	if FogNode.reset_links_charges(fogs):
		print()	# Add a new line for better readability

	# Delete all vehicles that are not in the simulation anymore
	Vehicle.acknowledge_removed_vehicles()

	# Create all vehicles that are not created yet
	Vehicle.acknowledge_new_vehicles()
	
	# Generate tasks for each vehicle that has no tasks
	for vehicle in Vehicle.vehicles:
		if vehicle.not_finished_tasks == 0:
			Vehicle.generate_tasks(
				vehicle,
				nb_tasks = (1, 3),
				random_resource_args = Resource.LOW_RANDOM_RESOURCE_ARGS,
				random_resolution_times = (1, 5, 1),
				random_costs = Task.COST_RANGE
			)
	
	# For each not assigned task, ask the nearest fog node to resolve the task
	pending_vehicles: list[Vehicle] = [vehicle for vehicle in Vehicle.vehicles if vehicle.not_finished_tasks > 0]
	for vehicle in pending_vehicles:
		vehicle.assign_tasks(fogs, assign_mode)
	
	# Change fog color depending on their resources
	FogNode.color_usage(fogs)
	
	# For each fog node, progress the tasks
	for fog_node in fogs:
		fog_node.progress_tasks()
	
	# Return the time taken to progress the algorithm
	return time.perf_counter() - start_time

