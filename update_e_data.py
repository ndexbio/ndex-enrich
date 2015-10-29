__author__ = 'dexter'

# This script is called from the command line to update a persisted e_set
#
# The script reads the configuration file and then updates the specified e_set:
#
# 1. load the e_set.
# 2. query to find the current status of each network in the e_set
# 3. remove current id_sets for networks that are no longer retrieved
# 4. replace id_sets for networks that have been modified
# 5. add id_sets for new networks
# 6. persist the e_set
#
# The optional argument 'rebuild' causes the update to ignore the existing persisted data:
#
# 1. query to find the networks in the e_set
# 2. add the id_set for each network
# 3. persist the e_set
#
# Note that this operation can be performed while the enrichment server is running.
# The enrichment server loads its e_sets at start time

# body

import argparse
import updater
import configuration as conf
import sys

parser = argparse.ArgumentParser(description='update an e_set')

parser.add_argument('eset', action='store')
parser.add_argument('rebuild', action='store')

arg = parser.parse_args()

rebuild = False
if arg.rebuild.lower() is "true":
    rebuild = True

config = conf.EServerConfiguration()

# Load the testing configuration
config.load(True)

if len(config.e_set_configs) is 0:
    print "No enrichment sets are specified in the configuration"
    sys.exit()

e_set_config_to_update = config.get_e_set_config(arg.eset)

if not e_set_config_to_update:
    print "No enrichment set in configuration file for name: " + arg.eset
    print "The configured enrichment sets are:"
    for e_set_config in config.e_set_configs:
        print str(e_set_config)
    sys.exit()

updater.update(e_set_config_to_update, rebuild)

print "Update complete"




