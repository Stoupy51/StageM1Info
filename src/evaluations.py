
# Imports
from src.task import Task, TaskStates
from src.fog import FogNode
from config import *
import numpy as np

# Evaluation of the network
class Evaluator():

	@staticmethod
	def calculate_qos(fogs: set[FogNode]) -> float:
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
		allocated_tasks: int = len(Task.all_tasks[TaskStates.IN_PROGRESS])
		nodes_usage: float = np.var([fog.get_usage() for fog in fogs])
		links_load: float = np.var([fog.get_links_load() for fog in fogs])

		# Calculate the QoS and return it
		return (K1 * allocated_tasks) - (K2 * nodes_usage) - (K3 * links_load)

