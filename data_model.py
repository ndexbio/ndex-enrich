__author__ = 'dexter'

from scipy.stats import hypergeom
from operator import itemgetter
from os.path import join, isdir
from os import listdir
import fake_persistance as storage


# An instance of this class holds all the enrichment sets
class EnrichmentData():
    def __init__(self, dir_name):
        self.enrichment_set_map = {}

        self.dir_name = dir_name

    def load(self):
        for f_name in listdir(self.dir_name):
            path = join(self.dir_name, f_name)
            if isdir(path):
                e_set = self.add_e_set(f_name)
                e_set.load()

    def get_e_set_names(self):
        return self.enrichment_set_map.keys()

    def get_e_set(self, e_set_name):
        return self.enrichment_set_map.get(e_set_name)

    def get_id_set_names(self, e_set_name):
        e_set = self.get_e_set(e_set_name)
        return e_set.get_id_set_names()

    def get_id_set(self, e_set_name, id_set_id):
        e_set = self.get_e_set(e_set_name)
        return e_set.get_id_set(id_set_id)

    def add_e_set (self, e_set_name):
        e_set_name = e_set_name.lower()
        e_set = EnrichmentSet(e_set_name)
        self.enrichment_set_map[e_set_name] = e_set
        return e_set

    def add_id_set(self, e_set_name, id_set_name, id_list):
        e_set_name = e_set_name.lower()
        if not e_set_name in self.enrichment_set_map.keys():
            e_set_name = self.add_e_set(e_set_name)
        if not e_set_name:
            return False
        return self.enrichment_set_map[e_set_name].add_id_set(id_set_name, id_list)

    def get_scores(self, e_set_name, query_id_set):
        e_set_name = e_set_name.lower()
        if e_set_name in self.enrichment_set_map.keys():
            e_set = self.enrichment_set_map.get(e_set_name)
            return e_set.get_enrichment_scores(query_id_set)
        else:
            print "unknown e_set " + e_set_name

# an enrichment set (e_set) is a named set of identifier sets (id_set)
# a query is made by testing a query id_set vs. each id_set in the e_set
class EnrichmentSet():

    def __init__(self, name):
        self.id_set_map = {}
        self.objects = set()
        self.name = name

    def load(self):
        if storage.e_set_exists(self.name):
            for f_name in storage.get_id_set_file_names(self.name):

                id_set_dict = storage.get_id_set_data(self.name, f_name)
                id_set = IdentifierSet(id_set_dict)
                self.add_id_set(id_set)

    def save(self):
        storage.ensure_e_set_dir(self.name)
        for set_name, id_set in self.id_set_map.iteritems():
            id_set.save()

    def get_id_set_names(self):
        return self.id_set_map.keys()

    def get_id_set(self, id_set_id):
        return self.id_set_map.get(id_set_id)

    def get_id_set_by_network_id(self, network_id):
        for id_set in self.id_set_map.values():
            if id_set.network_id == network_id:
                return id_set
        return None

    # create a new id_set in this e_set based on
    # a name and a list of id strings
    def add_id_set (self, id_set):
        self.id_set_map[id_set.network_id] = id_set
        self.update()

    def update(self):
        # calculate the set of all objects - across all id_sets in the e_set

        # first clear the set of all objects in the e_set
        self.objects = set()

        # now merge in each id set
        for id_set in self.id_set_map.values():
            self.objects = self.objects | id_set.set

    def get_enrichment_scores(self, query_id_set):
        scores = []
        M = len(self.objects)
        coverage = Coverage(query_id_set)
        for set_id, id_set in self.id_set_map.iteritems():
            score = id_set.get_enrichment_score(query_id_set, M, set_id)
            coverage.add_score(score)
            scores.append(score.to_dict())
        result = {"scores" : scores, "coverage" : coverage.to_dict()}
        return result

class Coverage():

    def __init__(self, id_set):
        self.map = {}
        for id in id_set.set:
            self.map[id] = 0

    def add_score(self, score):
        for id in score.overlap:
            if id in self.map.keys():
                self.map[id] += 1

    def get_sorted_ids(self):
        return sorted(self.map.items(), key=itemgetter(1))

    def to_dict(self):
        return self.get_sorted_ids()

class IdentifierSet():
    def __init__(self, id_set_dict):
        self.set = set(id_set_dict.get("ids"))
        self.name = id_set_dict.get("name")
        self.network_id = id_set_dict.get("network_id")
        self.ndex = id_set_dict.get("ndex")
        self.e_set = id_set_dict.get("e_set")
        self.n = len(self.set)

    def to_dict(self):
        return {
            "name": self.name,
            "ids":list(self.set),
            "network_id": self.network_id,
            "ndex": self.ndex,
            "e_set" : self.e_set
        }

    def save(self):
        storage.save_id_set_dict(self.e_set, self.network_id, self.to_dict())

    # compare this id_set to a query_id_set
    def get_enrichment_score(self, query_id_set, M, set_name):
        overlap = query_id_set.set & self.set
        k = len(overlap)
        pv = hypergeom(M, self.n, query_id_set.n).sf(k)
        return EnrichmentScore(pv, k, overlap, self.name)

class EnrichmentScore():

    def __init__(self, pv, k, overlap, set_name):
        self.k = k
        self.pv = pv
        self.overlap = overlap
        self.set_name = set_name

    def format(self):
        return self.set_name + "  pv: " + str(self.pv) + " k:" + str(self.k)

    def to_dict(self):
        return {
            "k" : self.k,
            "pv" : self.pv,
            "overlap" : list(self.overlap),
            "set_name" : self.set_name
        }




