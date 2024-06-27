
# Imports
from src.resources import Resource
from src.task import Task, TaskStates
from src.fog import FogNode
from src.utils import AssignMode
import traci
import random
import math

# Vehicle class
class Vehicle():
	vehicles: set["Vehicle"] = set()
	def __init__(self, vehicle_id: str, tasks: list[Task] = None) -> None:
		""" Vehicle constructor
		Args:
			vehicle_id	(str):		ID of the vehicle
			tasks		(list):		List of tasks for the vehicle (default is empty)
		"""
		self.vehicle_id = vehicle_id
		self.tasks = tasks if tasks is not None else []
		self.not_finished_tasks: int = len([task for task in self.tasks if task.state not in [TaskStates.COMPLETED, TaskStates.FAILED]])
		Vehicle.vehicles.add(self)
	
	def __str__(self) -> str:
		return f"Vehicle '{self.vehicle_id}' with {len(self.tasks)} tasks"
	
	def get_position(self) -> tuple:
		""" Get the position of the vehicle
		Returns:
			tuple: Position of the vehicle
		"""
		return traci.vehicle.getPosition(self.vehicle_id)
	
	def generate_tasks(self, nb_tasks: tuple[int,int] = (1,3), random_resource_args: tuple = Resource.LOW_RANDOM_RESOURCE_ARGS, random_costs: tuple[int,int,int] = Task.COST_RANGE) -> None:
		""" Generate tasks for the vehicle
		Args:
			nb_tasks				(tuple):	Min and Max number of tasks to generate
			random_resource_args	(tuple):	Arguments for the random resource generation
		"""
		for i in range(random.randint(*nb_tasks)):
			task_id = f"{self.vehicle_id}_task_{i}"						# Generate task ID based on vehicle ID
			random_resource = Resource.random(*random_resource_args)	# Generate random resource with low values
			self.tasks.append(Task(task_id, random_resource))
			self.not_finished_tasks += 1
	
	def get_nearest_fogs(self, fogs: set[FogNode]) -> FogNode:
		""" Get the nearest fog nodes to the vehicle
		Args:
			fogs	(set):	Set of fog nodes
		Returns:
			list[FogNode]: List of nearest fog nodes
		"""
		vehicle_position: tuple = traci.vehicle.getPosition(self.vehicle_id)
		return sorted(fogs, key = lambda fog: math.dist(fog.position, vehicle_position))
	
	def receive_task_result(self, task: Task) -> None:
		""" Receive the result of a task
		Args:
			task	(Task):	Task that has been resolved
		"""
		self.not_finished_tasks -= 1
		task.change_state(TaskStates.COMPLETED)
	
	def assign_tasks(self, fogs: set[FogNode], mode: AssignMode = AssignMode.ALL) -> None:
		""" Assign pensing tasks to the nearest fog node
		Args:
			fogs			(set[FogNode]):	Set of fog nodes
			mode			(AssignMode):	Configuration of how the tasks are assigned
		"""
		# Get the nearest fog and the pending tasks
		nearest_fog: FogNode = self.get_nearest_fogs(fogs)[0]
		pending_tasks: list[Task] = [task for task in self.tasks if task.state == TaskStates.PENDING]
		nb_tasks: int = len(pending_tasks)

		# Try to assign every tasks to the nearest fog node
		for task in pending_tasks:
			if nearest_fog.ask_assign_task(self, task, mode = mode):
				task.change_state(TaskStates.IN_PROGRESS)
				nb_tasks -= 1
		
		# Color green if no task is PENDING, blue instead
		color: tuple = (0, 255, 0) if nb_tasks == 0 else (0, 0, 255)
		traci.vehicle.setColor(self.vehicle_id, color)


	@staticmethod
	def get_vehicle_from_id(vehicle_id: str) -> "Vehicle":
		""" Get a vehicle from its ID
		Args:
			vehicle_id	(str):	ID of the vehicle
		Returns:
			Vehicle: Vehicle if found, None otherwise
		"""
		matching = [vehicle for vehicle in Vehicle.vehicles if vehicle.vehicle_id == vehicle_id]
		if len(matching) == 0:
			return None
		return matching[0]
	
	@staticmethod
	def acknowledge_removed_vehicles() -> None:
		""" Acknowledge removed vehicles in the simulation """
		id_list: set[str] = set(traci.vehicle.getIDList())
		Vehicle.vehicles = set([vehicle for vehicle in Vehicle.vehicles if vehicle.vehicle_id in id_list])
	
	@staticmethod
	def acknowledge_new_vehicles() -> None:
		""" Acknowledge new vehicles in the simulation """
		id_list: set = set(traci.vehicle.getIDList())
		vehicle_ids: set = set([vehicle.vehicle_id for vehicle in Vehicle.vehicles])
		not_known_vehicles: set = id_list - vehicle_ids
		for vehicle_id in not_known_vehicles:
			Vehicle(vehicle_id)

