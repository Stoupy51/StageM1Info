
# Imports
from src.utils import random_step
import random

# Classes for Resource and Task
class Resource():
	def __init__(self, cpu: int = 100, ram: int = 1024, storage: int = 16) -> None:
		""" Resource constructor
		Args:
			cpu		(int):	CPU of the resource (in Percentage)
			ram		(int):	RAM of the resource (in MB)
			storage	(int):	Storage of the resource (in GB)
		"""
		self.cpu: int = cpu
		self.ram: int = ram
		self.storage: int = storage
	
	def __str__(self) -> str:
		return f"(CPU: {self.cpu:>3}%, RAM: {self.ram:>5}MB, Storage: {self.storage:>3}GB)"
	
	# Arithmetic operations
	def __add__(self, other: "Resource") -> "Resource":
		return Resource(self.cpu + other.cpu, self.ram + other.ram, self.storage + other.storage)
	def __sub__(self, other: "Resource") -> "Resource":
		return Resource(self.cpu - other.cpu, self.ram - other.ram, self.storage - other.storage)
	def __mul__(self, other: int) -> "Resource":
		return Resource(self.cpu * other, self.ram * other, self.storage * other)
	def __truediv__(self, other) -> "Resource":
		if isinstance(other, Resource):
			return Resource(self.cpu / other.cpu, self.ram / other.ram, self.storage / other.storage)
		return Resource(self.cpu / other, self.ram / other, self.storage / other)
	def __floordiv__(self, other) -> "Resource":
		if isinstance(other, Resource):
			return Resource(self.cpu // other.cpu, self.ram // other.ram, self.storage // other.storage)
		return Resource(self.cpu // other, self.ram // other, self.storage // other)
	def __mod__(self, other) -> "Resource":
		if isinstance(other, Resource):
			return Resource(self.cpu % other.cpu, self.ram % other.ram, self.storage % other.storage)
		return Resource(self.cpu % other, self.ram % other, self.storage % other)
	
	# Comparison operations
	def __le__(self, other: "Resource") -> bool:	# Less or equal
		return self.cpu <= other.cpu and self.ram <= other.ram and self.storage <= other.storage
	
	# Get the maximum value between each type
	def max(self) -> int:
		return max(self.cpu, self.ram, self.storage)
	
	EXTREME_RANDOM_RESOURCE_ARGS: tuple = (5000, 20000, 2500), (8192, 65536, 8192), (1024, 8192, 256)
	HIGH_RANDOM_RESOURCE_ARGS: tuple = (500, 2000, 250), (1024, 16384, 1024), (128, 512, 32)
	MEDIUM_RANDOM_RESOURCE_ARGS: tuple = (64, 256, 32), (128, 1024, 128), (8, 64, 8)
	LOW_RANDOM_RESOURCE_ARGS: tuple = (2, 8, 1), (8, 64, 8), (1, 4, 1)
	@staticmethod
	def random(cpu: tuple = HIGH_RANDOM_RESOURCE_ARGS[0], ram: tuple = HIGH_RANDOM_RESOURCE_ARGS[1], storage: tuple = HIGH_RANDOM_RESOURCE_ARGS[2]) -> "Resource":
		""" Generate a random resource
		Args:
			cpu		(tuple[int,int,int]):	Min, Max and Step for the CPU, default value means between 50% and 200% with step of 25%
			ram		(tuple[int,int,int]):	Min, Max and Step for the RAM, default value means between 1024MB and 16384MB with step of 1024MB
			storage	(tuple[int,int,int]):	Min, Max and Step for the Storage, default value means between 128GB and 512GB with step of 32GB
		Returns:
			Resource: generated resource with random values
		"""
		r_cpu: int = random_step(*cpu)
		r_ram: int = random_step(*ram)
		r_storage: int = random_step(*storage)
		return Resource(r_cpu, r_ram, r_storage)

