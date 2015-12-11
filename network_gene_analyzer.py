__author__ = 'dexter'

import requests
from bson.json_util import dumps

class NetworkGeneAnalyzer:
    def __init__(self, network_id, ndex):
        self.ndex = ndex
        self.network = self.ndex.get_complete_network(network_id)
        self.identifiers = []
        self.node_map = self.network.get("nodes")
        self.base_term_map = self.network.get("baseTerms")
        self.function_term_map = self.network.get("functionTerms")
        self.scrubbed_terms = []

    def get_genes(self):
        self.get_network_identifiers()
        self.get_genes_for_identifiers()
        scrub_list = []

        for scrub_item in self.scrubbed_terms:
            scrub_list.append(scrub_item.get('symbol'))

        return scrub_list

    def get_genes_for_identifiers(self):
        #print "TODO"

        IDMAP_URL = 'http://ec2-52-34-209-69.us-west-2.compute.amazonaws.com:3000/idmapping'

        payload = {'ids':self.identifiers}

        headers = {'Content-Type': 'application/json',
               'Accept': 'application/json',
               'Cache-Control': 'no-cache',
               }

        r = requests.post(IDMAP_URL, data=dumps(payload), headers=headers)
        result_dictionary = r.json()

        print dumps(result_dictionary)
        #scrubbed_terms = []

        if(result_dictionary['matched'] is not None and len(result_dictionary['matched']) > 0):
            dedup_list = []

            #===========================================================
            # if the term we entered is already a gene symbol or a gene
            # id the response JSON will identify it in the inType field
            #
            # de-dup the list
            #===========================================================
            for term_match in result_dictionary['matched']:
                add_this_term = {'symbol': '', 'geneid':''}

                if(term_match['inType'] == 'Symbol'):
                    if(term_match['matches']['GeneID'] not in dedup_list):
                        add_this_term['symbol'] = term_match['in']
                        add_this_term['geneid'] = term_match['matches']['GeneID']
                        dedup_list.append(term_match['matches']['GeneID'])
                        self.scrubbed_terms.append(add_this_term)
                elif(term_match['inType'] == 'GeneID'):
                    if(term_match['in'] not in dedup_list):
                        add_this_term['symbol'] = term_match['matches']['Symbol']
                        add_this_term['geneid'] = term_match['in']
                        dedup_list.append(term_match['in'])
                        self.scrubbed_terms.append(add_this_term)
                else:
                    if(term_match['matches']['GeneID'] not in dedup_list):
                        add_this_term['symbol'] = term_match['matches']['Symbol']
                        add_this_term['geneid'] = term_match['matches']['GeneID']
                        dedup_list.append(term_match['matches']['GeneID'])
                        self.scrubbed_terms.append(add_this_term)


            #print dumps(self.scrubbed_terms)


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
