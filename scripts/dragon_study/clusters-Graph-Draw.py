import os
import pickle
from igraph import *

# Dictionnary containing the edges
# Key: Edge name
# Value: Edge vector
# [0:source pop, 1:target pop, 2:latency total, 3:number of occurences,
#  4: relationship]
cluster_edges = {}

cluster_relatedclusters = {}

##### New data #####

# pickle_dir = "pickle/"
pickle_dir = "pickle/confirmed/"

cluster_directed_graph = Graph(directed=True)

print "\n=== cluster-Graph-Build ===\n"

######################################################################## STEP 1

print "Step 1: loading data..."

print "Loading cluster_edges dictionnary..."

cluster_edges_path = pickle_dir + "cluster_edges.pickle"
cluster_edges_path = os.path.relpath(cluster_edges_path)

with open(cluster_edges_path, 'rb') as handle:
    cluster_edges = pickle.load(handle)

print "Length of cluster_edges: " + str(len(cluster_edges))

print "Loading cluster_relatedclusters dictionnary..."

cluster_relatedclusters_path = pickle_dir + "cluster_relatedclusters.pickle"
cluster_relatedclusters_path = os.path.relpath(cluster_relatedclusters_path)

with open(cluster_relatedclusters_path, 'rb') as handle2:
    cluster_relatedclusters = pickle.load(handle2)

print "Length of cluster_relatedclusters: " + str(len(cluster_relatedclusters))

print "Loading best_cluster_as dictionnary..."

best_cluster_as_path = pickle_dir + "best_cluster_as.pickle"
best_cluster_as_path = os.path.relpath(best_cluster_as_path)

with open(best_cluster_as_path, 'rb') as handle:
    best_cluster_as = pickle.load(handle)

print "Length of best_cluster_as: " + str(len(best_cluster_as))

######################################################################## STEP 2

print "Step 2: Writing cluster_directed_graph ..."

print "Adding nodes to the graph..."
print "Number of PoPs: " + str(len(cluster_relatedclusters))

int_id = 1
for cluster in cluster_relatedclusters:
    v = cluster_directed_graph.add_vertex(id=int_id,
                                          name=cluster
                                          )
    int_id += 1

print "DONE, Clusters added"
print summary(cluster_relatedclusters)

print "Adding edges to the graph...."
print "Number of edges: " + str(len(cluster_edges))

edgeVector = []
for edge in cluster_edges:
    source = cluster_edges[edge][0]
    source = cluster_directed_graph.vs.find(name=source).index
    destination = cluster_edges[edge][1]
    destination = cluster_directed_graph.vs.find(name=destination).index
    edgeVector += [(source, destination)]

cluster_directed_graph.add_edges(edgeVector)

print "DONE, edges added"
print summary(cluster_directed_graph)

print "Adding node properties..."

for node in cluster_directed_graph.vs:
    cluster_name = node["name"]
    asn = best_cluster_as[cluster_name]
    node["as"] = asn
    print node

print "DONE, node properties added"

print "Adding edge properties..."

for edge in cluster_directed_graph.es:
    source_name = cluster_directed_graph.vs[edge.source]["name"]
    target_name = cluster_directed_graph.vs[edge.target]["name"]
    edge_name = source_name + "-" + target_name
    latency_total = cluster_edges[edge_name][2]
    occurences = cluster_edges[edge_name][3]
    relationship = cluster_edges[edge_name][4]
    latency = 9999
    if occurences > 0:
        latency = latency_total/occurences
    edge["latency_total"] = latency_total
    edge["occurences"] = occurences
    edge["latency"] = latency
    edge["relationship"] = relationship

print "DONE, Edge properties added"

######################################################################## STEP 3

print "Step 3: save cluster_directed_graph in cluster_directed_graph.pickle..."

cluster_directed_graph_path = pickle_dir + "cluster_directed_graph.pickle"
cluster_directed_graph_path = os.path.relpath(cluster_directed_graph_path)

with open(cluster_directed_graph_path, 'wb') as handle4:
    pickle.dump(cluster_directed_graph, handle4)

print "Step 3 DONE"
