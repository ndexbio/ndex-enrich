__author__ = 'dexter'

import ndex.client as nc

class NdexAccess():

    def __init__(self, host):
        self.ndex = nc.Ndex(host)
        self.ndex.set_debug_mode(True)

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
        return ids

    def find_networks(self, id_set_config):
        if id_set_config.type == "QUERY":
            return self.ndex.search_networks(
                id_set_config.query_string,
                id_set_config.account_name,
                block_size=id_set_config.query_limit)
        elif id_set_config.type == "IDLIST":
            networks = []
            for network_id in id_set_config.id_list:
                network_summary = self.ndex.get_network_summary(network_id)
                if network_summary:
                    networks.append(network_summary)
            return networks
        else:
            print "Unknown id_set config type: " + id_set_config.type
            return []

    def get_account_network_ids(self, ndex_e_set_account_name, max=100):
        network_summary_list = self.ndex.find_networks("", ndex_e_set_account_name, block_size=max)
        ids = []
        for ns in network_summary_list:
            id = ns.get("externalId")
            ids.append(id)
        return ids