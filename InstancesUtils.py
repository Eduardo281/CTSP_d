import os
import json
import re

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
