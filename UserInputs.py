from InstancesUtils import *

###########################################
#               USER INPUTS               #
###########################################

GUROBI_PARAMETERS = {
    "MAX_RUNTIME": 3600,
    "PRINT_LOG": False
}

EXPORT_SOLUTION_PARAMETERS = {
    "EXPORT_SOLUTION": True,
    "DATETIME_ON_FILENAME": False
}

USE_SOLVED_INSTANCES_LIST = True

SOLUTION_LOG_LEVEL = 3

MODELS_LIST = ["MTZ2", "GP2", "SSB2", "SST2"]

INSTANCES_LIST = [
    "swiss42-C-3-0-c.json",
    "swiss42-R-5-0-c.json",
    "kroE100-R-5-0-a.json",
    "kroE100-C-5-0-a.json",
]
