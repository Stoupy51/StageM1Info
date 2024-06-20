
# Imports
from src.resources import Resource
from enum import Enum
import random
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

	def __init__(self, task_id: str, resource: Resource, resolving_time: int = 0, time_constraint: int|None = None) -> None:
		""" Task constructor
		Args:
			task_id			(str):		ID of the task
			resource		(Resource):	Resource needed for the task
			resolving_time	(int):		Time needed to complete the task (in seconds)
			time_constraint	(int):		Timestamp when the task must be completed
		"""
		self.id: str = task_id
		self.resource: Resource = resource
		self.resolving_time: int = resolving_time
		self.time_constraint: int = time_constraint
		self.state: TaskStates = TaskStates.PENDING
		Task.all_tasks[self.state].append(self)
	
	def __str__(self) -> str:
		limit_date: str = "None"
		if self.time_constraint is not None:
			limit_date = time.strftime("%H:%M:%S", time.localtime(self.time_constraint))
		return f"{self.state} Task '{self.id}' with: Resource = {self.resource}, Resolving Time = {self.resolving_time}s, Time Constraint = [{limit_date}]"
	
	@staticmethod
	def random(id: str, resource: Resource = None, resolving_time: tuple[int,int,int] = (10, 60, 5), time_constraint: int|None = None):
		""" Generate a random task
		Args:
			id				(str):			ID of the task
			resource		(Resource):		Resource needed for the task
			resolving_time	(tuple[int]):	Min, Max and Step for the resolving time, default value means between 10s and 60s with step of 5s
			time_constraint	(int):			Timestamp when the task must be completed
		Returns:
			Task: generated task with random values
		"""
		# Get random Resolving Time
		rt_min, rt_max, rt_step = resolving_time
		if rt_min > rt_max or rt_step <= 0:
			raise ValueError("Invalid Resolving Time values, min must be lower than max and step must be positive")
		rt_min //= rt_step
		rt_max //= rt_step
		if rt_min == rt_max:
			raise ValueError("Invalid Resolving Time values, step is too big")

		# Return the generated task
		if resource is None:
			resource = Resource.random()
		return Task(id, resource, random.randint(rt_min, rt_max) * rt_step, time_constraint)

	# Progress task
	def progress(self, time_spent: int = 0) -> None:
		""" Progress the task by spending time on it resulting in a state change if needed
		Args:
			time_spent	(int):	Time spent on the task, default is 0 (resulting in a state change if it was pending)
		"""
		self.resolving_time -= time_spent
		if self.resolving_time <= 0:
			Task.all_tasks[self.state].remove(self)
			self.state = TaskStates.COMPLETED
			Task.all_tasks[self.state].append(self)
		else:
			Task.all_tasks[self.state].remove(self)
			self.state = TaskStates.IN_PROGRESS
			Task.all_tasks[self.state].append(self)

