from InstancesUtils import *
from MiscUtils import MODELS_ENUM

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

MODELS_LIST = [
    MODELS_ENUM.MTZ2,
    MODELS_ENUM.GP2
]

INSTANCES_LIST = [
    "swiss42-C-3-0-a.json",
    "swiss42-R-5-0-a.json",
    "swiss42-R-3-0-b.json",
    "swiss42-C-5-0-b.json"
]
