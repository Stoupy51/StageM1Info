
# Imports
from src.resources import Resource
from src.task import Task
from src.fog import FogNode
import traci
import random

# Vehicle class
class Vehicle():
	vehicles: list["Vehicle"] = []
	def __init__(self, vehicle_id: str, tasks: list[Task] = []) -> None:
		""" Vehicle constructor
		Args:
			vehicle_id	(str):		ID of the vehicle
			tasks		(list):		List of tasks for the vehicle (default is empty)
		"""
		self.vehicle_id = vehicle_id
		self.tasks = tasks
		Vehicle.vehicles.append(self)
	
	def __str__(self) -> str:
		return f"Vehicle '{self.vehicle_id}' with {len(self.tasks)} tasks"
	
	def get_position(self) -> tuple:
		""" Get the position of the vehicle
		Returns:
			tuple: Position of the vehicle
		"""
		return traci.vehicle.getPosition(self.vehicle_id)
	
	def generate_tasks(self, nb_tasks: tuple[int,int] = (1,3), random_resource_args: tuple = Resource.LOW_RANDOM_RESOURCE_ARGS) -> None:
		""" Generate tasks for the vehicle
		Args:
			nb_tasks				(tuple):	Min and Max number of tasks to generate
			random_resource_args	(tuple):	Arguments for the random resource generation
		"""
		for i in range(random.randint(*nb_tasks)):
			task_id = f"{self.vehicle_id}_task_{i}"						# Generate task ID based on vehicle ID
			random_resource = Resource.random(*random_resource_args)	# Generate random resource with low values
			self.tasks.append(Task(task_id, random_resource))
	
	def get_nearest_fog(self, fog_list: list[FogNode]) -> FogNode:
		""" Get the nearest fog node to the vehicle
		Args:
			fog_list	(list):	List of fog nodes
		Returns:
			FogNode: Nearest fog node to the vehicle
		"""
		vehicle_position: tuple = traci.vehicle.getPosition(self.vehicle_id)
		nearest_fog: FogNode = None
		min_distance: float = None
		for fog_node in fog_list:

			# Calculate the distance between the vehicle and the fog node
			fog_position: tuple = fog_node.position
			distance: float = 0
			for i in range(len(vehicle_position)):
				distance += (vehicle_position[i] - fog_position[i]) ** 2

			# Check if the fog node is the nearest
			if min_distance is None or distance < min_distance:
				min_distance = distance
				nearest_fog = fog_node
		
		return nearest_fog
	
	def receive_task_result(self, task: Task) -> None:
		""" Receive the result of a task
		Args:
			task	(Task):	Task that has been resolved
		"""
		self.tasks.remove(task)


	@staticmethod
	def get_vehicle_from_id(vehicle_id: str):
		""" Get a vehicle from its ID
		Args:
			vehicle_id	(str):	ID of the vehicle
		Returns:
			Vehicle: Vehicle if found, None otherwise
		"""
		vehicles: list[Vehicle] = Vehicle.vehicles
		for vehicle in vehicles:
			if vehicle.vehicle_id == vehicle_id:
				return vehicle
		return None

