
# Imports
from src.vehicle import Vehicle
from src.task import Task, TaskStates
from src.fog import FogNode
from config import *

# Evaluation of the network
def evaluate_network(fogs: set[FogNode]) -> float:
	""" Evaluate the network by calculating the Quality of Service (QoS)\n
	The QoS is defined by:
	- The maximization of the number of allocated tasks
	- The minimization of Fog nodes usage
	- The minimization of Fog nodes links load (how used)
	Args:
		fogs	(set[FogNode]):	Set of fog nodes
	Returns:
		float: Quality of Service (QoS) = k1*allocated_tasks - k2*nodes_usage - k3*links_load
	"""
	# total_tasks: list[Task] = [task for vehicle in Vehicle.vehicles for task in vehicle.tasks]
	# nb_tasks: int = len(total_tasks) if len(total_tasks) > 0 else 1
	allocated_tasks: int = len(Task.all_tasks[TaskStates.IN_PROGRESS])
	nodes_usage: float = sum([fog.get_usage() for fog in fogs])
	links_load: float = sum([fog.get_links_load() for fog in fogs])

	# Calculate the QoS and return it
	qos: float = K1 * allocated_tasks - K2 * nodes_usage - K3 * links_load
	return qos

