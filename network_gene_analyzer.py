__author__ = 'dexter'


class NetworkGeneAnalyzer:
    def __init__(self, network_id, ndex):
        self.ndex = ndex
        self.network = self.ndex.get_complete_network(network_id)
        self.identifiers = []
        self.node_map = self.network.get("nodes")
        self.base_term_map = self.network.get("baseTerms")
        self.function_term_map = self.network.get("functionTerms")
        self.gene_symbols = []

    def get_genes(self):
        self.get_network_identifiers()
        self.get_genes_for_identifiers()
        return self.gene_symbols

    def get_genes_for_identifiers(self):
        print "TODO"

    def get_network_identifiers(self):
        for node in self.node_map.values():
            # get ids from represents
            represents_id = node.get('represents')
            if represents_id:
                self.get_identifiers_from_term_id(represents_id)
            # check aliases, take the first that resolves to a gen
            alias_ids = node.get('aliases')
            for alias_id in alias_ids:
                self.get_identifiers_from_term_id(alias_id)
            # finally, add the name
            name = node.get("name")
            if name:
                self.identifiers.append(name)

    def get_identifiers_from_term_id(self, term_id):
        if self.identifier_from_base_term_id(term_id):
            return True
        elif self.get_identifiers_from_function_term_id(term_id):
            return True
        else:
            return False

    def get_identifiers_from_function_term_id(self, function_term_id):
        # if it is a function term, process all genes mentioned
        function_term = self.function_term_map.get(function_term_id)
        if function_term:
            for parameter in function_term.get('parameters'):
                self.get_identifiers_from_term_id(parameter)
            return True
        else:
            return False

    def identifier_from_base_term_id(self, base_term_id):
        base_term = self.base_term_map.get(base_term_id)
        if base_term:
            self.identifiers.append(base_term.name)
        return False
