
# Imports
from src.main import run_simulation
from src.utils import *
from multiprocessing import Pool

# Constants
SEED: int = 0
SUMO_CONFIG: str = "Reims/osm.sumocfg"
VISUAL_CENTER: tuple[int,int] = (1200, 1600)
DEBUG_PERF: bool = False
AUTO_START: bool = True		# --start
AUTO_QUIT: bool = True		# --quit-on-end
OPEN_GUI: bool = True		# "sumo-gui" when True, "sumo" when False

# Thread method
def thread(assign_mode: AssignMode) -> dict:
	return run_simulation(
		simulation_name = f"outputs/Reims_{assign_mode.name}",
		assign_mode = assign_mode,
		sumo_config = SUMO_CONFIG,
		visual_center = VISUAL_CENTER,
		seed = SEED,
		debug_perf = DEBUG_PERF,
		auto_start = AUTO_START,
		auto_quit = AUTO_QUIT,
		open_gui = OPEN_GUI
	)

# Main method
if __name__ == "__main__":
	assign_modes: list[AssignMode] = [
		AssignMode(),
		AssignMode(neighbours = True),
		AssignMode(neighbours = True, cost = True),
		AssignMode.ALL
	]
	with Pool(processes = len(assign_modes)) as pool:
		evaluations_per_mode: list[dict] = pool.map(thread, assign_modes)
	process_simulation_evaluations(evaluations_per_mode)

