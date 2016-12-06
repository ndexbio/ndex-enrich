from __future__ import division
from ndex.networkn import NdexGraph
import data_model as dm
from os import getcwd

def create_similarity_map_from_enrichment_files(map_name, directory, e_set_name, min_subsumption):
    e_data = dm.EnrichmentData(directory)
    e_data.load_one_eset(e_set_name)
    e_set = e_data.get_e_set(e_set_name)
    create_similarity_map(map_name, e_set, min_subsumption)

def create_similarity_map(name, e_set, min_subsumption, id_attribute="genes"):
    similarity_map = NdexGraph()
    set_name_to_node_id_map = {}
    id_sets = {}
    for set_name in e_set.id_set_map:
        id_set = e_set.id_set_map[set_name].set
        id_sets[set_name] = id_set
        att = {id_attribute: list(id_set)}
        node_id = similarity_map.add_new_node(set_name, att)
        set_name_to_node_id_map[set_name] = node_id
        
    for set_name_1 in id_sets.keys():
        source_node_id = set_name_to_node_id_map[set_name_1]
        for set_name_2 in id_sets.keys():
            if set_name_1 != set_name_2:
                overlap = list(id_sets[set_name_1].intersection(id_sets[set_name_2]))
                size_overlap=len(overlap)
                if size_overlap != 0:
                    set_2_size = len(list(id_sets[set_name_2]))
                    subsumes_measure=size_overlap/set_2_size
                    if subsumes_measure > min_subsumption:
                        target_node_id = set_name_to_node_id_map[set_name_2]
                        atts = {"sub" : subsumes_measure, "overlap": overlap, "overlap_size": size_overlap}
                        similarity_map.add_edge_between(source_node_id, target_node_id, "subsumed_by", atts)

    filename = getcwd() + "/" + name + ".cx"
    print "writing map to: " + filename
    similarity_map.write_to(filename)



