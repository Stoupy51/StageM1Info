
# Imports
from src.main import run_simulation
from src.utils import AssignMode

# Constants
SEED: int = 0
SUMO_CONFIG: str = "Reims/osm.sumocfg"
VISUAL_CENTER: tuple[int,int] = (1200, 1600)
DEBUG_PERF: bool = False

# Start simulation
run_simulation(
	simulation_name = "Reims",
	assign_mode = AssignMode.ALL,
	sumo_config = SUMO_CONFIG,
	visual_center = VISUAL_CENTER,
	seed = SEED,
	debug_perf = DEBUG_PERF
)

