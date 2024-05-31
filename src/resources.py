
# Resource class
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

