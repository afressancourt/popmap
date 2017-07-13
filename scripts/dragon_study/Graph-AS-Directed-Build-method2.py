import os
from igraph import *
import pickle

# GOAL:
# Build the directed AS graph that we will use to compute the possible paths.

##### New data #####

# Dictionnary containing the graph's nodes
# Key: Node name
# Value: Node vector
nodes = {}

# Dictionnary containing the edges
# Key: Edge name
# Value: Edge vector
# [0:source=source, 1:target=target, 2: type=type]
edges = {}

# dragon_dir = "../Data/Dragon-topology/test-1/"
dragon_dir = "../Data/Dragon-topology/"

pickle_dir = "pickle/confirmed/"
# pickle_dir = "pickle/"

print "\n=== Graph-AS-Directed-Build ===\n"

######################################################################## STEP 1

print "Step 1: parsing topology.201309.txt..."

topology_path = dragon_dir + "topology.201309.txt"
topology_path = os.path.relpath(topology_path)

with open(topology_path, 'rb') as txt:

    while True:
        line = txt.readline()
        if not line:
            break
        #print line
        if line.startswith("#"):
            continue

        directed_graph_elements = line.split(" ")
        edge_source = directed_graph_elements[0]
        edge_destination = directed_graph_elements[1]
        edge_type = directed_graph_elements[2].rstrip('\r\n')

        if not edge_source in nodes:
            nodes[edge_source] = int(edge_source)
        if not edge_destination in nodes:
            nodes[edge_destination] = int(edge_destination)

        edge_name = edge_source + "-" + edge_destination

        if not edge_name in edges:
            edges[edge_name] = [edge_source,
                                edge_destination,
                                edge_type]

######################################################################## STEP 2

print "Step 2: write Graph method 2..."

g = Graph(directed=True)

i = 0
print "Number of nodes: " + str(len(nodes))
for node in nodes:
    i += 1
    if i % 1000 == 0:
        print "Node " + str(i) + " added"
    v = g.add_vertex(id=nodes[node],
                     name=node
                     )

edgeVector = []
i = 0
print "Number of edges: " + str(len(edges))
for edge in edges:
    i += 1
    if i % 1000 == 0:
        print "Edge " + str(i) + " added"
    relationship = int(edges[edge][2])
    source = g.vs.find(name=edges[edge][0]).index
    destination = g.vs.find(name=edges[edge][1]).index
    edgeVector += [(source, destination)]

g.add_edges(edgeVector)

for edge in g.es:
    source_name = g.vs[edge.source]["name"]
    target_name = g.vs[edge.target]["name"]
    edge_name = source_name + "-" + target_name
    relationship = int(edges[edge_name][2])
    edge["relationship"] = relationship

######################################################################## STEP 3

print "Step 3: save graph in as-directed-graph.pickle..."

graph_path = os.path.relpath(pickle_dir + "as-directed-graph-method2.pickle")

with open(graph_path, 'wb') as handle:
    pickle.dump(g, handle)

print "Step 3 DONE"

######################################################################## STEP 4

print "Step 4: save edges in dragon_edges.pickle..."

edges_path = os.path.relpath(pickle_dir + "dragon_edges.pickle")

with open(edges_path, 'wb') as handle2:
    pickle.dump(edges, handle2)

print "Step 4 DONE"
