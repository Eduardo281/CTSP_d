import os
import re
import json

import PATHS

def read_instance(instance_name: str):
    """Read an instance file in .csv format and return its data in a dict.
    
    Parameters
    ----------
    instance_name : str
        Name of the instance to be read.
    
    Returns
    -------
    dict
        Instance file data.
    """
    return json.load(open(os.path.join(PATHS.INSTANCES_FOLDER, instance_name), "r"))

def load_small_random_instances_list():
    """Build and return a list with all the small random instances filenames."""
    return [
        item for item in os.listdir(PATHS.INSTANCES_FOLDER) 
            if ("berlin52-R-" in item or "swiss42-R-" in item)
    ]

def load_small_clustered_instances_list():
    """Build and return a list with all the small clustered instances filenames."""
    return [
        item for item in os.listdir(PATHS.INSTANCES_FOLDER) 
            if ("berlin52-C-" in item or "swiss42-C-" in item)
    ]

def load_100_vertices_random_instances_list():
    """Build and return a list with all the 100 vertices random instances filenames."""
    pattern = re.compile("kro.100-R-")
    return [
        item for item in os.listdir(PATHS.INSTANCES_FOLDER) 
            if pattern.match(item)
    ]

def load_100_vertices_clustered_instances_list():
    """Build and return a list with all the 100 vertices clustered instances filenames."""
    pattern = re.compile("kro.100-C-")
    return [
        item for item in os.listdir(PATHS.INSTANCES_FOLDER) 
            if pattern.match(item)
    ]

def load_200_vertices_random_instances_list():
    """Build and return a list with all the 200 vertices random instances filenames."""
    pattern = re.compile("kro.200-R-")
    return [
        item for item in os.listdir(PATHS.INSTANCES_FOLDER) 
            if pattern.match(item)
    ]

def load_200_vertices_clustered_instances_list():
    """Build and return a list with all the 200 vertices clustered instances filenames."""
    pattern = re.compile("kro.200-C-")
    return [
        item for item in os.listdir(PATHS.INSTANCES_FOLDER) 
            if pattern.match(item)
    ]
