from __future__ import division
from ndex.networkn import NdexGraph
import data_model as dm
import operator

# TODO: only one edge between each pair of nodes. Take the best one.


def create_similarity_map_from_enrichment_files(map_name, directory, e_set_name, min_subsumption, max_edges=3):
    e_data = dm.EnrichmentData(directory)
    e_data.load_one_eset(e_set_name)
    e_set = e_data.get_e_set(e_set_name)
    return create_similarity_map(map_name, e_set, min_subsumption, max_edges=max_edges)

def create_similarity_map(name, e_set, min_subsumption, id_attribute="genes", max_edges=5):
    similarity_graph = NdexGraph()
    similarity_graph.set_name(name)
    set_name_to_node_id_map = {}
    id_sets = {}
    for network_id in e_set.id_set_map:
        id_set_object = e_set.id_set_map[network_id]
        network_name = id_set_object.name
        id_set = id_set_object.set
        id_sets[network_id] = id_set
        att = {id_attribute: list(id_set)}
        node_id = similarity_graph.add_new_node(network_name, att)
        set_name_to_node_id_map[network_id] = node_id
    source_similarities = {}
    for network_id_1 in id_sets.keys():
        source_node_id = set_name_to_node_id_map[network_id_1]

        list_1 = list(id_sets[network_id_1])
        set_1_size = len(list_1)
        similarities = []
        for network_id_2 in id_sets.keys():

            if network_id_1 != network_id_2:
                set_1 = id_sets[network_id_1]
                set_2 = id_sets[network_id_2]
                target_node_id = set_name_to_node_id_map[network_id_2]
                list_2 = list(id_sets[network_id_2])
                set_2_size = len(list_2)
                overlap = list(set_1.intersection(set_2))
                size_overlap=len(overlap)
                if size_overlap != 0:

                    subsumes = size_overlap/set_2_size
                    #subsumes_1 = size_overlap/set_2_size
                    #subsumes_2 = size_overlap/set_1_size
                    #subsumes = min(subsumes_1, subsumes_2)
                    if size_overlap > 3:
                        print "overlap: %s %s" % (size_overlap, overlap)


                    similarity = {"source_node_id": source_node_id,
                                  "target_node_id": target_node_id,
                                  "subsumes": subsumes}

                    similarity["atts"] = {"subsumes": subsumes,
                                          "overlap": overlap,
                                          "overlap_size": size_overlap}
                    similarities.append(similarity)
                else:
                    print "no overlap"

        # rank the similarities
        similarities = sorted(similarities, key=operator.itemgetter('subsumes'), reverse=True)
        source_similarities[network_id_1] = similarities



    # always include the most similar node to make sure that each node has at least one edge and the graph is connected
    # don't connect more than max_edges
    for network_id, similarities in source_similarities.iteritems():
        count = 0
        for similarity in similarities:
            if count >= max_edges:
                break
            if count == 0 or similarity["subsumes"] > min_subsumption:
                atts = similarity["atts"]
                source_node_id = similarity["source_node_id"]
                target_node_id = similarity["target_node_id"]

                similarity_graph.add_edge_between(source_node_id, target_node_id, attr_dict=atts)
            count = count + 1

    return similarity_graph




