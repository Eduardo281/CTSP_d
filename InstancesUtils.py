import os
import re
import json
import datetime

import PATHS

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

def export_results(model, datetime_on_filename=True):
    data = dict()
    
    ### INSTANCE_NAME:
    data["name"] = model.data["instance_name"]

    ### DATETIME:
    data["datetime"] = datetime.datetime.now().isoformat()

    ### OBJ VAL:
    data["objective_value"] = model.model.ObjVal

    ### RUNTIME:
    data["runtime"] = model.model.Runtime

    ### GAP:
    data["GAP"] = model.model.MIPGap

    ### ROUTE:
    # TODO

    filename = data["name"]
    if(datetime_on_filename):
        filename += "_" + datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    filename += ".json"

    f = open(os.path.join(PATHS.RESULTS_FOLDER, filename), "w")
    json.dump(data, f)
    f.close()
