
# Imports
import time
import math

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

