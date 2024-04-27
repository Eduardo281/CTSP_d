import os
import re
import sys
import json
import datetime
import platform

import PATHS

import gurobipy as gp

def read_instance(instance_name):
    return json.load(open(os.path.join(PATHS.INSTANCES_FOLDER, instance_name), "r"))

def load_small_random_instances_list():
    return [
        item for item in os.listdir(PATHS.INSTANCES_FOLDER) 
            if ("berlin52-R-" in item or "swiss42-R-" in item)
    ]

def load_small_clustered_instances_list():
    return [
        item for item in os.listdir(PATHS.INSTANCES_FOLDER) 
            if ("berlin52-C-" in item or "swiss42-C-" in item)
    ]

def load_100_vertices_random_instances_list():
    pattern = re.compile("kro.100-R-")
    return [
        item for item in os.listdir(PATHS.INSTANCES_FOLDER) 
            if pattern.match(item)
    ]

def load_100_vertices_clustered_instances_list():
    pattern = re.compile("kro.100-C-")
    return [
        item for item in os.listdir(PATHS.INSTANCES_FOLDER) 
            if pattern.match(item)
    ]

def load_200_vertices_random_instances_list():
    pattern = re.compile("kro.200-R-")
    return [
        item for item in os.listdir(PATHS.INSTANCES_FOLDER) 
            if pattern.match(item)
    ]

def load_200_vertices_clustered_instances_list():
    pattern = re.compile("kro.200-C-")
    return [
        item for item in os.listdir(PATHS.INSTANCES_FOLDER) 
            if pattern.match(item)
    ]

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

    filename = data["instance_name"]
    if(datetime_on_filename):
        filename += "_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    filename += ".json"

    f = open(os.path.join(PATHS.RESULTS_FOLDER, filename), "w")
    json.dump(data, f)
    f.close()
