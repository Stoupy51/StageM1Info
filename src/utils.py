
# Imports
from enum import Enum
import time
import math
import random

# Assign modes
class AssignMode(Enum):
	NEAREST = "nearest"
	WITH_NEIGHBOURS = "with_neighbours"
	WITH_NEIGHBOURS_AND_QOS = "with_neighbours_and_qos"
	COST_PRIORITY = "cost_priority"
	ALL = "ALL"


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
		raise ValueError("Min and Max values must be multiples of the step value")

	# Divide borders by the step and check if the step is too big
	min //= step
	max //= step
	if min == max:
		raise ValueError("Step value is too big")
	
	# Return
	return random.randint(min, max) * step
