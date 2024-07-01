
# Imports
from src.main import run_simulation
from src.utils import AssignMode
from multiprocessing import Pool

# Constants
SEED: int = 0
SUMO_CONFIG: str = "Reims/osm.sumocfg"
VISUAL_CENTER: tuple[int,int] = (1200, 1600)
DEBUG_PERF: bool = False

# Thread method
def thread(assign_mode: AssignMode) -> None:
	""" Thread method to run the simulation with the given assign mode
	Args:
		assign_mode	(AssignMode):	Assign mode to use for the simulation steps
	"""
	run_simulation(
		simulation_name = f"Reims_{assign_mode.name}",
		assign_mode = assign_mode,
		sumo_config = SUMO_CONFIG,
		visual_center = VISUAL_CENTER,
		seed = SEED,
		debug_perf = DEBUG_PERF
	)

# Main method
if __name__ == "__main__":

	# All combinations of assign modes
	#assign_modes: list[AssignMode] = AssignMode.get_all_assign_modes()

	# Only the best combinations
	assign_modes: list[AssignMode] = [
		AssignMode(),
		AssignMode(neighbours = True),
		AssignMode(neighbours = True, cost = True),
		AssignMode.ALL
	]

	with Pool(processes = len(assign_modes)) as pool:
		pool.map(thread, assign_modes)

