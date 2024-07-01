
# Imports
from src.main import run_simulation
from src.utils import AssignMode
from multiprocessing import Pool

# Constants
SEED: int = 0
SUMO_CONFIG: str = "Reims/osm.sumocfg"
VISUAL_CENTER: tuple[int,int] = (1200, 1600)
DEBUG_PERF: bool = False
AUTO_START: bool = True		# --start
AUTO_QUIT: bool = True		# --quit-on-end

# Thread method
def thread(assign_mode: AssignMode) -> list:
	return run_simulation(
		simulation_name = f"Reims_{assign_mode.name}",	assign_mode = assign_mode,
		sumo_config = SUMO_CONFIG,						visual_center = VISUAL_CENTER,
		seed = SEED,									debug_perf = DEBUG_PERF,
		auto_start = AUTO_START,						auto_quit = AUTO_QUIT
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
		evaluations_per_mode: list[list[float]] = pool.map(thread, assign_modes)

	# Generate a graph of the evaluations over time for each assign mode
	from matplotlib import pyplot as plt
	for i, assign_mode in enumerate(assign_modes):
		plt.plot(evaluations_per_mode[i], label = assign_mode.name)
	plt.title("Evaluations over time for each assign mode")
	plt.legend()
	plt.xlabel("Simulation Step")
	plt.ylabel("Evaluation")
	plt.savefig("outputs/Reims_evaluations_over_time.png")

