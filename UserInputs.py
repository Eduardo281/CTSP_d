###############################
#         USER INPUTS         #
###############################

GUROBI_PARAMETERS = {
    "MAX_RUNTIME": 3600,
    "PRINT_LOG": False
}

EXPORT_SOLUTION_PARAMETERS = {
    "EXPORT_SOLUTION": True,
    "DATETIME_ON_FILENAME": False
}

SOLUTION_LOG_LEVEL = 3

SOLVERS_LIST = ["MTZ2", "H2020"]

INSTANCES_LIST = [
    "berlin52-C-3-0-a.json", 
    "berlin52-C-5-1-c.json",
    "swiss42-C-5-0-b.json",
    "swiss42-C-3-0-c.json",
    "swiss42-C-3-1-a.json"
]
