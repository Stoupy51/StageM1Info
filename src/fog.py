
# Imports
from resources import Resource
import traci
import random

# Fog class
class FogNode():
	generated_nodes: list = []
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
		traci.polygon.add(polygonID = fog_id, shape = self.get_adjusted_shape(), color = color, fill = True)
		FogNode.generated_nodes.append(self)
	
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

	@staticmethod
	def get_node_from_id(fog_id: str):
		""" Get a fog node from its ID
		Args:
			fog_id	(str):	ID of the fog node
		Returns:
			FogNode: Fog node if found, None otherwise
		"""
		nodes: list[FogNode] = FogNode.generated_nodes
		for node in nodes:
			if node.fog_id == fog_id:
				return node
		return None

# Function that add multiple fog nodes at random positions and returns the result
def add_random_nodes(nb_fog_nodes: int, offsets: tuple, center: tuple, random_divider: int, fog_shape: list[tuple], fog_color: tuple) -> list[FogNode]:
	""" Add multiple fog nodes at random positions and returns the result
	Args:
		nb_fog_nodes	(int):		Number of fog nodes to add
		offsets			(tuple):	Offsets of the fog nodes
		center			(tuple):	Center of the fog nodes
		random_divider	(int):		Divider of the random position
		fog_shape		(list):		Shape of the fog nodes
		fog_color		(tuple):	Color of the fog nodes
	Returns:
		list[FogNode]: List of fog nodes
	"""
	fog_list: list[FogNode] = []
	for i in range(nb_fog_nodes):

		# Get random position around the center of the map
		x: float = random.uniform(-offsets[0], offsets[0]) / random_divider
		y: float = random.uniform(-offsets[1], offsets[1]) / random_divider
		x += center[0]
		y += center[1]

		# Add the fog node
		fog_id: str = "fog" + str(i)
		fog_list.append(FogNode(fog_id, (x, y), fog_shape, fog_color))
	
	# Return the list of fog nodes
	return fog_list

