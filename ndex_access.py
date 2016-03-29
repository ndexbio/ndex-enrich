__author__ = 'dexter'

import ndex.client as nc
import mygeneinfo

class NdexAccess():
    def __init__(self, host):
        self.ndex = nc.Ndex(host)
        self.ndex.set_debug_mode(True)
        self.node_map = {}
        self.base_term_map = {}
        self.function_term_map = {}
        self.term_to_gene_map = {}
        self.genes = {}

    def get_ids(self, prefix, network_id):
        network = self.ndex.get_complete_network(network_id)
        ids = []
        if prefix == "name":
            for node in network.get("nodes").values():
                if node.get("name"):
                    ids.append(node.get("name"))

        else:
            for term in network.get("baseTerms").values():
                name = term.get("name")
                components = name.split(":")
                id = False
                term_prefix = False
                if len(components) > 1:
                    term_prefix = components[0]
                    id = components[1]
                if id and term_prefix and term_prefix == prefix:
                    ids.append(id)
        return ids

    def get_genes_cx(self, network_id):
        response = self.ndex.get_network_as_cx_stream(network_id)
        cx_network = response.json()
        node_map = {}
        for fragment in cx_network :
            if "nodes" in fragment:
                nodes = fragment["nodes"]
                for node in nodes:
                    node_id = node["@id"]
                    if not (node_id in node_map) :
                        node_map[node_id] = {}
                    working_node = node_map[node_id]
                    if "n" in node:
                        if "name" in working_node :
                            working_node["name"] =  working_node["name"].add(node["n"])
                        else:
                            working_node["name"] = set([node["n"]])
                    if "r" in node:
                        working_node["represents"] = node["r"]
            elif "nodeAttributes" in fragment:
                for attr in fragment ["nodeAttributes"]:
                    if attr["n"] == "name":
                        node_id = attr["po"]
                        node_name = attr["v"]
                        working_node = node_map[node_id]
                        if not working_node:
                            working_node = {}
                            node_map[node_id] = working_node
                        if "name" in working_node:
                            names = working_node["name"]
                            names.add(node_name)
                            working_node["name"] = names
                        else:
                            working_node["name"] = set([node_name])
                    elif attr["n"] == "alias":
                        node_id = attr["po"]
                        alias_list = attr["v"]
                        working_node = node_map[node_id]
                        if not working_node:
                            working_node = {}
                            node_map[node_id] = working_node
                        if "alias" in working_node:
                            names = working_node["alias"]
                            names.union(set(alias_list))
                            working_node["alias"] = names
                        else:
                            working_node["alias"] = set(alias_list)
            elif "functionTerms" in fragment:
                for functionTerm in fragment ["functionTerms"]:
                    node_id = functionTerm["po"]
                    working_node = node_map[node_id]
                    if not working_node:
                        working_node = {}
                        node_map[node_id] = working_node
                    working_node["functionTerm"] = functionTerm

        for node in node_map.values():
            if "represents" in node:
                represents_id = node["represents"]
                if self.genes_from_base_term(represents_id):
                    break
            # otherwise check aliases
            if "aliases" in node:
                alias_ids = node.get('aliases')
                found_alias = False
                for alias_id in alias_ids:
                    if self.genes_from_base_term(alias_id):
                        found_alias = True
                        break
                if found_alias:
                    break

            # then, try using name
            if "name" in node:
                names = node.get("name")
                if names and self.gene_from_node_name(names):
                    break
            if "functionTerm" in node:
                self.genes_from_function_term(node["functionTerm"])

        return self.genes.values()

    def get_genes(self, network_id, term_to_gene_map):
        network = self.ndex.get_complete_network(network_id)
        self.node_map = network.get("nodes")
        self.base_term_map = network.get("baseTerms")
        self.function_term_map = network.get("functionTerms")
        self.term_to_gene_map = term_to_gene_map
        self.genes = {}
        for node in self.node_map.values():
            # first check to see if we can get a gene from "represents"
            represents_id = node.get('represents')
            if represents_id and self.genes_from_term_id(represents_id):
                break
            # otherwise check aliases
            alias_ids = node.get('aliases')
            found_alias = False
            for alias_id in alias_ids:
                if self.genes_from_term_id(alias_id):
                    found_alias = True
                    break
            if found_alias:
                break
            # finally, try using name
            name = node.get("name")
            if name:
                self.gene_from_node_name(name)

        return self.genes.values()

    def genes_from_term_id(self, term_id):
        if self.gene_from_base_term_id(term_id):
            return True
        elif self.genes_from_function_term_id(term_id):
            return True
        else:
            return False

    def genes_from_function_term_id(self, function_term_id):
        # if it is a function term, process all genes mentioned
        function_term = self.function_term_map.get(function_term_id)
        if function_term:
            for parameter in function_term.get('parameters'):
                self.genes_from_term_id(parameter)
            return True
        return False

    def genes_from_function_term(self, function_term):
        # if it is a function term, process all genes mentioned
        for parameter in function_term['args']:
            if type(parameter) == 'str':
                self.gene_from_base_term(parameter)
            else:
                self.genes_from_function_term(parameter)


    def gene_from_base_term_id(self, base_term_id):
        base_term = self.base_term_map.get(base_term_id)
        if base_term:
            gene = self.term_to_gene_map.get(base_term.name)
            if gene:
                self.genes[gene.id] = gene
                return True
            else:
                # look for term on external service
                gene = mygeneinfo.query_standard_to_gene(base_term.name)
                if gene:
                    self.term_to_gene_map[base_term.name] = gene
                    self.genes[gene.id] = gene
                    return True
        return False


    def gene_from_base_term(self, base_term):
        gene = self.term_to_gene_map.get(base_term)
        if gene:
            self.genes[gene.id] = gene
            return True
        else:
            # look for term on external service
            gene = mygeneinfo.query_standard_to_gene(base_term)
            if gene:
                self.term_to_gene_map[base_term] = gene
                self.genes[gene.id] = gene
                return True
        return False

    # try using the name to find a gene
    # assume species is human for now
    def gene_from_node_name(self, names):
        for name in names:
            gene = mygeneinfo.query_standard_to_gene(name)
            if gene:
                self.term_to_gene_map[name] = gene
                self.genes[gene.id] = gene
                return True
        return False


    def find_networks(self, id_set_config):
        result = []
        if id_set_config.type == "QUERY":
            result = self.ndex.search_networks(
                id_set_config.query_string,
                id_set_config.account_name,
                block_size=id_set_config.query_limit)
        elif id_set_config.type == "IDLIST":
            networks = []
            for network_id in id_set_config.id_list:
                network_summary = self.ndex.get_network_summary(network_id)
                if network_summary:
                    result.append(network_summary)
        else:
            print "Unknown id_set config type: " + id_set_config.type
            return result
        result = self.filter_source_format(result, id_set_config)
        return result

    def filter_source_format(self, network_summaries, id_set_config):
        if not id_set_config.source_format:
            return network_summaries
        filtered = []
        filter_format = id_set_config.source_format.upper()
        for network_summary in network_summaries:
            source_format = self.getNetworkProperty(network_summary, "sourceFormat")
            if source_format and filter_format == source_format.upper():
                filtered.append(network_summary)
        return filtered

    def getNetworkProperty(self, network, name):
        properties = network.get("properties")
        if not properties:
            return False
        for prop in properties:
            if prop.get("predicateString") == name:
                return prop.get("value")
        return False

    def get_account_network_ids(self, ndex_e_set_account_name, max=100):
        network_summary_list = self.ndex.find_networks("", ndex_e_set_account_name, block_size=max)
        ids = []
        for ns in network_summary_list:
            id = ns.get("externalId")
            ids.append(id)
        return ids