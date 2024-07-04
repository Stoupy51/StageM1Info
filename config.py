
# Imports
import random
random.seed(0)

# Coefficient for the calculation of the bandwidth charge when transfering a task from a fog to another
K_BANDWIDTH_CHARGE: float = 5.0

# Quality of Service (QoS) constants
K_TASKS: float = 3.0		# Coefficient for the number of allocated tasks in the QoS
K_NODES: float = 1.0		# Coefficient for the nodes usage
K_LINKS: float = 1.0		# Coefficient for the links load
K_COST: float = 0.5			# Coefficient for the cost of the tasks multiplied by the distance from the vehicle


## Constants
FOG_COLOR: tuple = (255, 0, 0, 255)
FOG_SIZE: int = 50
FOG_SHAPE: list[tuple] = [(0, 0), (0, FOG_SIZE), (FOG_SIZE, FOG_SIZE), (FOG_SIZE, 0)]
NB_FOG_NODES: int = 10
MAX_NEIGHBOURS: int = 3
RANDOM_DIVIDER: int = 3
PLOT_INTERVAL: int = 1

# Plot resolution
DPI_MULTIPLIER = 2

