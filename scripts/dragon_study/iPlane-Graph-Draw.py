import os
import pickle
from igraph import *

# GOAL:
# Draw the directed graph from the data built by iPlane-Graph-Build.py

# Dictionnary containing the edges
# Key: Edge name
# Value: Edge vector
# [0:source pop, 1:target pop, 2:latency total, 3:number of occurences,
#  4: relationship]
iPlane_edges = {}

# Dictionnary containing the PoPs connected to a given PoP
# Key: PoP number
# Value: Dictionnary containg the PoPs
iPlane_pop_relatedpops = {}

##### New data #####

pickle_dir = "pickle/confirmed/"
# pickle_dir = "pickle/"

iPlane_directed_graph = Graph(directed=True)

print "\n=== iPlane-Graph-Build ===\n"

######################################################################## STEP 1

print "Step 1: loading data..."

print "Loading iPlane_edges dictionnary..."

iPlane_edges_path = pickle_dir + "iPlane_edges.pickle"
iPlane_edges_path = os.path.relpath(iPlane_edges_path)

with open(iPlane_edges_path, 'rb') as handle:
    iPlane_edges = pickle.load(handle)

print "Length of iPlane_edges: " + str(len(iPlane_edges))

print "Loading iPlane_pop_relatedpops dictionnary..."

iPlane_pop_relatedpops_path = pickle_dir + "iPlane_pop_relatedpops.pickle"
iPlane_pop_relatedpops_path = os.path.relpath(iPlane_pop_relatedpops_path)

with open(iPlane_pop_relatedpops_path, 'rb') as handle2:
    iPlane_pop_relatedpops = pickle.load(handle2)

print "Length of iPlane_pop_relatedpops: " + str(len(iPlane_pop_relatedpops))

######################################################################## STEP 2

print "Step 2: Writing iPlane_directed_graph ..."

print "Adding nodes to the graph..."
print "Number of PoPs: " + str(len(iPlane_pop_relatedpops))

int_id = 1
for pop in iPlane_pop_relatedpops:
    # int_id = int(pop)
    v = iPlane_directed_graph.add_vertex(id=int_id,
                                         name=pop
                                         )
    int_id += 1

print "DONE, PoPs added"
print summary(iPlane_directed_graph)

print "Adding edges to the graph...."
print "Number of edges: " + str(len(iPlane_edges))

edgeVector = []
for edge in iPlane_edges:
    source = iPlane_edges[edge][0]
    source = iPlane_directed_graph.vs.find(name=source).index
    destination = iPlane_edges[edge][1]
    destination = iPlane_directed_graph.vs.find(name=destination).index
    edgeVector += [(source, destination)]

iPlane_directed_graph.add_edges(edgeVector)

print "DONE, edges added"
print summary(iPlane_directed_graph)

print "Adding node properties..."

for node in iPlane_directed_graph.vs:
    pop_name = node["name"]
    # asn = iPlane_pop_as[pop_name]
    asn = pop_name.split('-')[1]
    node["as"] = asn

print "DONE, node properties added"

print "Adding edge properties..."

for edge in iPlane_directed_graph.es:
    source_name = iPlane_directed_graph.vs[edge.source]["name"]
    target_name = iPlane_directed_graph.vs[edge.target]["name"]
    edge_name = source_name + "-" + target_name
    latency_total = iPlane_edges[edge_name][2]
    occurences = iPlane_edges[edge_name][3]
    relationship = iPlane_edges[edge_name][4]
    latency = 9999
    if occurences > 0:
        latency = latency_total/occurences
    edge["latency_total"] = latency_total
    edge["occurences"] = occurences
    edge["latency"] = latency
    edge["relationship"] = relationship

print "DONE, Edge properties added"

######################################################################## STEP 3

print "Step 3: save iPlane_directed_graph in iPlane_directed_graph.pickle..."

iPlane_directed_graph_path = pickle_dir + "iPlane_directed_graph.pickle"
iPlane_directed_graph_path = os.path.relpath(iPlane_directed_graph_path)

with open(iPlane_directed_graph_path, 'wb') as handle4:
    pickle.dump(iPlane_directed_graph, handle4)

print "Step 3 DONE"
