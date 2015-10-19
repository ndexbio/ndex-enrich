__author__ = 'dexter'

import data_model as dm
import ndex_access as na
import fake_persistance as storage

class Updater():

    def __init__(self, e_set_config):

        self.config = e_set_config
        self.rebuild = False

    def update(self, rebuild = False):

        self.rebuild = rebuild
        # Create a fresh data model
        self.e_data = dm.EnrichmentData()

        self.networks = na.find_networks()

        self.remove_cached_id_sets()

        for id_set_config in self.config.get_id_set_configs():
            ids = id_set_config.get_ids()
            id_set = dm.IdentifierSet(ids, id_set_config.host, id_set_config.network_id, id_set_config.name)
            print "caching " + str(id_set)
            storage.cacheIdentifierSet(id_set)

    def removed_cached_id_sets():
        # if rebuild is true, then all cached id sets are removed
        # otherwise, it removes the ones where the network was not found or has been modified.
        return False

