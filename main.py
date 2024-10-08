#!/usr/bin/python3

from InstancesUtils import *
from MiscUtils import *
from UserInputs import *

print_solution_log(SOLUTION_LOG_LEVEL, 1, "Starting Solution Process!")

model = create_solvers_aliases_dict()

solver_count = 1
for solver_alias in SOLVERS_LIST:
    print_solution_log(SOLUTION_LOG_LEVEL, 2, f"Actual Solver: {solver_alias} ({solver_count}/{len(SOLVERS_LIST)})")
    if(USE_SOLVED_INSTANCES_LIST):
        if(not os.path.isfile(get_solved_instances_list_path(solver_alias))):
            create_solved_instances_list(solver_alias)
            solved_instances_list = set()
        else:
            solved_instances_list = load_solved_instances_list(solver_alias)
    instances_count = 1
    for instance in INSTANCES_LIST:
        print_solution_log(SOLUTION_LOG_LEVEL, 3, f"Solving instance {instance} ({instances_count}/{len(INSTANCES_LIST)})...")
        if(USE_SOLVED_INSTANCES_LIST):
            if instance in solved_instances_list:
                print_solution_log(SOLUTION_LOG_LEVEL, 4, f"Skipped solved instance {instance}!")
                instances_count += 1
                continue
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
        if(USE_SOLVED_INSTANCES_LIST):
            append_to_solved_instances_list(solver_alias, instance)
            print_solution_log(SOLUTION_LOG_LEVEL, 4, f"Stored {instance} to {solver_alias} solved instances list!")
    solver_count += 1

print_solution_log(SOLUTION_LOG_LEVEL, 1, "Finished Solution Process!")
