__author__ = 'dexter'

import data_model as dm
import ndex_access
import fake_persistence as storage

def update(e_set_config, rebuild = False):

        # Create a fresh data model
        e_data = dm.EnrichmentData("e_sets")

        # Load the specified e_set, if it exists
        print "Updating e_set: " + e_set_config.name
        e_set = e_data.add_e_set(e_set_config.name)
        storage.ensure_e_set_dir(e_set_config.name)
        e_set.load()

        na = ndex_access.NdexAccess(e_set_config.ndex, e_set_config.account, e_set_config.password)

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
                modification_date = network.get("modificationTime")
                id_set = e_set.get_id_set_by_network_id(network_id)
                if id_set:
                    if not id_set.modificationDate == modification_date:
                        networks_to_update[network_name] = network_id
                else:
                    networks_to_update[network_name] = network_id

        print "Updating " + str(len(networks_to_update.keys())) + " networks"
        # Do the updates
        counter = 0
        for network_name, network_id in networks_to_update.iteritems():
            print network_name.encode('ascii','ignore') + " : " + network_id.encode('ascii','ignore')
            ids = na.get_genes_cx( network_id)
            id_set_dict = {
                "name": network_name,
                "ids": ids,
                "network_id": network_id,
                "ndex" : e_set_config.ndex,
                "e_set" : e_set_config.name
            }
            id_set = dm.IdentifierSet(id_set_dict)
            e_set.add_id_set(id_set)
            counter +=1
            print str(counter) + " networks indexed."

        # now that the updated e_set is ready to save, clear the old cached data
        storage.remove_all_id_sets(e_set_config.name)

        print "Saving e_set with " + str(len(e_set.get_id_set_names())) + " id_sets"
        e_set.save()


