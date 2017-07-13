import os
from igraph import *
import pickle

# GOAL:
# Build the directed AS graph that we will use to compute the possible paths.

##### New data #####

# Dictionnary containing the AS that are present in the currated CAIDA topology
# Key: AS number
# Value: AS number
caida_ases = {}

caida_dir = "../Data/curated-caida-topology/"

pickle_dir = "pickle/confirmed/"
# pickle_dir = "pickle/"

print "\n=== Graph-AS-Directed-Build ===\n"

######################################################################## STEP 1

print "Step 1: parsing topology.201309.txt..."

topology_path = caida_dir + "topology.201309.txt"
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

        if not edge_source in caida_ases:
            caida_ases[edge_source] = edge_source
        if not edge_destination in caida_ases:
            caida_ases[edge_destination] = edge_destination

######################################################################## STEP 2

print "Step 2: write caida_ases.pickle..."

caida_ases_path = os.path.relpath(pickle_dir + "caida_ases.pickle")

with open(caida_ases_path, 'wb') as handle:
    pickle.dump(caida_ases, handle)

print "Step 3 DONE"
