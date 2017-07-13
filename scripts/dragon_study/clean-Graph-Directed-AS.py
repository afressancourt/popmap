import os
from igraph import *
import pickle
import utils

# GOAL:
# Find the ASes that only have client-provider relationships to lower the
# number of nodes to include in the graph

# Dictionnary containing the ASes associated to an IXP that are present in the
# iPlane dataset
# Key: IXP Public id according to PeeringDB
# Value: Dictionnary containing the ASes
ixp_confirmed_ases = {}

# Dictionnary containing the ASes for which we want to build the iPlane graph.
# We remove the stub ASes as well as the ASes that do not participate in any
# IXP
# Key: AS number
# Value: AS number
interesting_ases = {}

# Dictionnary containing the CSP ASes
# Key: AS number
# Value: AS number
csp_ases = {}

# Dictionnary containing the AS that are present in the Dragon topology
# Key: AS number
# Value: AS number
dragon_ases = {}

as_graph = Graph()

pickle_dir = "pickle/confirmed/"
# pickle_dir = "pickle/"

# method = "-method1"
method = "-method2"

csp_source = "../Data/CSP_AS-complementary.txt"

print "\n=== Graph-AS-Directed-Study ===\n"

######################################################################## STEP 1

print "Step 1: loading data.."

print "Loading graph..."

as_graph_path = pickle_dir + "as-directed-graph" + method + ".pickle"
as_graph_path = os.path.relpath(as_graph_path)

with open(as_graph_path, 'rb') as handle:
    as_graph = pickle.load(handle)

print "Loading ixp_confirmed_ases dictionnary..."

ixp_confirmed_ases_path = pickle_dir + "ixp_confirmed_ases_3.pickle"
ixp_confirmed_ases_path = os.path.relpath(ixp_confirmed_ases_path)

with open(ixp_confirmed_ases_path, 'rb') as handle2:
    ixp_confirmed_ases = pickle.load(handle2)

print "Length of ixp_confirmed_ases: " + str(len(ixp_confirmed_ases))

print "Loading dragon_ases dictionnary..."

dragon_ases_path = pickle_dir + "dragon_ases.pickle"
dragon_ases_path = os.path.relpath(dragon_ases_path)

with open(dragon_ases_path, 'rb') as handle3:
    dragon_ases = pickle.load(handle3)

print "Length of dragon_ases: " + str(len(dragon_ases))

print "Step 1 DONE"

######################################################################## STEP 2

print "Step 2: Adding the CSP ASes in the interesting_ases dictionnary..."

csp_path = os.path.relpath(csp_source)

with open(csp_path, 'rb') as txt:

    while True:
        line = txt.readline()
        if not line:
            break
        csp_element = line.split(";")
        asn = csp_element[0]
        if (asn in dragon_ases) and (not asn in csp_ases):
            csp_ases[asn] = asn

print "Number of CSP ASes: " + str(len(csp_ases))

for asn in csp_ases:
    if not asn in interesting_ases:
        interesting_ases[asn] = asn

print "Number of CSP ASes in interesting_ases: " + str(len(interesting_ases))


print "Step 2 DONE"

####################################################################### STEP2_2

print "Step 2_2: Adding the ASes at IXPs to the interesting_ases dict..."

for ixp in ixp_confirmed_ases:
    confirmed_ases = ixp_confirmed_ases[ixp]
    for asn in confirmed_ases:
        if (asn in dragon_ases) and (not asn in interesting_ases):
            interesting_ases[asn] = asn

print "Number of ASes in interesting_ases: " + str(len(interesting_ases))

print "Step 2_2 DONE"

######################################################################## STEP 3

print "Step 3: looking for stub ASes in the graph..."

no_stub_ases = {}

for as_node in as_graph.vs:
    edges = as_graph.incident(as_node, mode=OUT)
    stub = True
    for edge in edges:
        edge_type = as_graph.es[edge]["relationship"]
        if edge_type > 0 and edge_type < 3:
            stub = False
    if not stub:
        no_stub_ases[as_node["name"]] = as_node["name"]


print "Number of non-stub ASes: " + str(len(no_stub_ases))

for asn in no_stub_ases:
    if not asn in interesting_ases:
        interesting_ases[asn] = asn

print "Number of interesting ASes: " + str(len(interesting_ases))

######################################################################## STEP 4

print "Step 4: write interesting_ases.pickle..."

interesting_ases_path = os.path.relpath(pickle_dir + "interesting_ases.pickle")

with open(interesting_ases_path, 'wb') as handle4:
    pickle.dump(interesting_ases, handle4)

print "Step 4 DONE"

######################################################################## STEP 5

print "Step 5: write csp_ases.pickle..."

csp_ases_path = os.path.relpath(pickle_dir + "csp_ases.pickle")

with open(csp_ases_path, 'wb') as handle5:
    pickle.dump(csp_ases, handle5)

print "Step 5 DONE"
