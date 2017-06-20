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

#
# usage:
#
# python update_e_data.py config_example --rebuild

# body
import argparse
import updater
import configuration as conf
import sys

parser = argparse.ArgumentParser(description='update an e_set')

parser.add_argument('config', action='store')
parser.add_argument('--test', dest='test', action='store_const',
                    const=True, default=False,
                    help='use the test configuration')

parser.add_argument('--rebuild', dest='rebuild', action='store_const',
                    const=True, default=False,
                    help='rebuild all the cached e_sets')

arg = parser.parse_args()

# nci_pid_preview e_sets nci_pid_preview 0.02
config = conf.EServiceConfiguration()

# Load the testing configuration
config.load(arg.config)

if len(config.e_set_configs) is 0:
    print "No enrichment sets are specified in the configuration"
    sys.exit()

for e_set_config in config.e_set_configs:

    updater.update(e_set_config, arg.rebuild)

print "Update complete"



# if not e_set_config_to_update:
#     print "No enrichment set in configuration file for name: " + arg.eset
#     print "The configured enrichment sets are:"
#     for e_set_config in config.e_set_configs:
#         print str(e_set_config)
#     sys.exit()
