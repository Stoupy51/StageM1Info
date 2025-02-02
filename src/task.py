
# Imports
from src.resources import Resource
from src.utils import random_step
from config import *
from enum import Enum
import time

class TaskStates(Enum):
	PENDING = 0
	IN_PROGRESS = 1
	COMPLETED = 2
	FAILED = 3

# Task class
class Task():
	""" Task class """
	# Dictionary of all tasks with their states
	all_tasks: dict[TaskStates, list["Task"]] = {
		TaskStates.PENDING: [],
		TaskStates.IN_PROGRESS: [],
		TaskStates.COMPLETED: [],
		TaskStates.FAILED: []
	}

	def __init__(self, task_id: str, vehicle: "Vehicle", resource: Resource, resolving_time: int = 0, cost: int = 1, time_constraint: int|None = None) -> None:	# type: ignore
		""" Task constructor
		Args:
			task_id			(str):		ID of the task
			vehicle			(Vehicle):	Owner vehicle of the task
			resource		(Resource):	Resource needed for the task
			resolving_time	(int):		Time needed to complete the task (in seconds)
			cost			(int):		Cost of the task (in euros)
			time_constraint	(int):		Timestamp when the task must be completed
		"""
		self.id: str = task_id
		self.vehicle: "Vehicle" = vehicle	# type: ignore
		self.resource: Resource = resource
		self.resolving_time: int = resolving_time
		self.cost: int = cost
		self.time_constraint: int = time_constraint
		self.state: TaskStates = TaskStates.PENDING
		Task.all_tasks[self.state].append(self)
		self.distance_to_vehicle: float = 0.0

		# Bandwidth charge needed to transfer the task from a node to another one
		self.bandwidth_charge: int = int(K_BANDWIDTH_CHARGE * self.resolving_time)
	
	def __str__(self) -> str:
		limit_date: str = "None"
		if self.time_constraint is not None:
			limit_date = time.strftime("%H:%M:%S", time.localtime(self.time_constraint))
		return f"{self.state.name} Task '{self.id}' with: Resource = {self.resource}, Resolving Time = {self.resolving_time}s, Cost = {self.cost}€, Time Constraint = [{limit_date}]"
	
	def change_state(self, new_state: TaskStates) -> None:
		""" Change the state of the task (removes it from the current state and adds it to the new state)
		Args:
			new_state	(TaskStates):	New state for the task
		"""
		if self.state == new_state:	# stop if no changes
			return

		# If the task is in the current state list, move it to the new state list
		if self in Task.all_tasks[self.state]:
			Task.all_tasks[self.state].remove(self)
			Task.all_tasks[new_state].append(self)

		# Else, add the task to the new list if it's not in it
		elif self not in Task.all_tasks[new_state]:
			Task.all_tasks[new_state].append(self)

		# Change the state to the new one
		self.state = new_state
	
	def calculate_distance_to_vehicle(self, vehicle: "Vehicle", fog: "FogNode") -> None:	# type: ignore
		""" Calculate the distance to the vehicle
		Args:
			vehicle		(Vehicle):	Vehicle to calculate the distance to
			fog			(FogNode):	Fog node to calculate the distance to
		"""
		self.distance_to_vehicle = vehicle.get_distance_to_fog(fog)
	
	# Progress task
	def progress(self, time_spent: int = 0) -> None:
		""" Progress the task by spending time on it resulting in a state change if needed
		Args:
			time_spent	(int):	Time spent on the task, default is 0 (resulting in a state change if it was pending)
		"""
		self.resolving_time -= time_spent
		if self.resolving_time <= 0:
			self.change_state(TaskStates.COMPLETED)
		else:
			self.change_state(TaskStates.IN_PROGRESS)

