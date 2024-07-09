
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

# Solution Algortihm
def solution_algorithm_step(fogs: set[FogNode], assign_mode: AssignMode) -> float:
	""" This function is called at each step of the simulation.\n
	Args:
		fogs		(set):			Set of fog nodes
		assign_mode	(AssignMode):	Configuration of how the tasks are assigned
	Returns:
		float: Time taken to progress the algorithm
	"""
	start_time: float = time.perf_counter()

	# Reset fog links charge
	FogNode.reset_links_charges(fogs, debug_msg = DEBUG_LINKS_CHARGES)
	
	# Delete all vehicles that are not in the simulation anymore and create new ones if any
	Vehicle.acknowledge_removed_vehicles()
	Vehicle.acknowledge_new_vehicles()

	# Vehicle routine
	for vehicle in Vehicle.vehicles:

		# If no tasks, generate tasks
		if vehicle.not_finished_tasks == 0:
			vehicle.generate_tasks()
		
		# If there are pending tasks, calculate distance to fogs and assign tasks
		if vehicle.not_finished_tasks > 0:
			vehicle.set_distance_to_fogs(fogs)
			vehicle.assign_tasks(assign_mode)
	
	# Change fog color depending on their resources
	FogNode.color_usage(fogs)
	
	# For each fog node, progress the tasks
	for fog_node in fogs:
		fog_node.progress_tasks()
	
	# Return the time taken to progress the algorithm
	return time.perf_counter() - start_time

