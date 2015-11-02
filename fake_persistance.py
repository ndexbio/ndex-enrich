__author__ = 'dexter'

from os import listdir, makedirs
from os.path import isfile, isdir, join, abspath, dirname, exists, basename, splitext

# This fake persistance system just uses the local directory and
# has a structure of:
#
# e_sets
#       /e_set_name
#                  /id_set_name.json
#

import data_model as dm
import json
from os import remove

def e_set_dir_name(e_set_name):
    current_directory = dirname(abspath(__file__))
    return join(current_directory, "e_sets", e_set_name)

def e_data_dir_name():
    current_directory = dirname(abspath(__file__))
    return join(current_directory, "e_sets")

def e_set_exists(e_set_name):
    return isdir(e_set_dir_path(e_set_name))

def e_set_dir_path(e_set_name):
    return join(e_data_dir_name(), e_set_name)

def get_e_set_names():
    return listdir(e_data_dir_name())

def get_id_set_file_names(e_set_name):
    path = e_set_dir_name(e_set_name)
    return listdir(path)

def ensure_e_set_dir(e_set_name):
    path = e_set_dir_path(e_set_name)
    if not e_set_exists(e_set_name):
        print "Creating " + str(path)
        makedirs(path)
    return path

def save_id_set(e_set_name, id_set):
    e_set_dir = ensure_e_set_dir(e_set_name)
    filename = join(e_set_dir, id_set.name + ".json")
    file = open(filename, "w")
    json.dump(id_set.to_dict(), file)
    file.close()

def save_e_set(e_set, e_set_name):
    for id_set_name, id_set in e_set.id_set_map:
        save_id_set(e_set_name, id_set)

def remove_id_set(e_set_name, id_set_name):
    e_set_dir = e_set_dir_name(e_set_name)
    filename = join(e_set_dir, id_set_name + ".json")
    remove(filename)

def remove_all_id_sets(e_set_name):
    dirpath = e_set_dir_name(e_set_name)
    for filename in listdir(dirpath):
        path = join(dirpath, filename)
        remove(path)

def get_id_set_data(e_set_name, id_set_file_name):
    base = basename(id_set_file_name)
    name = splitext(base)[0]
    e_set_dir = e_set_dir_name(e_set_name)
    filename = join(e_set_dir, name + ".json")
    file = open(filename, "r")
    data = json.load(file)
    file.close()
    return data

def save_id_set_dict(e_set_name, id_set_id, id_set_dict):
    e_set_dir = ensure_e_set_dir(e_set_name)
    filename = join(e_set_dir, id_set_id + ".json")
    file = open(filename, "w")
    json.dump(id_set_dict, file)
    file.close()

def get_e_set_configs(name="config"):
    current_directory = dirname(abspath(__file__))
    filename = join(current_directory, "e_service_configuration", name + ".json")
    file = open(filename, "r")
    data = json.load(file)
    file.close()
    return data



