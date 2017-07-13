import os
import pickle
from igraph import *

# pickle_dir = "pickle/"
pickle_dir = "pickle/confirmed/"

##### New data #####

print "\n=== cspclusters-AS-Graph-Draw ===\n"

######################################################################## STEP 1

print "Step 1: loading data..."

print "Loading provider_asns dictionnary..."

provider_asns_path = pickle_dir + "provider_asns.pickle"
provider_asns_path = os.path.relpath(provider_asns_path)

with open(provider_asns_path, 'rb') as handle:
    provider_asns = pickle.load(handle)

print "Length of dragon_edges: " + str(len(provider_asns))

######################################################################## STEP 2

print "Step 2: Writing cluster_AS_directed_graph ..."


def drawGraph(node_relatednodes, provider_edges):

    cluster_AS_directed_graph = Graph(directed=True)

    int_id = 1
    for node in node_relatednodes:
        cluster_AS_directed_graph.add_vertex(id=int_id,
                                             name=node
                                             )
        int_id += 1

    edgeVector = []
    for edge in provider_edges:
        source = provider_edges[edge][0]
        source = cluster_AS_directed_graph.vs.find(name=source).index
        destination = provider_edges[edge][1]
        destination = cluster_AS_directed_graph.vs.find(name=destination).index
        edgeVector += [(source, destination)]

    cluster_AS_directed_graph.add_edges(edgeVector)

    for node in cluster_AS_directed_graph.vs:
        node_name = node["name"]
        if '++' in node_name:
            node["as"] = node_name.split('++')[0]
        else:
            node["as"] = node_name

    for edge in cluster_AS_directed_graph.es:
        source_name = cluster_AS_directed_graph.vs[edge.source]["name"]
        target_name = cluster_AS_directed_graph.vs[edge.target]["name"]
        edge_name = source_name + "-" + target_name
        latency_total = provider_edges[edge_name][2]
        occurences = provider_edges[edge_name][3]
        relationship = provider_edges[edge_name][4]
        latency = 9999
        if occurences > 0:
            latency = latency_total/occurences
        edge["latency_total"] = latency_total
        edge["occurences"] = occurences
        edge["latency"] = latency
        edge["relationship"] = relationship

    return cluster_AS_directed_graph

for provider in provider_asns:

    print "Drawing graph for " + provider

    node_relatednodes = {}

    path = pickle_dir + provider + "_node_relatednodes.pickle"
    path = os.path.relpath(path)

    with open(path, 'rb') as handle:
        node_relatednodes = pickle.load(handle)

    path = pickle_dir + provider + "_cluster_edges.pickle"
    path = os.path.relpath(path)

    provider_edges = {}

    with open(path, 'rb') as handle:
        provider_edges = pickle.load(handle)

    cluster_AS_directed_graph = drawGraph(node_relatednodes,
                                          provider_edges)
    print summary(cluster_AS_directed_graph)

    path = pickle_dir + provider + "_cluster_AS_directed_graph.pickle"
    path = os.path.relpath(path)

    with open(path, 'wb') as handle:
        pickle.dump(cluster_AS_directed_graph, handle)

    print provider + " DONE"
