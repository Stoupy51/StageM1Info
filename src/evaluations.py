
# Imports
from src.task import Task, TaskStates
from src.vehicle import Vehicle
from src.fog import FogNode
from config import *
import numpy as np
import traci
import time

# Evaluation of the network
class Evaluator():

	@staticmethod
	def calculate_qos(fogs: set[FogNode]) -> float:
		""" Evaluate the network by calculating the Quality of Service (QoS)\n
		The QoS is defined by:
		- The maximization of the number of allocated tasks per vehicle
		- The minimization of Fog nodes usage
		- The minimization of Fog nodes links load (how used)
		- The minimization of the distance of the tasks from the vehicles multiplied by their cost
		Args:
			fogs	(set[FogNode]):	Set of fog nodes
		Returns:
			float: Quality of Service (QoS) = k1*allocated_tasks - k2*nodes_usage - k3*links_load - k4*task_distance_cost
		"""
		return (K_TASKS * len(Task.all_tasks[TaskStates.IN_PROGRESS])) \
			- (K_NODES * np.var([fog.get_usage() for fog in fogs])) \
			- (K_LINKS * np.var([fog.get_links_load() for fog in fogs])) \
			- (K_COST * FogNode.all_task_distances)

	@staticmethod
	def get_eval_parameters(fogs: set[FogNode]) -> dict[str,float]:
		""" Returns parameters for the evaluation of the network\n
		Args:
			fogs	(set[FogNode]):	Set of fog nodes
		Returns:
			dict[str,float]: Allocated tasks, nodes usage, links load, completed tasks, pending tasks, failed tasks, total tasks
		"""
		# QoS
		allocated_tasks: float = len(Task.all_tasks[TaskStates.IN_PROGRESS])
		nodes_usage: float = np.var([fog.get_usage() for fog in fogs])
		links_load: float = np.var([fog.get_links_load() for fog in fogs])
		tasks_distance_cost: float = FogNode.all_task_distances

		# Other
		completed_tasks: int = len(Task.all_tasks[TaskStates.COMPLETED])
		pending_tasks: int = len(Task.all_tasks[TaskStates.PENDING])
		failed_tasks: int = len(Task.all_tasks[TaskStates.FAILED])
		total_tasks: int = sum(len(x) for x in Task.all_tasks.values())

		# Return everything
		return {
			"allocated_tasks": allocated_tasks,
			"nodes_usage": nodes_usage,
			"links_load": links_load,
			"tasks_distance_cost": tasks_distance_cost,

			"completed_tasks": completed_tasks,
			"pending_tasks": pending_tasks,
			"failed_tasks": failed_tasks,

			"total_tasks": total_tasks,
		}

