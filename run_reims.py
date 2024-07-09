
# Imports
from src.main import run_simulation
from src.utils import *
from src.resources import Resource
from multiprocessing import Pool

# Constants
SEED: int = 0
SUMO_CONFIG: str = "Reims/osm.sumocfg"
VISUAL_CENTER: tuple[int,int] = (1200, 1600)
DEBUG_PERF: bool = False
AUTO_START: bool = True		# --start
AUTO_QUIT: bool = True		# --quit-on-end
OPEN_GUI: bool = True		# "sumo-gui" when True, "sumo" when False

# Assign modes: uncomment to enable simulation
ASSIGN_MODES: list[tuple[AssignMode, str, tuple[int,int,int]]] = [
	# (AssignMode.ALL,								"medium", Resource.MEDIUM_RANDOM_RESOURCE_ARGS),
	# (AssignMode(neighbours = True, cost = True),	"medium", Resource.MEDIUM_RANDOM_RESOURCE_ARGS),
	# (AssignMode(neighbours = True),					"medium", Resource.MEDIUM_RANDOM_RESOURCE_ARGS),
	# (AssignMode(),									"medium", Resource.MEDIUM_RANDOM_RESOURCE_ARGS),

	# (AssignMode.ALL,								"high", Resource.HIGH_RANDOM_RESOURCE_ARGS),
	(AssignMode(neighbours = True, cost = True),	"high", Resource.HIGH_RANDOM_RESOURCE_ARGS),
	# (AssignMode(neighbours = True),					"high", Resource.HIGH_RANDOM_RESOURCE_ARGS),
	# (AssignMode(),									"high", Resource.HIGH_RANDOM_RESOURCE_ARGS),

	# (AssignMode.ALL,								"extreme", Resource.EXTREME_RANDOM_RESOURCE_ARGS),
	# (AssignMode(neighbours = True, cost = True),	"extreme", Resource.EXTREME_RANDOM_RESOURCE_ARGS),
	# (AssignMode(neighbours = True),					"extreme", Resource.EXTREME_RANDOM_RESOURCE_ARGS),
	# (AssignMode(),									"extreme", Resource.EXTREME_RANDOM_RESOURCE_ARGS),
]

# Disable the GUI opening if too many window
if OPEN_GUI and len(ASSIGN_MODES) > 4:
	OPEN_GUI = False

# Thread method
def thread(args: tuple[AssignMode, str, tuple[int,int,int]]) -> dict:
	return run_simulation(
		simulation_name = f"outputs/{args[1]}/Reims_{args[0].name}",
		assign_mode = args[0],
		sumo_config = SUMO_CONFIG,
		visual_center = VISUAL_CENTER,
		seed = SEED,
		debug_perf = DEBUG_PERF,
		auto_start = AUTO_START,
		auto_quit = AUTO_QUIT,
		open_gui = OPEN_GUI,
		fog_resources = args[2]
	)

# Main method
if __name__ == "__main__":

	# Run the simulation in multiple threads
	NB_THREADS: int = len(ASSIGN_MODES)
	with Pool(processes = NB_THREADS) as pool:
		evaluations_per_mode: list[dict] = pool.map(thread, ASSIGN_MODES)

	# For each preset type, process the results
	USED_ASSIGN_FOLDERS: list[str] = [folder for mode, folder, args in ASSIGN_MODES]	# Used to generate the output folders
	for folder in USED_ASSIGN_FOLDERS:
		evaluations: list[dict] = [x for x in evaluations_per_mode if x["folder"] == folder]
		process_simulation_evaluations(evaluations)

