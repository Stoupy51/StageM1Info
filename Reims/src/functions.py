
# Imports
import traci
import time
import math
import random
random.seed(0)

# Utils function for rainbow
def get_rainbow_color(speed: float = 1.0) -> tuple[int,int,int,int]:
	""" Return a rainbow color depending on the current time
	Returns:
		tuple[int,int,int,int]: Rainbow color
	"""
	current: float = time.time() * speed
	red: int = int((1 + math.sin(current)) * 127)
	green: int = int((1 + math.sin(current + 2)) * 127)
	blue: int = int((1 + math.sin(current + 4)) * 127)
	return (red, green, blue, 255)


# Function that add a fog node as a colored polygon
def add_fog_node(fog_list: list, position: tuple[float,float], fog_shape: list[tuple], fog_color: tuple) -> None:
	""" Add a fog node as a colored polygon on the simulation
	Args:
		fog_list	(list):		List of fog nodes to add the new fog node to
		position	(tuple):	Position of the fog node
		fog_shape	(list):		Shape of the fog node
		fog_color	(tuple):	Color of the fog node
	"""
	# Get ID and extract position
	fog_id = "fog" + str(len(fog_list))
	x, y = position

	# Make new shape and add it to the simulation
	shape = [(x + dx, y + dy) for dx, dy in fog_shape]
	traci.polygon.add(polygonID = fog_id, shape = shape, color = fog_color, fill = True)

	# Add the new fog node to the list
	fog_list.append((fog_id, position))


# Function that add multiple fog nodes at random positions and returns the result
def add_random_nodes(nb_fog_nodes: int, offsets: tuple, center: tuple, random_divider: int, fog_shape: list[tuple], fog_color: tuple) -> list[tuple]:
	""" Add multiple fog nodes at random positions and returns the result
	Args:
		nb_fog_nodes	(int):		Number of fog nodes to add
		offsets			(tuple):	Offsets of the fog nodes
		center			(tuple):	Center of the fog nodes
		random_divider	(int):		Divider of the random position
		fog_shape		(list):		Shape of the fog nodes
		fog_color		(tuple):	Color of the fog nodes
	Returns:
		list[tuple]: List of fog nodes
	"""
	fog_list: list[tuple] = []
	for _ in range(nb_fog_nodes):

		# Get random position around the center of the map
		x: float = random.uniform(-offsets[0], offsets[0]) / random_divider
		y: float = random.uniform(-offsets[1], offsets[1]) / random_divider
		x += center[0]
		y += center[1]

		# Add the fog node
		add_fog_node(fog_list, (x, y), fog_shape, fog_color)
	
	# Return the list of fog nodes
	return fog_list

