__author__ = 'dexter'


import argparse
import similarity_map_utils as smu
import ndex.beta.layouts as layouts
import ndex.beta.toolbox as toolbox
from os import getcwd
import ndex.client as nc
import ndex.networkn as networkn

parser = argparse.ArgumentParser(description='build a similarity map from files in an e_set directory')
# map_name='nci_pid_preview'
# e_set_dir='e_sets'
# e_set_name='nci_pid_preview'
# min_sub=0.02
parser.add_argument('map_name', action='store')

parser.add_argument('e_set_dir', action='store')

parser.add_argument('e_set_name', action='store')

parser.add_argument('min_sub', action='store', type=float)

arg = parser.parse_args()

#ndex = nc.Ndex("http://dev.ndexbio.org", "nci-test", "nci-test")
ndex = nc.Ndex("http://dev2.ndexbio.org", "aarongary", "ccbbucsd")
#response = ndex.get_network_as_cx_stream("3aeca6e7-c3c5-11e6-a7bc-0660b7976219")
#response = ndex.get_network_as_cx_stream("981ed28b-1b06-11e7-801c-0660b7976219")
response = ndex.get_network_as_cx_stream("1e37ed1c-1bbd-11e7-801c-0660b7976219")


template_cx = response.json()
template_network = networkn.NdexGraph(template_cx)

similarity_graph = smu.create_similarity_map_from_enrichment_files(arg.map_name, arg.e_set_dir, arg.e_set_name, arg.min_sub)


toolbox.apply_network_as_template(similarity_graph, template_network)
print "applied graphic style from " + str(template_network.get_name())

layouts.apply_directed_flow_layout(similarity_graph, node_width=35, iterations=50, use_degree_edge_weights=True)

filename = getcwd() + "/" + similarity_graph.get_name() + ".cx"
print "writing map to: " + filename
similarity_graph.write_to(filename)
print "Map complete"


