from __future__ import division
from ndex.networkn import NdexGraph
import data_model as dm
import operator
from math import sqrt

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
    remove_super_nodes = []
    for network_id in e_set.id_set_map:
        id_set_object = e_set.id_set_map[network_id]
        network_name = id_set_object.name
        id_set = id_set_object.set
        id_sets[network_id] = id_set
        att = {id_attribute: list(id_set)}
        node_id = similarity_graph.add_new_node(network_name, att)
        gene_count = float(len(id_set_object.gene_set))
        similarity_graph.set_node_attribute(node_id, "gene count", gene_count)
        similarity_graph.set_node_attribute(node_id, "width", sqrt(gene_count))
        similarity_graph.set_node_attribute(node_id, "ndex:internalLink", "[%s](%s)" % ("<i class='fa fa-eye' aria-hidden='true'></i>&nbsp;&nbsp;&nbsp;View network<br />",network_id))

        externalLink1 = "[%s](%s)" %("<i class='fa fa-download' aria-hidden='true'></i>&nbsp;&nbsp;&nbsp;BioPAX3 file (.owl)<br />","ftp://ftp.ndexbio.org/NCI_PID_BIOPAX_2016-06-08-PC2v8-API/" + network_name.replace(" ", "%20") + ".owl.gz")
        externalLink2 = "[%s](%s)" % ("<i class='fa fa-download' aria-hidden='true'></i>&nbsp;&nbsp;&nbsp;GSEA gene set (.grp)<br />","ftp://ftp.ndexbio.org/NCI_PID_GSEA_2017-04-06/" + network_name.replace(" ", "%20") + ".grp.gz")
        externalLink3 = "[%s](%s)" % ("<i class='fa fa-download' aria-hidden='true'></i>&nbsp;&nbsp;&nbsp;CX file (.cx)","http://dev2.ndexbio.org/v2/network/" + network_id + "?download=true")
        similarity_graph.set_node_attribute(node_id, "ndex:externalLink", [externalLink1, externalLink2, externalLink3])

        if(network_name == "NCI Pathway Interaction Database - Final Revision"):
            remove_super_nodes.append(node_id)

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

    temp_similarity_graph = similarity_graph.copy()
    for network_id, similarities in source_similarities.iteritems():
        count = 0
        for similarity in similarities:
            if count >= max_edges:
                break
            if count == 0 or similarity["subsumes"] > min_subsumption:
                atts = similarity["atts"]
                source_node_id = similarity["source_node_id"]
                target_node_id = similarity["target_node_id"]
                edge_id = temp_similarity_graph.add_edge_between(source_node_id, target_node_id, attr_dict=atts)

            count = count + 1

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
                source_gene_count = similarity_graph.node[source_node_id].get("gene count")

                target_node_id = similarity["target_node_id"]
                target_gene_count = similarity_graph.node[target_node_id].get("gene count")

                edge_overlap = float(atts["overlap_size"])

                # If the edge is pointing from low gene count to high gene count we proceed.
                # if the edge is pointing from high gene count to low count we check
                # the edge map to see if the converse edge exists.  If so we skip adding and
                # let the converse edge populate
                # if there is no acceptable edge we switch the source and target and proceed


                if(target_gene_count > source_gene_count):
                    edge_function = edge_overlap / (source_gene_count + target_gene_count - edge_overlap)

                    edge_id = similarity_graph.add_edge_between(source_node_id, target_node_id, attr_dict=atts, interaction='shares genes with')
                    similarity_graph.set_edge_attribute(edge_id, "overlap metric", similarity["subsumes"])
                    similarity_graph.set_edge_attribute(edge_id, "edge function", edge_function)

                    if(similarity["subsumes"] > 0.4):
                        similarity_graph.set_edge_attribute(edge_id, "strength", "high")
                    else:
                        similarity_graph.set_edge_attribute(edge_id, "strength", "low")
                elif(target_gene_count == source_gene_count):
                    if(source_node_id not in similarity_graph[target_node_id] and target_node_id not in similarity_graph[source_node_id]):
                        edge_function = edge_overlap / (source_gene_count + target_gene_count - edge_overlap)

                        edge_id = similarity_graph.add_edge_between(source_node_id, target_node_id, attr_dict=atts, interaction='shares genes with')
                        similarity_graph.set_edge_attribute(edge_id, "overlap metric", similarity["subsumes"])
                        similarity_graph.set_edge_attribute(edge_id, "edge function", edge_function)

                        if(similarity["subsumes"] > 0.4):
                            similarity_graph.set_edge_attribute(edge_id, "strength", "high")
                        else:
                            similarity_graph.set_edge_attribute(edge_id, "strength", "low")
                else:
                    if(source_node_id in temp_similarity_graph[target_node_id]):
                        print "Converse edge exists.  Skipping " + str(source_node_id) + ", " + str(target_node_id)
                    else:
                        edge_function = edge_overlap / (source_gene_count + target_gene_count - edge_overlap)

                        edge_id = similarity_graph.add_edge_between(target_node_id, source_node_id, attr_dict=atts, interaction='shares genes with')
                        similarity_graph.set_edge_attribute(edge_id, "overlap metric", similarity["subsumes"])
                        similarity_graph.set_edge_attribute(edge_id, "edge function", edge_function)

                        if(similarity["subsumes"] > 0.4):
                            similarity_graph.set_edge_attribute(edge_id, "strength", "high")
                        else:
                            similarity_graph.set_edge_attribute(edge_id, "strength", "low")


            count = count + 1

    for remove_this_node in remove_super_nodes:
        similarity_graph.remove_node(remove_this_node)

    return similarity_graph




