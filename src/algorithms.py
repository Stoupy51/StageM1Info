
# Imports
from src.utils import *
from src.print import *
from src.resources import Resource
from src.vehicle import Vehicle
from src.task import Task
from src.fog import FogNode
import traci

# Get number of tasks per task state
def evaluate_network() -> list[int]:
	""" Evaluate the network by returning the number of tasks for each state
	Returns:
		list[int]: Number of tasks for each state
	"""
	vehicles: list[Vehicle] = Vehicle.vehicles
	nb_states: list[int] = [0 for _ in Task.STATES]
	for vehicle in vehicles:
		for task in vehicle.tasks:
			nb_states[Task.STATES.index(task.state)] += 1
	
	normalized: list[float] = [100 * (nb / len(vehicles)) for nb in nb_states]
	return normalized


# Simple Algortihm
def simple_algorithm_step(fog_list: list[FogNode]) -> float:
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
		fog_list	(list):	List of fog nodes
	Returns:
		float: Time taken to progress the algorithm
	"""
	start_time: float = time.time()

	# Delete all vehicles that are not in the simulation anymore
	for vehicle in Vehicle.vehicles:
		try:
			traci.vehicle.getPosition(vehicle.vehicle_id)
		except:
			Vehicle.vehicles.remove(vehicle)

	# Create all vehicles that are not created yet
	for vehicle_id in traci.vehicle.getIDList():
		if Vehicle.get_vehicle_from_id(vehicle_id) is None:
			Vehicle(vehicle_id)
	
	# Generate tasks for each vehicle that has no tasks
	for vehicle in Vehicle.vehicles:
		not_completed_tasks: list[Task] = [task for task in vehicle.tasks if task.state != Task.STATES[2]]
		if len(not_completed_tasks) == 0:
			Vehicle.generate_tasks(vehicle)
	
	# For each not assigned task, ask the nearest fog node to resolve the task
	for vehicle in Vehicle.vehicles:
		try:
			for task in vehicle.tasks:
				if task.state == Task.STATES[0]:
					nearest_fog: FogNode = vehicle.get_nearest_fog(fog_list)
					is_assigned: bool = nearest_fog.assign_task(vehicle, task)
					if is_assigned:
						task.state = Task.STATES[1]
		except Exception as e:
			warning(f"Error while assigning task to the nearest fog node: {e}")
	
	# For each fog node, progress the tasks
	for fog_node in fog_list:
		fog_node.progress_tasks()
	
	# Return the time taken to progress the algorithm
	return time.time() - start_time

