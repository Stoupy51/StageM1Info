
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
	
	# Extract all evaluations labels
	import os
	from matplotlib import pyplot as plt
	evaluations_labels: list[str] = [key for key in evaluations_per_mode[0].keys() if key not in ["folder", "name"]]

	# For each assign mode, generate its content
	for data in evaluations_per_mode:
		os.makedirs(data["folder"], exist_ok = True)
		folder: str = data["folder"]
		name: str = data["name"]
		for label in evaluations_labels:
			plt.clf()
			plt.plot(data[label])
			plt.title(f"{label} over time - {name}")
			plt.xlabel("Simulation Step")
			plt.ylabel(label)
			plt.savefig(f"{folder}/{label}.png")
		
		# Save data
		with open(f"{folder}/data.json", "w", encoding = "utf-8") as file:
			super_json_dump(data, file, max_level = 2)

	# For each label, generate graphs comparing each assign mode
	for label in evaluations_labels:
		data: list[list[float]] = [assign_mode[label] for assign_mode in evaluations_per_mode]
		plt.clf()
		for i, mode in enumerate(evaluations_per_mode):
			plt.plot(data[i], label = mode["name"])
		plt.title(f"{label} over time")
		plt.legend()
		plt.xlabel("Simulation Step")
		plt.ylabel(label)
		plt.savefig(f"outputs/{label}_comparison.png")

