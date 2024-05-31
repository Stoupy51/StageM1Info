
# Imports
import random

# Classes for Resource and Task
class Resource():
	def __init__(self, cpu: int = 100, ram: int = 1) -> None:
		""" Resource constructor
		Args:
			cpu		(int):	CPU of the resource (in Percentage)
			ram		(int):	RAM of the resource (in MB)
		"""
		self.cpu: int = cpu
		self.ram: int = ram
	
	def __str__(self) -> str:
		return f"(CPU: {self.cpu:>3}%, RAM: {self.ram:>5}MB)"
	
	HIGH_RANDOM_RESOURCE_ARGS: tuple = (50, 200, 25), (1024, 16384, 1024)
	LOW_RANDOM_RESOURCE_ARGS: tuple = (2, 8, 1), (64, 512, 64)
	@staticmethod
	def random(cpu: tuple[int,int,int] = HIGH_RANDOM_RESOURCE_ARGS[0], ram: tuple[int,int,int] = HIGH_RANDOM_RESOURCE_ARGS[1]):
		""" Generate a random resource
		Args:
			cpu		(tuple[int]):	Min, Max and Step for the CPU, default value means between 50% and 200% with step of 25%
			ram		(tuple[int]):	Min, Max and Step for the RAM, default value means between 1024MB and 16384MB with step of 1024MB
		Returns:
			Resource: generated resource with random values
		"""
		# Get random CPU
		cpu_min, cpu_max, cpu_step = cpu
		if cpu_min > cpu_max or cpu_step <= 0:
			raise ValueError("Invalid CPU values, min must be lower than max and step must be positive")
		cpu_min //= cpu_step
		cpu_max //= cpu_step
		if cpu_min == cpu_max:
			raise ValueError("Invalid CPU values, step is too big")
		r_cpu: int = random.randint(cpu_min, cpu_max) * cpu_step

		# Get random RAM
		ram_min, ram_max, ram_step = ram
		if ram_min > ram_max or ram_step <= 0:
			raise ValueError("Invalid RAM values, min must be lower than max and step must be positive")
		ram_min //= ram_step
		ram_max //= ram_step
		if ram_min == ram_max:
			raise ValueError("Invalid RAM values, step is too big")
		r_ram: int = random.randint(ram_min, ram_max) * ram_step

		# Return the generated resource
		return Resource(r_cpu, r_ram)

