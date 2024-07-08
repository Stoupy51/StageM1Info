
# Imports
from __future__ import annotations
from src.resources import Resource
from src.task import Task, TaskStates
from src.utils import *
from src.print import *
from config import *
import traci
import random
import math


# Fog class
class FogNode():
	generated_nodes: set[FogNode] = set()
	all_task_distances: float = 0.0

	def __init__(self, id: str, position: tuple[float,float], shape: list[tuple], color: tuple, resources: Resource = Resource()) -> None:
		""" FogNode constructor
		Args:
			id		(str):		ID of the fog node
			position	(tuple):	Position of the fog node
			shape		(list):		Shape of the fog node
			color		(tuple):	Color of the fog node
		"""
		self.id: str = id
		self.position: tuple[float,float] = position
		self.shape: list[tuple] = shape
		self.color: tuple = color
		self.resources: Resource = resources
		self.used_resources = Resource.empty()
		self.usage: float = 0.0
		self.assigned_tasks: list[Task] = []
		self.links: list[FogNodesLink] = []
		self.task_distances: float = 0.0	# Indicates the sum of the task distances to their vehicle
		FogNode.generated_nodes.add(self)
		traci.polygon.add(polygonID = id, shape = self.get_adjusted_shape(), color = color, fill = True)
	
	def __str__(self) -> str:
		x, y = self.position
		return f"FogNode '{self.id}' with: Position = ({x:>7.2f}, {y:>7.2f}),\tResource = {self.resources}"
	
	def get_adjusted_shape(self) -> list[tuple]:
		""" Calculate the adjusted shape of the fog node """
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
	
	def add_task_distance(self, distance: float) -> None:
		distance = math.sqrt(distance)
		self.task_distances += distance
		FogNode.all_task_distances += distance
	def remove_task_distance(self, distance: float) -> None:
		distance = math.sqrt(distance)
		self.task_distances -= distance
		FogNode.all_task_distances -= distance
	
	def set_color(self, color: tuple) -> None:
		""" Set the color of the fog node
		Args:
			color	(tuple):	Color of the fog node
		"""
		self.color = tuple(color)
		traci.polygon.setColor(self.id, self.color)
	
	def has_enough_resources(self, task: Task) -> bool:
		""" Check if the fog node has enough resources to resolve the task
		Args:
			task	(Task):	Task to resolve
		Returns:
			bool: True if the fog node has enough resources, False otherwise
		"""
		return (self.used_resources + task.resource) <= self.resources
	
	def set_neighbours(self, nodes: list[FogNode], bandwidth_range: tuple[int,int,int]) -> None:
		""" Set node links to neighbours of the fog node sorted by distance (using math.dist)\n
		The method should be called after all fog nodes are created
		Args:
			bandwidth_range	(tuple):	Range of the bandwidth for the links (min, max, step)
		"""
		# Get neighbours sorted by distance
		neighbours: list[tuple[float,FogNode]] = [
			(math.dist(node.position, self.position), node)
			for node in nodes
			if node != self
		]
		neighbours.sort(key = lambda pair: pair[0])
		neighbours = neighbours[:MAX_NEIGHBOURS]

		# Create links to each neighbour
		self.links: list[FogNodesLink] = []
		for distance, node in neighbours:
			latence: int = int(distance)
			bandwidth: int = random_step(*bandwidth_range)
			self.links.append(FogNodesLink(node, latence, bandwidth))
	
	def reset_links_charge(self, debug_msg: bool) -> bool:
		""" Reset the charge of all links of the fog node
		Args:
			debug_msg	(bool):	Whether to print debug messages
		Returns:
			bool: if any link got a charge before reset
		"""
		any_reset: bool = False
		for link in self.links:
			if link.charge != 0:
				if debug_msg:
					debug(link)
				link.charge = 0
				any_reset = True
		return any_reset
	
	def get_links(self) -> list[FogNodesLink]:
		""" Get the links of the fog node
		Returns:
			list[FogNodesLink]: List of the links of the fog node
		"""
		return self.links
	
	def calculate_usage(self) -> None:
		""" Calculate the usage variable (the highest usage of the resources for each type) """
		self.usage: float = (self.used_resources / self.resources).max()

	def get_usage(self) -> float:
		""" Get the highest usage of the resources for each type
		Returns:
			float: Highest usage of the resources
		"""
		return self.usage

	def get_links_load(self) -> float:
		""" Get the sum of the Fog nodes links load
		Returns:
			float: Sum of the Fog nodes links load
		"""
		return sum(link.get_usage() for link in self.links)
	
	def assign_task(self, task: Task) -> TaskStates:
		""" Assign a task to the fog node and returns the old state of the task\n
		Args:
			vehicle			(Vehicle):		Vehicle to assign the task to
			task			(Task):			Task to assign
		Returns:
			TaskStates:		Old state of the task
		"""
		old_state: TaskStates = task.state
		task.progress(0)

		# Register task and calculate the new usage
		self.assigned_tasks.append(task)
		self.used_resources += task.resource
		self.calculate_usage()

		# Add up the task distance
		task.calculate_distance_to_vehicle(task.vehicle, self)
		self.add_task_distance(task.distance_to_vehicle * task.cost)

		return old_state
	
	def revert_assign(self, assigned_task: Task, old_state: TaskStates = None, is_last: bool = True) -> None:
		""" Revert the assignation of a task to the fog node
		Args:
			assigned_task	(Task):			Task to revert
			old_state		(TaskStates):	Old state of the task
			is_last			(bool):			Used for code optimization, the task is at last position of the list if True
		"""
		self.used_resources -= assigned_task.resource
		self.calculate_usage()
		if is_last:
			self.assigned_tasks.pop()
		else:
			self.assigned_tasks = [task for task in self.assigned_tasks if task is not assigned_task]
		if old_state is not None:
			assigned_task.change_state(old_state)
	
	def get_replaceable_tasks(self, incomming_task: Task) -> list[Task]:
		""" Get tasks that can be replaced (if we remove the task we have enough resources to accept the incomming one)\n
		The tasks are sorted by cost and the cost is lower than the incomming task cost
		Args:
			incomming_task	(Task):			New task to assign to compare with
		Returns:
			list[Task]:	List of tasks that can be replaced
		"""
		replaceable_tasks: list[Task] = [
			task for task in self.assigned_tasks
			if (task.cost < incomming_task.cost)													# Task cost is lower than the incomming task cost
			and (self.used_resources - task.resource + incomming_task.resource) <= self.resources	# We have enough resources to accept the incomming task if we remove the task
		]
		return sorted(replaceable_tasks, key = lambda task: task.cost)

	def ask_assign_task(self, incomming_task: Task, mode: AssignMode, from_vehicle: bool = True) -> bool:
		""" Assign a task from a vehicle to the fog node
		Args:
			task			(Task):			Task to assign
			mode			(AssignMode):	Configuration of the assign mode
			from_vehicle	(bool):			True if the task is from a vehicle, False if it is from a fog node (to prevent too deep recursion)
		Returns:
			bool: True if the task was assigned, False otherwise
		"""
		if self.has_enough_resources(incomming_task):

			# If check_qos, accept the task if the new QoS is better than the old one
			if mode.qos:
				from src.evaluations import Evaluator

				old_qos: float = Evaluator.calculate_qos(FogNode.generated_nodes)
				old_state: TaskStates = self.assign_task(incomming_task)
				new_qos: float = Evaluator.calculate_qos(FogNode.generated_nodes)

				if new_qos >= old_qos:
					return True
				self.revert_assign(incomming_task, old_state)
				self.remove_task_distance(incomming_task.distance_to_vehicle * incomming_task.cost)

			# Else, accept the task as we have enough resources
			else:
				self.assign_task(incomming_task)
				return True
		
		# If the task is from a vehicle, try communication with other fog nodes
		if from_vehicle:

			# For each replaceable tasks, try to assign to each neighbour and stop if any accept
			if mode.cost:
				for task in self.get_replaceable_tasks(incomming_task):
					task_distance: float = task.distance_to_vehicle * task.cost
					for link in self.links:

						# If the link can handle the charge and the fog node accept the task,
						if link.can_handle_charge(task.bandwidth_charge) and \
						link.other.ask_assign_task(task, mode = mode, from_vehicle = False):
							debug(f"Moved task {task.id} from {self.id} to {link.other.id} because cost {task.cost} is lower than {incomming_task.cost}. Charge: {task.bandwidth_charge}")

							# Revert assign the task (as the link sended it) to allow the assignment of the incomming one
							self.revert_assign(task, is_last = False)
							self.remove_task_distance(task_distance)
							self.assign_task(incomming_task)

							# Add up the new charge to the link and return True
							link.charge += task.bandwidth_charge
							return True

			# Ask the neighbours if they can assign the task
			elif mode.neighbours:
				for link in self.links:

					# If the link can handle the charge and the fog node accept the task,
					if link.can_handle_charge(incomming_task.bandwidth_charge) and \
					link.other.ask_assign_task(incomming_task, mode = mode, from_vehicle = False):
						link.charge += incomming_task.bandwidth_charge
						return True
		
		# Nobody can assign the task
		return False


	def progress_tasks(self) -> None:
		""" Progress the tasks of the fog node, sending the results to the vehicles when completed and removing the tasks from the list """
		new_list: list[Task] = []
		for task in self.assigned_tasks:
			task.progress(1)
			if task.state == TaskStates.COMPLETED:
				task.vehicle.receive_task_result(task)

				self.remove_task_distance(task.distance_to_vehicle * task.cost)
				self.used_resources -= task.resource
				self.calculate_usage()
			else:
				new_list.append(task)
		self.assigned_tasks = new_list
	

	@staticmethod
	def reset_links_charges(fogs: set[FogNode], debug_msg: bool) -> bool:
		""" Reset the charge of all links of all fog nodes
		Args:
			fogs		(set[FogNode]):	Set of fog nodes
			debug_msg	(bool):			Whether to print debug messages
		Returns:
			bool: if any link got a charge before reset
		"""
		any_reset: bool = False
		for fog in fogs:
			if fog.reset_links_charge(debug_msg):
				any_reset = True
		return any_reset
	
	@staticmethod
	def color_usage(fogs: set[FogNode]) -> None:
		""" Change the color of the fog nodes depending on their resources """
		LOW_COLOR = (0, 0, 255)
		HIGH_COLOR = (255, 0, 0)
		for fog in fogs:
			
			# Get highest usage of the resource
			usage = fog.used_resources / fog.resources
			usage = max(usage.cpu, usage.ram)

			# Calculate the color depending on the usage
			fog.set_color( [int(LOW_COLOR[i] + (HIGH_COLOR[i] - LOW_COLOR[i]) * usage) for i in range(3)] )

	# Function that add multiple fog nodes at random positions and returns the result
	@staticmethod
	def random_nodes(nb_fog_nodes: int, offsets: tuple, center: tuple, random_divider: int, fog_shape: list[tuple], fog_color: tuple) -> set[FogNode]:
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
			id: str = "fog" + str(i)
			fog_list.add(FogNode(id, (x, y), fog_shape, fog_color))
		
		# Return the list of fog nodes
		return fog_list


class FogNodesLink():
	def __init__(self, other: FogNode, latence: int, bandwidth: int) -> None:
		""" FogNodesLink constructor
		Args:
			other		(FogNode):	Other fog node
			latence		(int):		Latence of the link (not used)
			bandwidth	(int):		Bandwidth of the link (in MB/s)
		"""
		self.other: FogNode = other
		self.latence: int = latence
		self.bandwidth: int = bandwidth
		self.charge: int = 0
	
	def __str__(self) -> str:
		return f"Link to {self.other.id} with: Latence = {self.latence}, Bandwidth = {self.bandwidth}MB/s, Current charge = {self.charge}MB"
	
	def can_handle_charge(self, incomming: int) -> bool:
		""" Check if the link can handle the charge
		Args:
			incomming	(int):	Charge to handle
		Returns:
			bool: True if the link can handle the charge, False otherwise
		"""
		return (self.charge + incomming) <= self.bandwidth

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

