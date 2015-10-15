__author__ = 'dexter'

import ndex.client as nc

class NdexAccess():

    def __init__(self, host):
        self.ndex = nc.Ndex(host)

    def get_ids(self, prefix, network_id):
        network = self.ndex.get_complete_network(network_id)
        ids = []
        for term in network.get("baseTerms").values():
            name = term.get("name")
            components = name.split(":")
            if len(components) > 1:
                term_prefix = components[0]
                id = components[1]
            if id and term_prefix and term_prefix == prefix:
                ids.append(id)
        return network.get("name"), ids

    def get_account_network_ids(self, ndex_e_set_account_name, max=100):
        network_summary_list = self.ndex.find_networks("", ndex_e_set_account_name, block_size=max)
        ids = []
        for ns in network_summary_list:
            id = ns.get("externalId")
            ids.append(id)
        return ids