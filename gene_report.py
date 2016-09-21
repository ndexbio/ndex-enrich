__author__ = 'dexter'

import ndex_access
import term2gene_mapper

class GeneReport():
    def __init__(self, name):
        self.gene_network_pairs = {}
        self.name = name
        self.fields = [
            "Gene Symbol",
            "Entrez Gene Id",
            "Network Id",
            "Network Name",
            "Network Sets"
        ]

    def add_gene_network_pair(self, gene_id, gene_symbol, network_id, network_name, e_set_name):
        key = str(gene_id) + "_" + network_id
        pair = self.gene_network_pairs.get(key)
        if not pair:
            pair = {
                "Gene Symbol": gene_symbol,
                "Entrez Gene Id": gene_id,
                "Network Id": network_id,
                "Network Name": network_name,
                "e_sets": [e_set_name]
            }
            self.gene_network_pairs[key] = pair
        else:
            e_sets = pair["e_sets"]
            if e_set_name not in e_sets:
                e_sets.append(e_set_name)
                pair["e_sets"] = e_sets

    def get_rows(self):
        s = ", "
        for pair in self.gene_network_pairs.values():
            pair["Network Sets"] = s.join(pair.get("e_sets"))
        return self.gene_network_pairs.values()

    def get_network_summary(self):
        networks = {}
        rows = self.get_rows()
        for row in rows:
            network_id = row.get("Network Id")
            network = networks.get(network_id)
            new_symbol = row.get('Gene Symbol')
            new_id = row.get('Entrez Gene Id')
            if not network:
                network = {'Network Id': row.get('Network Id'),
                           'Gene Symbols': [new_symbol],
                           'Entez Gene Ids': [new_id],
                           'Network Name' : row.get('Network Name'),
                           }
                networks[network_id] = network
            network['Gene Symbols'].append(new_symbol)
            network['Entez Gene Ids'].append(new_id)
        return networks

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

    def create_gene_report(self, config):
        report = GeneReport(config.name)
        term_to_gene_map = {}

        for e_set_config in config.e_set_configs:
            self.process_e_set_for_report(e_set_config, report, term_to_gene_map)
        return report

    def process_e_set_for_report(self, e_set_config, report, term_to_gene_map):
        ndex = ndex_access.NdexAccess(e_set_config.ndex, username=e_set_config.username, password=e_set_config.password)
        # Find the networks
        networks = ndex.find_networks(e_set_config)
        print "Found " + str(len(networks)) + " networks for gene report"
        for network in networks:
            self.process_network_for_report(network, e_set_config, report, ndex, term_to_gene_map)

    def process_network_for_report(self, network, e_set_config, report, ndex, term_to_gene_map):
        network_id = network.get("externalId")
        network_name = network.get("name")
        print " - " + network_name + " : " + network_id
        #    genes = ndex.get_genes(network_id, term_to_gene_map)
        node_table = ndex.get_nodes_from_cx(network_id)
        self.term_mapper.add_network_nodes(node_table)

        for node_id, node in node_table.items():
            if "represents" in node:
                represents_id = node["represents"]
                gene = self.term_mapper.gene_symbol_and_id_from_term(represents_id)
                if gene != None:
                    report.add_gene_network_pair(gene.id, gene.symbol, network_id, network_name, e_set_config.name)
                    continue
            # otherwise check aliases
            if "aliases" in node:
                alias_ids = node.get('aliases')
                found_alias = False
                for alias_id in alias_ids:
                    gene = self.term_mapper.gene_symbol_and_id_from_term(alias_id)
                    if gene != None:
                        report.add_gene_network_pair(gene.id, gene.symbol, network_id, network_name, e_set_config.name)
                        found_alias = True
                        break
                if found_alias:
                    continue

            # then, try using name
            if "name" in node:
                names = node.get("name")
                foundGeneInName = False
                for node_name in names:
                    if len(node_name) < 40:
                        gene = self.term_mapper.gene_symbol_and_id_from_term(node_name)
                        if gene != None:
                            report.add_gene_network_pair(gene.id, gene.symbol, network_id, network_name, e_set_config.name)
                            foundGeneInName = True
                            break
                if foundGeneInName:
                    continue

            if "functionTerm" in node:
                self.genes_from_function_term(node["functionTerm"], network_id, network_name, e_set_config.name, report)

    def genes_from_function_term(self, function_term, network_id, network_name, e_set_name, report):
        # if it is a function term, process all genes mentioned
        for parameter in function_term['args']:
            if type(parameter) == 'str':
                gene = self.term_mapper.gene_symbol_and_id_from_term(parameter)
                if gene != None:
                    report.add_gene_network_pair(gene.id, gene.symbol, network_id, network_name, e_set_name)
            else:
                self.genes_from_function_term(parameter, network_id, network_name, e_set_name, report)
