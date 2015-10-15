__author__ = 'dexter'

from scipy.stats import hypergeom
from operator import itemgetter

# An instance of this class holds all the enrichment sets
class EnrichmentData():
    def __init__(self):
        self.enrichment_set_map = {}

    def add_enrichment_set (self, e_set_name):
        e_set_name = e_set_name.lower()
        if e_set_name in self.enrichment_set_map.keys():
            return False
        self.enrichment_set_map[e_set_name] = EnrichmentSet()
        return e_set_name

    def add_id_set(self, e_set_name, id_set_name, id_list):
        e_set_name = e_set_name.lower()
        if not e_set_name in self.enrichment_set_map.keys():
            e_set_name = self.add_enrichment_set(e_set_name)
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

    def __init__(self):
        self.id_set_map = {}
        self.objects = set()

    # create a new id_set in this e_set based on
    # a name and a list of id strings
    def add_id_set (self, name, id_list):
        name = name.lower()
        if name in self.id_set_map.keys():
            return False
        self.id_set_map[name] = IdentifierSet(id_list)
        self.update()
        return name

    def update(self):
        # clear the set of all objects in the e_set
        self.objects = set()
        for id_set in self.id_set_map.values():
            self.objects = self.objects | id_set.set

    def get_enrichment_scores(self, query_id_set):
        scores = []
        M = len(self.objects)
        coverage = Coverage(query_id_set)
        for set_name, id_set in self.id_set_map.iteritems():
            score = id_set.get_enrichment_score(query_id_set, M, set_name)
            coverage.add_score(score)
            scores.append(score)
        return scores, coverage

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

class IdentifierSet():
    def __init__(self, id_list):
        self.set = set(id_list)
        self.n = len(self.set)

    # compare this id_set to a query_id_set
    def get_enrichment_score(this, query_id_set, M, set_name):
        overlap = query_id_set.set & this.set
        k = len(overlap)
        pv = hypergeom(M, this.n, query_id_set.n).sf(k)
        return EnrichmentScore(pv, k, overlap, set_name)

class EnrichmentScore():

    def __init__(self, pv, k, overlap, set_name):
        self.k = k
        self.pv = pv
        self.overlap = overlap
        self.set_name = set_name

    def format(self):
        return self.set_name + "  pv: " + str(self.pv) + " k:" + str(self.k)




