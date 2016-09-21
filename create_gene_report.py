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
import gene_report
import ndex_access
import term2gene_mapper

class report_generator():
    def __init__(self):
        # a map to hold the term to gene mapping to speed the query.
        self.term_mapper = term2gene_mapper.Term2gene_mapper()

    # for each e_set in the configuration:
    #       for each network specified in the e_set:
    #           get the network from the specified NDEx
    #           analyze the identifiers in each network and normalize to genes using the mygeneinfo service
    #           add each gene-network pair to the report
    # output the report to a file in the gene_reports directory when all networks have been processed
    #  (the name of the file is <configuration name>_gene_report.txt

    def create_gene_report(self,config):
        report = gene_report.GeneReport(config.name)
        term_to_gene_map = {}

        for e_set_config in config.e_set_configs:
            self.process_e_set_for_report(e_set_config, report, term_to_gene_map)
        return report

    def process_e_set_for_report(self,e_set_config, report, term_to_gene_map):
        ndex = ndex_access.NdexAccess(e_set_config.ndex, username=e_set_config.username, password=e_set_config.password)
        # Find the networks
        networks = ndex.find_networks(e_set_config)
        print "Found " + str(len(networks)) + " networks for gene report"
        for network in networks:
            self.process_network_for_report(network, e_set_config, report, ndex, term_to_gene_map)

    def process_network_for_report(self,network, e_set_config, report, ndex, term_to_gene_map):
        network_id = network.get("externalId")
        network_name = network.get("name")
        print " - " + network_name + " : " + network_id
        #    genes = ndex.get_genes(network_id, term_to_gene_map)
        node_table = ndex.get_nodes_from_cx(network_id)

        for node_id, node in node_table.items():
            if "represents" in node:
                represents_id = node["represents"]
                gene = self.term_mapper.gene_symbol_and_id_from_term(represents_id)
                if gene != None :
                    report.add_gene_network_pair(gene.id, gene.symbol,  network_id, network_name, e_set_config.name)
                    continue
            # otherwise check aliases
            if "aliases" in node:
                alias_ids = node.get('aliases')
                found_alias = False
                for alias_id in alias_ids:
                    gene = self.term_mapper.gene_symbol_and_id_from_term(alias_id)
                    if gene != None:
                        report.add_gene_network_pair( gene.id, gene.symbol, network_id, network_name, e_set_config.name)
                        found_alias = True
                        break
                if found_alias:
                    continue

            # then, try using name
            if "name" in node:
                names = node.get("name")
                foundGeneInName = False
                for node_name in names :
                    if len(node_name) < 40:
                        gene = self.term_mapper.gene_symbol_and_id_from_term(node_name)
                        if gene != None:
                            report.add_gene_network_pair(gene.id, gene.symbol, network_id, network_name, e_set_config.name)
                            foundGeneInName = True
                            break
                if foundGeneInName :
                    continue

            if "functionTerm" in node:
                self.genes_from_function_term(node["functionTerm"], node_id)


    def genes_from_function_term(self, function_term, network_id, network_name, e_set_name):
        # if it is a function term, process all genes mentioned
        for parameter in function_term['args']:
            if type(parameter) == 'str':
                gene = self.term_mapper.gene_symbol_and_id_from_term(parameter)
                if gene != None:
                    report.add_gene_network_pair(gene.id, gene.symbol, network_id, network_name, e_set_name)
            else:
                self.genes_from_function_term(parameter,network_id,network_name, e_set_name)

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

reporter = report_generator()

report = reporter.create_gene_report(config)
storage.save_gene_report(report)

print "gene report complete"





