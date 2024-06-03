
# Imports
from src.resources import Resource
from src.task import Task, TaskStates
import traci
import random

# Fog class
class FogNode():
	generated_nodes: set['FogNode'] = set()
	def __init__(self, fog_id: str, position: tuple[float,float], shape: list[tuple], color: tuple, resources: Resource = Resource()) -> None:
		""" FogNode constructor
		Args:
			fog_id		(str):		ID of the fog node
			position	(tuple):	Position of the fog node
			shape		(list):		Shape of the fog node
			color		(tuple):	Color of the fog node
		"""
		self.fog_id = fog_id
		self.position = position
		self.shape = shape
		self.color = color
		self.resources = resources
		self.used_resources = Resource()
		self.assigned_tasks: list[tuple["Vehicle",Task]] = []	# type: ignore
		traci.polygon.add(polygonID = fog_id, shape = self.get_adjusted_shape(), color = color, fill = True)
		FogNode.generated_nodes.add(self)
	
	def __str__(self) -> str:
		x, y = self.position
		return f"FogNode '{self.fog_id}' with: Position = ({x:>7.2f}, {y:>7.2f}),\tResource = {self.resources}"
	
	def get_adjusted_shape(self) -> list[tuple]:
		x, y = self.position
		return [(x + dx, y + dy) for dx, dy in self.shape]
	
	def get_resources(self) -> Resource:
		return self.resources
	def set_resources(self, resources: Resource) -> None:
		self.resources = resources
	
	def set_color(self, color: tuple) -> None:
		""" Set the color of the fog node
		Args:
			color	(tuple):	Color of the fog node
		"""
		self.color = color
		traci.polygon.setColor(self.fog_id, color)
	
	def has_enough_resources(self, task: Task) -> bool:
		""" Check if the fog node has enough resources to resolve the task
		Args:
			task	(Task):	Task to resolve
		Returns:
			bool: True if the fog node has enough resources, False otherwise
		"""
		return (self.used_resources + task.resource) <= self.resources
	
	def get_neighbours(self, position: tuple, radius: float) -> list['FogNode']:
		""" Get the neighbours of the fog node within a certain radius and sorted by distance
		Args:
			position	(tuple):	Position to compare
			radius		(float):	Radius to search for neighbours
		Returns:
			list: List of neighbours sorted by distance
		"""
		neighbours: list[tuple[float,'FogNode']] = []
		radius_squared: float = radius ** 2
		for node in FogNode.generated_nodes:
			if node != self:

				# Calculate distance
				distance: float = 0
				for i in range(len(position)):
					distance += (position[i] - node.position[i]) ** 2

				# Check if the node is within the radius
				if distance <= radius_squared:
					neighbours.append((distance, node))
		
		# Sort the neighbours by distance and return the nodes
		neighbours.sort(key = lambda x: x[0])
		return [node for _, node in neighbours]
	
	def assign_task(self, vehicle: "Vehicle", task: Task, radius: float = 10000, from_node: bool = False) -> bool:	# type: ignore
		""" Assign a task to the vehicle
		Args:
			vehicle		(Vehicle):	Vehicle to assign the task to
			task		(Task):		Task to assign
			radius		(float):	Radius to search for FogNode neighbours
			from_node	(bool):		True if the task is assigned from another node, False otherwise
		Returns:
			bool: True if the task was assigned, False otherwise
		"""
		if self.has_enough_resources(task):
			self.used_resources += task.resource
			self.assigned_tasks.append((vehicle, task))
			return True
		elif not from_node:
			# Ask another fog node to resolve the task
			for node in self.get_neighbours(vehicle.get_position(), radius):
				if node.assign_task(vehicle, task, from_node = True):
					return True
			
		# If no fog node can resolve the task, send a failure message (False) to the vehicle
		return False
	
	def progress_tasks(self) -> None:
		""" Progress the tasks of the fog node, sending the results to the vehicles when completed and removing the tasks from the list """
		for pair in list(self.assigned_tasks):
			vehicle: "Vehicle" = pair[0]	# type: ignore
			task: Task = pair[1]
			task.progress(1)
			if task.state == TaskStates.COMPLETED:
				vehicle.receive_task_result(task)
				self.used_resources -= task.resource
				self.assigned_tasks.remove(pair)

	@staticmethod
	def get_node_from_id(fog_id: str) -> "FogNode":
		""" Get a fog node from its ID
		Args:
			fog_id	(str):	ID of the fog node
		Returns:
			FogNode: Fog node if found, None otherwise
		"""
		matching = [node for node in FogNode.generated_nodes if node.fog_id == fog_id]
		if len(matching) == 0:
			return None
		return matching[0]

# Function that add multiple fog nodes at random positions and returns the result
def add_random_nodes(nb_fog_nodes: int, offsets: tuple, center: tuple, random_divider: int, fog_shape: list[tuple], fog_color: tuple) -> set[FogNode]:
	""" Add multiple fog nodes at random positions and returns the result
	Args:
		nb_fog_nodes	(int):		Number of fog nodes to add
		offsets			(tuple):	Offsets of the fog nodes
		center			(tuple):	Center of the fog nodes
		random_divider	(int):		Divider of the random position
		fog_shape		(list):		Shape of the fog nodes
		fog_color		(tuple):	Color of the fog nodes
	Returns:
		set[FogNode]: Set of fog nodes
	"""
	fog_list: set[FogNode] = set()
	for i in range(nb_fog_nodes):

		# Get random position around the center of the map
		x: float = random.uniform(-offsets[0], offsets[0]) / random_divider
		y: float = random.uniform(-offsets[1], offsets[1]) / random_divider
		x += center[0]
		y += center[1]

		# Add the fog node
		fog_id: str = "fog" + str(i)
		fog_list.add(FogNode(fog_id, (x, y), fog_shape, fog_color))
	
	# Return the list of fog nodes
	return fog_list

