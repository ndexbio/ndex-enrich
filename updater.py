__author__ = 'dexter'

import data_model as dm
import ndex_access
import fake_persistence as storage
import gene_report

def update(e_set_config, rebuild = False):

        # Create a fresh data model
        e_data = dm.EnrichmentData("e_sets")

        # Load the specified e_set, if it exists
        print "Updating e_set: " + e_set_config.name
        e_set = e_data.add_e_set(e_set_config.name)
        storage.ensure_e_set_dir(e_set_config.name)
        e_set.load()

        na = ndex_access.NdexAccess(e_set_config.ndex)

        # Find the candidate networks
        networks = na.find_networks(e_set_config)

        print "Found " + str(len(networks)) + " networks"

        # TODO: remove e_sets that are not found in the query

        # Figure out which ones to update
        networks_to_update = {}
        if rebuild:
            for network in networks:
                network_id = network.get("externalId")
                network_name = network.get("name")
                networks_to_update[network_name] = network_id
        else:
            for network in networks:
                network_id = network.get("externalId")
                network_name = network.get("name")
                modification_date = network.get("modificationDate")
                id_set = e_set.get_id_set_by_network_id(network_id)
                if id_set:
                    if not id_set.modificationDate == modification_date:
                        networks_to_update[network_name] = network_id
                else:
                    networks_to_update[network_name] = network_id

        print "Updating " + str(len(networks_to_update.keys())) + " networks"
        # Do the updates
        for network_name, network_id in networks_to_update.iteritems():
            print network_name + " : " + network_id
            ids = na.get_ids(e_set_config.id_prefix, network_id)
            id_set_dict = {
                "name": network_name,
                "ids": ids,
                "network_id": network_id,
                "ndex" : e_set_config.ndex,
                "e_set" : e_set_config.name
            }
            id_set = dm.IdentifierSet(id_set_dict)
            e_set.add_id_set(id_set)

        # now that the updated e_set is ready to save, clear the old cached data
        storage.remove_all_id_sets(e_set_config.name)

        print "Saving e_set with " + str(len(e_set.get_id_set_names())) + " id_sets"
        e_set.save()


# for each e_set in the configuration:
#       for each network specified in the e_set:
#           get the network from the specified NDEx
#           analyze the identifiers in each network and normalize to genes using the mygeneinfo service
#           add each gene-network pair to the report
# output the report to a file in the gene_reports directory when all networks have been processed
#  (the name of the file is <configuration name>_gene_report.txt

def create_gene_report(config):
    report = gene_report.GeneReport(config.name)
    term_to_gene_map = {}
    for e_set_config in config.e_set_configs:
        process_e_set_for_report(e_set_config, report, term_to_gene_map)
    return report

def process_e_set_for_report(e_set_config, report, term_to_gene_map):
    ndex = ndex_access.NdexAccess(e_set_config.ndex)
    # Find the networks
    networks = ndex.find_networks(e_set_config)
    for network in networks:
        process_network_for_report(network, e_set_config, report, ndex, term_to_gene_map)

def process_network_for_report(network, e_set_config, report, ndex, term_to_gene_map):
    network_id = network.get("externalId")
    network_name = network.get("name")
    print " - " + network_name + " : " + network_id
    genes = ndex.get_genes(network_id, term_to_gene_map)
    for gene in genes:
        print "adding gene " + gene.symbol
        report.add_gene_network_pair(gene.symbol, gene.id, network_id, network_name, e_set_config.name)


