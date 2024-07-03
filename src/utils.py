
# Imports
from __future__ import annotations
from matplotlib import pyplot as plt
from src.print import *
from config import *
import time
import math
import random
import json
import io
import os


# Assign modes
class AssignMode():
	NB_ARGS: int = 3
	def __init__(self, neighbours: bool = False, qos: bool = False, cost: bool = False):
		self.neighbours = neighbours
		self.qos = qos
		self.cost = cost

		self.name: str = ""
		if self.neighbours:
			self.name += "N"
		if self.qos:
			self.name += "Q"
		if self.cost:
			self.name += "C"
		
		if self.name == "":
			self.name = "None"
	
	@staticmethod
	def get_all_assign_modes() -> list[AssignMode]:
		""" Get all the assign modes combinations
		Returns:
			list[AssignMode]: List of all the assign modes
		"""
		bools = [False, True]
		return [
			AssignMode(n, q, c)
			for n in bools
			for q in bools
			for c in bools
		]

	ALL: AssignMode = None
AssignMode.ALL = AssignMode(True, True, True)


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


# Random step function to get a number between Min and Max
def random_step(min: int, max: int, step: int = 1) -> int:

	# Check basic values
	if min > max:
		raise ValueError("Min value cannot be greater than Max value")
	if step <= 0:
		raise ValueError("Step value must be positive and different from zero")
	if min % step != 0 or max % step != 0:
		warning(f"Min and Max values must be multiples of the step value, got ({min}, {max}, {step})")

	# Divide borders by the step and check if the step is too big
	min //= step
	max //= step
	if min == max:
		raise ValueError("Step value is too big")
	
	# Return
	return random.randint(min, max) * step


# JSON dump with indentation for levels
def super_json_dump(data: dict|list, file: io.TextIOWrapper = None, max_level: int = 2) -> str:
	""" Dump the given data to a JSON file with indentation for only 2 levels by default
	Args:
		data (dict|list): 			The data to dump
		file (io.TextIOWrapper): 	The file to dump the data to, if None, the data is returned as a string
		max_level (int):			The level of where indentation should stop (-1 for infinite)
	Returns:
		str: The content of the file in every case
	"""
	content = json.dumps(data, indent = '\t', ensure_ascii = False)
	if max_level > -1:

		# Seek in content to remove to high indentations
		longest_indentation = 0
		for line in content.split("\n"):
			indentation = 0
			for char in line:
				if char == "\t":
					indentation += 1
				else:
					break
			longest_indentation = max(longest_indentation, indentation)
		for i in range(longest_indentation, max_level, -1):
			content = content.replace("\n" + "\t" * i, "")
			pass

		# To finalyze, fix the last indentations
		finishes = ('}', ']')
		for char in finishes:
			to_replace = "\n" + "\t" * max_level + char
			content = content.replace(to_replace, char)
	
	# Write file content and return it
	content += "\n"
	if file:
		file.write(content)
	return content


# Utility function that processes the return value of a simulation
def process_simulation_evaluations(evaluations_per_mode: list[dict]) -> None:
	""" Process the return value of a simulation and generate the outputs (images and data)\n
	Args:
		evaluations_per_mode (list[dict]): The evaluations of each assign mode
	"""
	# Extract all evaluations labels
	evaluations_labels: list[str] = [key for key in evaluations_per_mode[0].keys() if key not in ["folder", "name"]]

	# For each assign mode, generate its content
	root_folder: str = '/'.join(evaluations_per_mode[0]["folder"].split('/')[:-1])
	for data in evaluations_per_mode:
		folder: str = data["folder"]
		name: str = data["name"]
		os.makedirs(folder, exist_ok = True)
		for label in evaluations_labels:
			plt.clf()
			plt.plot(data[label])
			plt.title(f"{label} over time - {name}")
			plt.xlabel("Simulation Step")
			plt.ylabel(label)
			plt.savefig(f"{folder}/{label}.png", dpi = DPI_MULTIPLIER * plt.rcParams["figure.dpi"])
		
		# Save data
		with open(f"{folder}/data.json", "w", encoding = "utf-8") as file:
			super_json_dump(data, file, max_level = 1)

	# Save data
	with open(f"{root_folder}/all_data.json", "w", encoding = "utf-8") as file:
		super_json_dump(evaluations_per_mode, file, max_level = 2)

	# For each label, generate graphs comparing each assign mode
	for label in evaluations_labels:
		data: list[list[float]] = [assign_mode[label] for assign_mode in evaluations_per_mode]
		minimized_label: str = label.replace(" ", "_").lower()

		plt.clf()
		for i, mode in enumerate(evaluations_per_mode):
			plt.plot(data[i], label = mode["name"])
		plt.title(f"{label} over time")
		plt.legend()
		plt.xlabel("Simulation Step")
		plt.ylabel(label)
		plt.savefig(f"{root_folder}/{minimized_label}_comparison.png", dpi = DPI_MULTIPLIER * plt.rcParams["figure.dpi"])

