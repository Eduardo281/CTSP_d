import os
import sys
import json
import datetime
import platform

import gurobipy as gp

import PATHS

from BasicModels import MTZ_CTSP_d_Model, GP_CTSP_d_Model, SSB_CTSP_d_Model, SST_CTSP_d_Model
from ValidInequalitiesBaseClass import VI_MTZ_CTSP_d_Model, VI_GP_CTSP_d_Model, VI_SSB_CTSP_d_Model, VI_SST_CTSP_d_Model, VI_Ha_CTSP_d_Model

AVAILABLE_MODELS_LIST = [
    MTZ_CTSP_d_Model, GP_CTSP_d_Model, SSB_CTSP_d_Model, SST_CTSP_d_Model,
    VI_MTZ_CTSP_d_Model, VI_GP_CTSP_d_Model, VI_SSB_CTSP_d_Model, VI_SST_CTSP_d_Model,
    VI_Ha_CTSP_d_Model
]

def create_solvers_aliases_dict():
    return {
        model.alias: model
        for model in AVAILABLE_MODELS_LIST
    }

def export_results(
        model, 
        datetime_on_filename=True):
    data = dict()
    
    data["instance_name"] = model.data["instance_name"]
    data["solver_alias"] = model.alias
    data["python_version"] = sys.version
    data["gurobi_version"] = "Gurobi " + ".".join([str(val) for val in gp.gurobi.version()])
    data["platform"] = platform.platform()
    data["datetime"] = datetime.datetime.now().isoformat()

    if(model.model.SolCount > 0):
        data["objective_value"] = model.model.ObjVal
        data["runtime"] = model.model.Runtime
        data["GAP"] = model.model.MIPGap
        data["route"] = model.routeList
        data["x_vars"] = {str(pair): model.x[pair].X for pair in model.x if model.x[pair].X > 0.5}
        if(len(model.u) > 0):
            data["u_vars"] = {str(index): model.u[index].X for index in model.u if model.u[index].X > 0.5}
        if(len(model.y) > 0):
            data["y_vars"] = {str(pair): model.y[pair].X for pair in model.y if model.y[pair].X > 0.5}

    filename = data["solver_alias"] + "_" + data["instance_name"]
    if(datetime_on_filename):
        filename += "_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    filename += ".json"

    f = open(os.path.join(PATHS.RESULTS_FOLDER, filename), "w")
    json.dump(data, f)
    f.close()

def print_solution_log(solution_log_level, msg_log_level, msg):
    LOG_TAB = "    "
    if(msg_log_level <= solution_log_level):
        print((msg_log_level-1)*LOG_TAB + msg)

def get_solved_instances_list_path(solver_alias):
    return os.path.join(PATHS.SOLVED_INSTANCES_FOLDER, solver_alias)

def create_solved_instances_list(solver_alias):
    if(not os.path.isfile(get_solved_instances_list_path(solver_alias))):
        open(get_solved_instances_list_path(solver_alias), "w").close()

def load_solved_instances_list(solver_alias):
    if(os.path.isfile(get_solved_instances_list_path(solver_alias))):
        f = open(get_solved_instances_list_path(solver_alias), "r")
        return set([line.strip() for line in f.readlines()])
    
def append_to_solved_instances_list(solver_alias, instance_name):
    if(os.path.isfile(get_solved_instances_list_path(solver_alias))):
        f = open(get_solved_instances_list_path(solver_alias), "a")
        f.write(instance_name+"\n")
        f.close()
