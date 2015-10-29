__author__ = 'dexter'

import data_model as dm
import ndex_access as na
from operator import attrgetter

# Testing enrichment components

ndex_host = "http://dev2.ndexbio.org"
ndex_e_set_account_name = "enrichtest"
e_set_name = 'test'
query_ids = [
    "ALDOA",
    "HSPB1",
    "GREB1",
    "HDAC1"
]

# Create a fresh data model
e_data = dm.EnrichmentData()

# create one e_set in e_data
e_data.add_e_set(e_set_name)

n_access = na.NdexAccess(ndex_host)

# a list of network ids
network_ids = n_access.get_account_network_ids(ndex_e_set_account_name)

print "found " + str(len(network_ids)) + " networks"

# Process networks into the e_set 'test'
for network_id in network_ids:
    name, id_list = n_access.get_ids("HGNC Symbol", network_id)
    print name + " : " + str(len(id_list))
    e_data.add_id_set(e_set_name, name, id_list)

# Make a query id_set
query_id_set = dm.IdentifierSet(query_ids)

# Run an enrichment query vs the enrichment set
scores, coverage = e_data.get_scores( e_set_name, query_id_set)

# Sort the scores by p-value
scores = sorted(scores, key=attrgetter('pv'))

print "Scores"
for score in scores:
    print score.format()

print "Query Coverage"
for tuple in coverage.get_sorted_ids():
    print str(tuple[1]) + ":" + str(tuple[0])
