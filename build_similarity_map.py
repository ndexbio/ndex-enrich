__author__ = 'dexter'


import argparse
import similarity_map_utils as smu

parser = argparse.ArgumentParser(description='build a similarity map from files in an e_set directory')

parser.add_argument('map_name', action='store')

parser.add_argument('e_set_dir', action='store')

parser.add_argument('e_set_name', action='store')

parser.add_argument('min_sub', action='store', type=float)

arg = parser.parse_args()

smu.create_similarity_map_from_enrichment_files(arg.map_name, arg.e_set_dir, arg.e_set_name, arg.min_sub)

print "Map complete"


