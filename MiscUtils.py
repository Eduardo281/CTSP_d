import os
import sys
import json
import datetime
import platform

import gurobipy as gp
from typing import Dict, Set
from enum import Enum

import PATHS

from BasicModels import CTSP_d_BaseModel, MTZ_CTSP_d_Model, GP_CTSP_d_Model, SSB_CTSP_d_Model, SST_CTSP_d_Model
from ValidInequalitiesBaseClass import VI_MTZ_CTSP_d_Model, VI_GP_CTSP_d_Model, VI_SSB_CTSP_d_Model, VI_SST_CTSP_d_Model, VI_Ha_CTSP_d_Model

class MODELS_ENUM(Enum):
    """Enum representing the available models"""
    H2020 = "H2020"
    
    MTZ1 = "MTZ1"
    GP1  = "GP1"
    SSB1 = "SSB1"
    SST1 = "SST1"

    MTZ2 = "MTZ2"
    GP2  = "GP2"
    SSB2 = "SSB2"
    SST2 = "SST2"

def create_model(model_type: MODELS_ENUM, data: Dict) -> CTSP_d_BaseModel:
    """Function to build a model using a given input data"""
    if(model_type == MODELS_ENUM.H2020):
        return VI_Ha_CTSP_d_Model(data)
    if(model_type == MODELS_ENUM.MTZ1):
        return MTZ_CTSP_d_Model(data)
    if(model_type == MODELS_ENUM.GP1):
        return GP_CTSP_d_Model(data)
    if(model_type == MODELS_ENUM.SSB1):
        return SSB_CTSP_d_Model(data)
    if(model_type == MODELS_ENUM.SST1):
        return SST_CTSP_d_Model(data)
    if(model_type == MODELS_ENUM.MTZ2):
        return VI_MTZ_CTSP_d_Model(data)
    if(model_type == MODELS_ENUM.GP2):
        return VI_GP_CTSP_d_Model(data)
    if(model_type == MODELS_ENUM.SSB2):
        return VI_SSB_CTSP_d_Model(data)
    if(model_type == MODELS_ENUM.SST2):
        return VI_SST_CTSP_d_Model(data)

def export_results(
        model: CTSP_d_BaseModel, 
        datetime_on_filename: bool=True
    ) -> None:
    """Export the results of a solved instance as a .json file.

    Parameters
    ----------
    model : CTSP_d_BaseModel
        Any of the CTSP-d models available.
    datetime_on_filename : bool, default=True
        Allow to include a date-based information in the exported file name.
        Useful to not overwrite already existing solution files.
    """
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

def print_solution_log(
        solution_log_level: int, 
        msg_log_level: int, 
        msg: str
    ) -> None:
    """Print log messages of the solution process on the terminal.

    Parameters
    ----------
    solution_log_level : int
        Log level input by the user. Lower levels means less detailed 
        information, while higher levels includes a more step-by-step 
        description of the solution process.
        Levels available:
        * 0: No log messages.
        * 1: Prints messages for the start and the end of the solution process.
        * 2: Prints a message for every model change in the process.
        * 3: Prints a message every time an instance starts to be solved.
        * 4: Prints messages for skipped instances and exported solutions.
    msg_log_level : int
        Represents the level of the message in the logging process.
        Msg argument will only be print when msg_log_level <= solution_log_level.
    msg : str
        The message to be printed.
    """
    LOG_TAB = "    "
    if(msg_log_level <= solution_log_level):
        print((msg_log_level-1)*LOG_TAB + msg)

def get_solved_instances_list_path(model_alias: str) -> str:
    """Return the path to the solved instances list of the input model_alias."""
    return os.path.join(PATHS.SOLVED_INSTANCES_FOLDER, model_alias)

def create_solved_instances_list(model_alias: str) -> None:
    """Create the solved instances list file of the input model_alias."""
    if(not os.path.isfile(get_solved_instances_list_path(model_alias))):
        open(get_solved_instances_list_path(model_alias), "w").close()

def load_solved_instances_list(model_alias: str) -> Set[str]:
    """Load the solved instances list of the input model_alias and return it as a set."""
    if(os.path.isfile(get_solved_instances_list_path(model_alias))):
        f = open(get_solved_instances_list_path(model_alias), "r")
        return set([line.strip() for line in f.readlines()])
    
def append_to_solved_instances_list(
        model_alias: str, 
        instance_name: str
    ) -> None:
    """Append instance_name to the solved instances list of the input model_alias."""
    if(os.path.isfile(get_solved_instances_list_path(model_alias))):
        f = open(get_solved_instances_list_path(model_alias), "a")
        f.write(instance_name+"\n")
        f.close()
