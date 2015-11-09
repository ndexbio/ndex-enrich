__author__ = 'dexter'

# This script is called from the command line to create a gene report for a specified e_set
#
# Summary:
#
# load the specified configuration file
# for each e_set in the configuration:
#       for each network specified in the e_set:
#           get the network from the specified NDEx
#           analyze the identifiers in each network and normalize to genes using the mygeneinfo service
#           add each gene-network pair to the report
# output the report to a file in the gene_reports directory when all networks have been processed
#  (the name of the file is <configuration name>_gene_report.txt
#
# usage:
#
# python create_gene_report.py config_example

# body

import argparse
import updater
import configuration as conf
import sys
import fake_persistence as storage

parser = argparse.ArgumentParser(description='update an e_set')

parser.add_argument('config', action='store')
parser.add_argument('--test', dest='test', action='store_const',
                    const=True, default=False,
                    help='use the test configuration')

arg = parser.parse_args()

config = conf.EServiceConfiguration()

# Load the configuration for the specified
config.load(arg.config, test_mode=arg.test)

if len(config.e_set_configs) is 0:
    print "No enrichment sets are specified in the configuration"
    sys.exit()

report = updater.create_gene_report(config)
storage.save_gene_report(report)

print "gene report complete"


