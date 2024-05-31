
# Imports
from resources import *
import traci
import random
"""	# Change color of every vehicles
	for vehicle_id in traci.vehicle.getIDList():
		traci.vehicle.setColor(vehicle_id, get_rainbow_color())
	
	# Change color of each fog
	for fog_node in fog_list:
		fog_node.set_color(get_rainbow_color(0.25))
"""

# Vehicle class
class Vehicle():
	vehicles: list = []
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

