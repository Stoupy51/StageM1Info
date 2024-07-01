
# Imports
import random
random.seed(0)

# Coefficient for the calculation of the bandwidth charge when transfering a task from a fog to another
K_BC: float = 5.0

# Quality of Service (QoS) constants
K1: int = 3		# Coefficient for the number of allocated tasks in the QoS
K2: int = 1		# Coefficient for the nodes usage in the QoS
K3: int = 1		# Coefficient for the links load in the QoS

