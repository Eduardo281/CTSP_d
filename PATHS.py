import os

INSTANCES_FOLDER = os.path.join(".", "Instances")
RESULTS_FOLDER = os.path.join(".", "Results")
SOLVED_INSTANCES_FOLDER = os.path.join(".", "Solved_Instances")

FOLDERS = [
    INSTANCES_FOLDER,
    RESULTS_FOLDER,
    SOLVED_INSTANCES_FOLDER
]

for folder in FOLDERS:
    if not os.path.exists(folder):
        os.mkdir(folder)
