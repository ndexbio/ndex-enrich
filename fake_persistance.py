__author__ = 'dexter'

# This fake persistance system just uses the local directory and
# has a structure of:
#
# e_sets
#       /e_set_name
#                  /id_set_name.json
#

import data_model as dm

def save_id_set(e_set_name, id_set):
    return False

def remove_id_set(e_set_name, id_set_name):
    return False

def load_id_set(e_set_name, id_set_name):
    return False

