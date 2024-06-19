
# Imports
from src.resources import Resource
from src.task import Task, TaskStates
import traci
import random
import math

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
		self.used_resources = Resource(cpu = 0, ram = 0)
		self.assigned_tasks: list[tuple["Vehicle",Task]] = []	# type: ignore
		traci.polygon.add(polygonID = fog_id, shape = self.get_adjusted_shape(), color = color, fill = True)
		FogNode.generated_nodes.add(self)
	
	def __str__(self) -> str:
		x, y = self.position
		return f"FogNode '{self.fog_id}' with: Position = ({x:>7.2f}, {y:>7.2f}),\tResource = {self.resources}"
	
	def get_adjusted_shape(self) -> list[tuple]:

		# Offset the position so that x and y are the center of the shape
		x, y = self.position
		r_x, r_y = [x // 2 for x in self.shape[-1]]
		x -= r_x
		y -= r_y

		# Return the adjusted shape
		return [(x + dx, y + dy) for dx, dy in self.shape]
	
	def get_resources(self) -> Resource:
		return self.resources
	def set_resources(self, resources: Resource) -> None:
		self.resources = resources
	def get_used_resources(self) -> Resource:
		return self.used_resources
	
	def get_usage(self) -> float:
		""" Get the highest usage of the resources for each type
		Returns:
			float: Highest usage of the resources
		"""
		return (self.used_resources / self.resources).max()
	
	def get_links_load(self) -> float:
		""" Get the sum of the Fog nodes links load
		Returns:
			float: Sum of the Fog nodes links load
		"""
		return 0	# Not implemented
	
	def set_color(self, color: tuple) -> None:
		""" Set the color of the fog node
		Args:
			color	(tuple):	Color of the fog node
		"""
		self.color = tuple(color)
		traci.polygon.setColor(self.fog_id, self.color)
	
	def has_enough_resources(self, task: Task) -> bool:
		""" Check if the fog node has enough resources to resolve the task
		Args:
			task	(Task):	Task to resolve
		Returns:
			bool: True if the fog node has enough resources, False otherwise
		"""
		return (self.used_resources + task.resource) <= self.resources
	
	def set_neighbours(self, nodes: list['FogNode'], bandwith_range: tuple[int,int]) -> None:
		""" Set node links to neighbours of the fog node sorted by distance (using math.dist)\n
		The method should be called after all fog nodes are created
		Args:
			bandwith_range	(tuple):	Range of the bandwidth for the links
		"""
		# Get neighbours sorted by distance
		neighbours: list[tuple[float,'FogNode']] = [
			(math.dist(node.position, self.position), node)
			for node in FogNode.generated_nodes
			if node != self
		]
		neighbours.sort(key = lambda pair: pair[0])

		# Create links to each neighbour
		self.links: list[FogNodesLink] = []
		for distance, node in neighbours:
			latence: int = int(distance)
			bandwidth: int = random.randint(*bandwith_range)
			self.links.append(FogNodesLink(node, latence, bandwidth))

	
	def get_links(self) -> list['FogNodesLink']:
		""" Get the links of the fog node
		Returns:
			list[FogNodesLink]: List of the links of the fog node
		"""
		return self.links
	
	def assign_task(self, vehicle: "Vehicle", task: Task) -> bool:	# type: ignore
		""" Assign a task from a vehicle to the fog node
		Args:
			vehicle		(Vehicle):	Vehicle to assign the task to
			task		(Task):		Task to assign
		Returns:
			bool: True if the task was assigned, False otherwise
		"""
		if self.has_enough_resources(task):
			self.used_resources += task.resource
			self.assigned_tasks.append((vehicle, task))
			return True
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
	
	@staticmethod
	def color_usage(fogs: set['FogNode']) -> None:
		""" Change the color of the fog nodes depending on their resources """
		LOW_COLOR = (0, 255, 0)
		HIGH_COLOR = (255, 0, 0)
		for fog in fogs:
			
			# Get highest usage of the resource
			usage = fog.used_resources / fog.resources
			usage = max(usage.cpu, usage.ram)

			# Calculate the color depending on the usage
			fog.set_color( [int(LOW_COLOR[i] + (HIGH_COLOR[i] - LOW_COLOR[i]) * usage) for i in range(3)] )

	# Function that add multiple fog nodes at random positions and returns the result
	@staticmethod
	def random_nodes(nb_fog_nodes: int, offsets: tuple, center: tuple, random_divider: int, fog_shape: list[tuple], fog_color: tuple) -> set['FogNode']:
		""" Create multiple fog nodes at random positions and returns the result
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


class FogNodesLink():
	def __init__(self, other: FogNode, latence: int, bandwidth: int) -> None:
		""" FogNodesLink constructor
		Args:
			other		(FogNode):	Other fog node
			latence		(int):		Latence of the link
			bandwidth	(int):		Bandwidth of the link (in MB/s)
		"""
		self.other: FogNode = other
		self.latence: int = latence
		self.bandwidth: int = bandwidth
		self.charge: int = 0
	
	def __str__(self) -> str:
		return f"Link to {self.other.fog_id} with: Latence = {self.latence}, Bandwidth = {self.bandwidth}MB/s"

	def get_charge(self) -> int:
		""" Get the charge of the link
		Returns:
			int: Charge of the link
		"""
		return self.charge
	
	def get_usage(self) -> float:
		""" Get the usage of the link (charge divided by bandwidth)
		Returns:
			float: Usage of the link
		"""
		return self.charge / self.bandwidth

