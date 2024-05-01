#!/usr/bin/python3

from InstancesUtils import *
from MiscUtils import *
from UserInputs import *

print_solution_log(SOLUTION_LOG_LEVEL, 1, "Starting Solution Process!")

model = create_solvers_aliases_dict()

for solver_alias in SOLVERS_LIST:
    print_solution_log(SOLUTION_LOG_LEVEL, 2, f"Actual Solver: {solver_alias}")
    instances_count = 1
    for instance in INSTANCES_LIST:
        print_solution_log(SOLUTION_LOG_LEVEL, 3, f"Solving instance {instance} ({instances_count}/{len(INSTANCES_LIST)})...")
        data = read_instance(instance)
        solver = model[solver_alias](data)
        solver.solve(
            time=GUROBI_PARAMETERS["MAX_RUNTIME"],
            log=GUROBI_PARAMETERS["PRINT_LOG"]
        )
        instances_count += 1
        if(EXPORT_SOLUTION_PARAMETERS["EXPORT_SOLUTION"]):
            export_results(
                solver,
                EXPORT_SOLUTION_PARAMETERS["DATETIME_ON_FILENAME"]
            )
