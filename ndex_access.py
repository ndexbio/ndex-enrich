__author__ = 'dexter'

import ndex.client as nc
import mygeneinfo

class NdexAccess():
    def __init__(self, host, username=None, password=None):
        self.ndex = nc.Ndex(host, username=username, password=password)
        self.ndex.set_debug_mode(True)
        self.node_map = {}
        self.base_term_map = {}
        self.function_term_map = {}
        self.term_to_gene_map = {}
        self.genes = {}

    def reset_tables(self):
        self.node_map = {}
        self.base_term_map = {}
        self.function_term_map = {}
        self.term_to_gene_map = {}
        self.genes = {}

    # def get_ids(self, prefix, network_id):
    #     network = self.ndex.get_complete_network(network_id)
    #     ids = []
    #     if prefix == "name":
    #         for node in network.get("nodes").values():
    #             if node.get("name"):
    #                 ids.append(node.get("name"))
    #
    #     else:
    #         for term in network.get("baseTerms").values():
    #             name = term.get("name")
    #             components = name.split(":")
    #             id = False
    #             term_prefix = False
    #             if len(components) > 1:
    #                 term_prefix = components[0]
    #                 id = components[1]
    #             if id and term_prefix and term_prefix == prefix:
    #                 ids.append(id)
    #     return ids

    def get_genes_cx(self, network_id):
        node_table = self.get_nodes_from_cx(network_id)

        self.reset_tables()

        for node_id, node in node_table.items():
            if "represents" in node:
                represents_id = node["represents"]
                if self.gene_from_term(represents_id, node_id):
                    continue
            # otherwise check aliases
            if "alias" in node:
                alias_ids = node.get('alias')
                found_alias = False
                for alias_id in alias_ids:
                    if self.gene_from_term(alias_id,node_id):
                        found_alias = True
                        break
                if found_alias:
                    continue

            # then, try using name
            if "name" in node:
                names = node.get("name")
                foundGeneInName = False
                for node_name in names :
                    if self.gene_from_term(node_name,node_id):
                        foundGeneInName = True
                        break
                if foundGeneInName :
                    continue

            if "functionTerm" in node:
                self.genes_from_function_term(node["functionTerm"], node_id)

        # turn the gene lists into a hash table
        result = {}
        for geneRelation in self.genes.values():
            result[geneRelation.symbol] = list (geneRelation.nodes)
        return result

    def get_nodes_from_cx(self, network_id, node_att_prefix="name"):
        response = self.ndex.get_network_as_cx_stream(network_id)
        cx_network = response.json()
        node_table = {}
        for fragment in cx_network :
            if "nodes" in fragment:
                nodes = fragment["nodes"]
                for node in nodes:
                    node_id = node["@id"]
                    if not (node_id in node_table) :
                        node_table[node_id] = {}
                    working_node = node_table[node_id]
                    if "n" in node:
                        if "name" in working_node :
                            working_node["name"] =  working_node["name"].add(node["n"])
                        else:
                            node_name_set = set()
                            node_name_set.add(node["n"])
                            working_node["name"] = node_name_set
                    if "r" in node:
                        working_node["represents"] = node["r"]

            elif "nodeAttributes" in fragment:
                for attr in fragment ["nodeAttributes"]:
                    if attr["n"] == "name":
                        node_id = attr["po"]
                        node_name = attr["v"]

                        if node_id not in node_table:
                            working_node = {}
                            node_table[node_id] = working_node
                            node_name_set = set()
                            node_name_set.add(node_name)
                            working_node["name"] = node_name_set
                            node_table[node_id] = working_node
                        else:
                            working_node = node_table[node_id]
                            names = working_node["name"]
                            names.add(node_name)
                            working_node["name"] = names

                    elif attr["n"] == "alias":
                        node_id = attr["po"]
                        alias_list = attr["v"]
                        if node_id not in node_table:
                            working_node = {}
                            node_table[node_id] = working_node
                            node_alias_set = set()
                            node_alias_set = node_alias_set.union(set(alias_list))
                            working_node["alias"] = node_alias_set
                            node_table[node_id] = working_node
                        else:
                            working_node = node_table[node_id]
                            node_alias_set = working_node["name"]
                            node_alias_set = node_alias_set.union(set(alias_list))
                            working_node["alias"] = node_alias_set

            elif "functionTerms" in fragment:
                raise ValueError("not handling function terms in this version")
                # for functionTerm in fragment ["functionTerms"]:
                #     node_id = functionTerm["po"]
                #     working_node = node_table[node_id]
                #     if not working_node:
                #         working_node = {}
                #         node_table[node_id] = working_node
                #     working_node["functionTerm"] = functionTerm

        return node_table

    def gene_from_term(self, term, node_id):
        gene_relation = self.term_to_gene_map.get(term)
        if gene_relation:
            gene_relation.add_node(node_id)
            self.genes[gene_relation.id] = gene_relation
            return True
        else:
            # look for term on external service
            gene_relation = mygeneinfo.get_gene_symbol(term,node_id)
            if gene_relation:
                self.term_to_gene_map[term] = gene_relation
                self.genes[gene_relation.id] = gene_relation
                return True
            else:
                print term + " doesn't map to any gene"
        return False

    def genes_from_function_term(self, function_term,node_id):
        # if it is a function term, process all genes mentioned
        for parameter in function_term['args']:
            if type(parameter) == 'str':
                self.gene_from_term(parameter,node_id)
            else:
                self.genes_from_function_term(parameter,node_id)



    # try using the name to find a gene
    # assume species is human for now
    def gene_from_node_name(self, names):
        for name in names:
            gene = mygeneinfo.query_standard_to_gene_quick(name)
            if gene:
                self.term_to_gene_map[name] = gene
                self.genes[gene.id] = gene.symbol
                return True
            else:
                print name + " not found in mygene.info"
        return False

    def genes_from_term_id(self, term_id):
        if self.gene_from_base_term_id(term_id):
            return True
        # elif self.genes_from_function_term_id(term_id):
        #     return True
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

    def gene_from_base_term_id(self, base_term_id):
        base_term = self.base_term_map.get(base_term_id)
        if base_term:
            gene = self.term_to_gene_map.get(base_term.name)
            if gene:
                self.genes[gene.id] = gene
                return True
            else:
                # look for term on external service
                gene = mygeneinfo.query_standard_to_gene_quick(base_term.name)
                if gene:
                    self.term_to_gene_map[base_term.name] = gene
                    self.genes[gene.id] = gene
                    return True
        return False

    def find_networks(self, id_set_config):
        result = []
        print "ID set type %s " % (id_set_config.type)
        if id_set_config.type == "QUERY":
            result = self.ndex.search_networks(
                id_set_config.query_string,
                id_set_config.account_name,
                size=id_set_config.query_limit)
            print "%s network ids from id_list" % (len(id_set_config.id_list))
        elif id_set_config.type in ["IDLIST", "IDMAP"]:

            if id_set_config.type == "IDLIST":
                print "%s network ids from id_list" % (len(id_set_config.id_list))
                id_list = id_set_config.id_list
            else:
                print "%s network ids from id_map" % (len(id_set_config.id_map))
                id_list = id_set_config.id_map.values()

            for network_id in id_list:
                network_summary = self.ndex.get_network_summary(network_id)
                if network_summary:
                    result.append(network_summary)
        else:
            print "Unknown id_set config type: " + id_set_config.type
            return result
        if('networks' in result):
            result = result.get('networks')

        result = self.filter_source_format(result, id_set_config)
        return result

    def filter_source_format(self, network_summaries, id_set_config):
        if not id_set_config.source_format:
            return network_summaries
        filtered = []
        filter_format = id_set_config.source_format.upper()
        for network_summary in network_summaries:
            source_format = self.getNetworkProperty(network_summary, "ndex:sourceFormat")

            if(not source_format):
                source_format = self.getNetworkProperty(network_summary, "sourceFormat")

            if source_format and filter_format == source_format.upper():
                filtered.append(network_summary)
            elif(filter_format == 'UNKNOWN' and not source_format):
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
        network_summary_list = self.ndex.find_networks("", ndex_e_set_account_name, size=max)
        ids = []
        for ns in network_summary_list:
            id = ns.get("externalId")
            ids.append(id)
        return ids