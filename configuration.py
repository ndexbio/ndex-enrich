__author__ = 'dexter'

class EServerConfiguration():

    def __init__(self):
        self.e_set_configs =[]

    def get_e_set_config(self, name):
        for conf in self.e_set_configs:
            if conf.name == name:
                return conf
        return False

    def load(self, test_mode = False):
        if test_mode:
            test_config = ESetConfiguration('test')
            # set parameters
            test_config.host = "http://dev2.ndexbio.org"
            test_config.account_name = "enrichtest"
            test_config.query_limit = 100

            self.e_set_configs.append(test_config)
        else:
            print "loading of configuration file not yet implemented"

class ESetConfiguration():
    def __init__(self, name):
        self.name = name
        self.host = "http://public.ndexbio.org"
        self.username = None
        self.password = None
        self.type = "QUERY"
        self.account_name = None
        self.id_list = []
        self.query_string = ""
        self.query_limit = 20
        self.id_prefix = "HGNC Symbol"

