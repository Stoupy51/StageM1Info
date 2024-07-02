
# Imports
import random
random.seed(0)

# Coefficient for the calculation of the bandwidth charge when transfering a task from a fog to another
K_BC: float = 5.0

# Quality of Service (QoS) constants
K1: int = 3		# Coefficient for the number of allocated tasks in the QoS
K2: int = 1		# Coefficient for the nodes usage in the QoS
K3: int = 1		# Coefficient for the links load in the QoS


## Constants
FOG_COLOR: tuple = (255, 0, 0, 255)
FOG_SIZE: int = 50
FOG_SHAPE: list[tuple] = [(0, 0), (0, FOG_SIZE), (FOG_SIZE, FOG_SIZE), (FOG_SIZE, 0)]
NB_FOG_NODES: int = 10
RANDOM_DIVIDER: int = 3
PLOT_INTERVAL: int = 1

