
# Imports
from src.task import Task, TaskStates
from src.vehicle import Vehicle
from src.fog import FogNode
from config import *
import numpy as np

# Evaluation of the network
class Evaluator():

	@staticmethod
	def calculate_qos(fogs: set[FogNode]) -> float:
		""" Evaluate the network by calculating the Quality of Service (QoS)\n
		The QoS is defined by:
		- The maximization of the number of allocated tasks per vehicle
		- The minimization of Fog nodes usage
		- The minimization of Fog nodes links load (how used)
		Args:
			fogs	(set[FogNode]):	Set of fog nodes
		Returns:
			float: Quality of Service (QoS) = k1*allocated_tasks - k2*nodes_usage - k3*links_load
		"""
		allocated_tasks: float = len(Task.all_tasks[TaskStates.IN_PROGRESS]) / len(Vehicle.vehicles) if len(Vehicle.vehicles) > 0 else 0
		nodes_usage: float = np.var([fog.get_usage() for fog in fogs])
		links_load: float = np.var([fog.get_links_load() for fog in fogs])

		# Calculate the QoS and return it
		return (K1 * allocated_tasks) - (K2 * nodes_usage) - (K3 * links_load)

	@staticmethod
	def get_eval_parameters(fogs: set[FogNode]) -> tuple[float]:
		""" Returns parameters for the evaluation of the network\n
		Args:
			fogs	(set[FogNode]):	Set of fog nodes
		Returns:
			tuple[float]: Allocated tasks, nodes usage, links load, completed tasks, pending tasks, failed tasks, total tasks
		"""
		# QoS
		allocated_tasks: float = len(Task.all_tasks[TaskStates.IN_PROGRESS]) / len(Vehicle.vehicles) if len(Vehicle.vehicles) > 0 else 0
		nodes_usage: float = np.var([fog.get_usage() for fog in fogs])
		links_load: float = np.var([fog.get_links_load() for fog in fogs])

		# Other
		completed_tasks: int = len(Task.all_tasks[TaskStates.COMPLETED])
		pending_tasks: int = len(Task.all_tasks[TaskStates.PENDING])
		failed_tasks: int = len(Task.all_tasks[TaskStates.FAILED])
		total_tasks: int = sum([len(x) for x in Task.all_tasks.values()])

		# Return everything
		return allocated_tasks, nodes_usage, links_load, completed_tasks, pending_tasks, failed_tasks, total_tasks

