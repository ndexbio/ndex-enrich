__author__ = 'dexter'

import fake_persistence as storage

class EServiceConfiguration():

    def __init__(self):
        self.e_set_configs =[]
        self.name = None

    def get_e_set_config(self, name):
        for conf in self.e_set_configs:
            if conf.name == name:
                return conf
        return False

    def load(self, config_name, test_mode = False):
        self.name = config_name
        if test_mode:
            test_config = ESetConfiguration(
                {"name": 'test',
                 "ndex": "http://dev2.ndexbio.org",
                 "account_name": "enrichtest",
                 "query_limit" : 100
                 }
            )
            self.e_set_configs.append(test_config)
        else:
            configs = storage.get_e_set_configs(config_name)
            for e_set_config in configs.get("e_sets"):
                config_object = ESetConfiguration(e_set_config)
                self.e_set_configs.append(config_object)
                print "loaded e_set configuration: " + str(config_object.name)

class ESetConfiguration():
    def __init__(self, config):
        self.name = config.get('name')
        self.ndex = config.get('ndex') if config.get('ndex') else "http://public.ndexbio.org"
        self.username = config.get('username')
        self.password = config.get('password')
        self.type = config.get('type') if config.get('type') else "QUERY"
        self.account_name = config.get('account_name')
        self.id_list = config.get('id_list') if config.get('id_list') else []
        self.query_string = config.get('query_string') if config.get('query_string') else ""
        self.query_limit = config.get('query_limit') if config.get('query_limit') else 100
        self.id_prefix = config.get('id_prefix') if config.get('id_prefix') else "HGNC Symbol"
        self.source_format = config.get('source_format')

