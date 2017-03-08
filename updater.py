__author__ = 'dexter'

import data_model as dm
import ndex_access
import fake_persistence as storage
import term2gene_mapper

def update(e_set_config, rebuild = False):

        # Create a fresh data model
        e_data = dm.EnrichmentData("e_sets")

        # Load the specified e_set, if it exists
        print "Updating e_set: " + e_set_config.name
        e_set = e_data.add_e_set(e_set_config.name)
        storage.ensure_e_set_dir(e_set_config.name)
        e_set.load()

        na = ndex_access.NdexAccess(e_set_config.ndex, e_set_config.account_name, e_set_config.password)

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
        term_mapper = term2gene_mapper.Term2gene_mapper()
        for network_name, network_id in networks_to_update.iteritems():
            print network_name.encode('ascii','ignore') + " : " + network_id.encode('ascii','ignore')
            node_table = na.get_nodes_from_cx(network_id)
            term_mapper.add_network_nodes(node_table)
            gene_symbols = get_genes_for_network(node_table, term_mapper)
            id_set_dict = {
                "name": network_name,
                "ids": gene_symbols,
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


def get_genes_for_network(node_table, term_mapper, symbols_only=True):
        all_found = []
        all_not_found = []
        for node_id, node in node_table.items():
            found = False
            if "represents" in node:
                represents_id = node["represents"]
                gene = term_mapper.get_gene_from_identifier(represents_id)
                if gene != None:
                    found = True
                    all_found.append({"node_id": node_id, "symbol": gene.symbol, "gene_id":gene.id, "input":represents_id, "type":"represents"})
                    continue
            # otherwise check aliases
            if "alias" in node:
                alias_ids = node.get('alias')
                for alias_id in alias_ids:
                    gene = term_mapper.get_gene_from_identifier(alias_id)
                    if gene != None:
                        found = True
                        all_found.append({"node_id": node_id, "symbol": gene.symbol, "gene_id":gene.id, "input":alias_id, "type":"alias"})
                        break
                if found:
                    continue

            # then, try using name
            if "name" in node:
                names = node.get("name")
                for node_name in names:
                    if len(node_name) < 40:
                        gene = term_mapper.get_gene_from_identifier(node_name)
                        if gene != None:
                            found = True
                            all_found.append({"node_id": node_id, "symbol": gene.symbol, "gene_id":gene.id, "input":node_name, "type":"name"})
                            break
                if found:
                    continue

            # if "functionTerm" in node:
            #     genes = self.genes_from_function_term(node["functionTerm"], network_id, network_name, e_set_config.name, report, all_found, node_id)

            if not found:
                all_not_found.append({"node_id":node_id, "names": list(node.get("name"))})

        print "Found genes for " + str(len(all_found)) + " nodes"
        print "Did not find genes for " + str(len(all_not_found)) + " nodes"
        if symbols_only:
            symbols = []
            for dict in all_found:
                if "symbol" in dict:
                    symbols.append(dict["symbol"])
            print "Found %s symbols" % (len(symbols))
            return symbols
        else:
            return all_found