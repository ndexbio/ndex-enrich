__author__ = 'dexter'

# This script is called from the command line to run the enrichment server with the persisted e_sets
#
# The script reads all of the e_sets and then starts the bottle server
#
# The optional argument 'verbose' specifies verbose logging for testing
#

# body

import argparse
import e_server as es

parser = argparse.ArgumentParser(description='run the enrichment server')

parser.add_argument('verbose', action='store')

arg = parser.parse_args()

if arg.verbose.lower() == "true":
    print "Starting enrichment server in verbose mode"
    verbose = True
else:
    print "Starting enrichment server"
    verbose = False

es.run_e_server(verbose)