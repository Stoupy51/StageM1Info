
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
OPEN_GUI: bool = False		# "sumo-gui" when True, "sumo" when False

# Thread method
def thread(args: tuple[AssignMode, str, tuple[int,int,int]]) -> dict:
	assign_mode: AssignMode = args[0]
	folder: str = args[1]
	fog_resources: tuple[int,int,int] = args[2]
	return run_simulation(
		simulation_name = f"outputs/{folder}/Reims_{assign_mode.name}",
		assign_mode = assign_mode,
		sumo_config = SUMO_CONFIG,
		visual_center = VISUAL_CENTER,
		seed = SEED,
		debug_perf = DEBUG_PERF,
		auto_start = AUTO_START,
		auto_quit = AUTO_QUIT,
		open_gui = OPEN_GUI,
		fog_resources = fog_resources
	)

# Main method
if __name__ == "__main__":
	fog_resources_types: list[tuple[str, tuple[int,int,int]]] = [
		("high",	Resource.HIGH_RANDOM_RESOURCE_ARGS),
		("medium",	Resource.MEDIUM_RANDOM_RESOURCE_ARGS),
		("extreme",	Resource.EXTREME_RANDOM_RESOURCE_ARGS),
	]

	nb_modes_per_type: int = 4
	assign_modes: list[tuple[AssignMode, str, tuple[int,int,int]]] = []
	for folder, fog_resources in fog_resources_types:
		assign_modes += [
			(AssignMode.ALL,								folder, fog_resources),
			(AssignMode(neighbours = True, cost = True),	folder, fog_resources),
			(AssignMode(neighbours = True),					folder, fog_resources),
			(AssignMode(),									folder, fog_resources),
		]
	NB_THREADS: int = len(assign_modes)
	#NB_THREADS: int = 1
	with Pool(processes = NB_THREADS) as pool:
		evaluations_per_mode: list[dict] = pool.map(thread, assign_modes)
	
	nb_types: int = len(fog_resources_types)
	for i in range(nb_types):
		start_index: int = i * nb_modes_per_type
		end_index: int = (i + 1) * nb_modes_per_type
		type_results: list[dict] = evaluations_per_mode[start_index:end_index]
		process_simulation_evaluations(type_results)

