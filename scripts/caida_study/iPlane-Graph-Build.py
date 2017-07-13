import os
import pickle

# GOAL:
# Build the graph structure that will be used to build the graph from the
# iPlane dataset

# Dictionnary containing the AS that are present in the currated CAIDA topology
# Key: AS number
# Value: AS number
caida_ases = {}

# Dictionnary containing the interesting ASes for which PoPs need to be
# included
# Key: AS number
# Value: AS number
interesting_ases = {}

# Dictionnary containing the edges of the currated CAIDA Topology
# Key: Edge name
# Value: Edge vector
# [0:source=source, 1:target=target, 2: type=type]
caida_edges = {}

##### New data #####

# Dictionnary containing the PoPs connected to a given PoP
# Key: PoP number
# Value: Dictionnary containg the PoPs
pop_relatedpops = {}

# Dictionnary containing the edges
# Key: Edge name
# Value: Edge vector
# [0:source pop, 1:target pop, 2:latency total, 3:number of occurences,
#  4: relationship]
edges = {}

# Dictionnary containing the PoP associated to an IP
# Key: PoP number
# Value: AS number
pop_as = {}

pickle_dir = "pickle/confirmed/"
# pickle_dir = "pickle/"

print "\n=== iPlane-Graph-Build ===\n"

######################################################################## STEP 2

print "Step 1: loading data..."

print "Loading caida_ases dictionnary..."

caida_ases_path = pickle_dir + "caida_ases.pickle"
caida_ases_path = os.path.relpath(caida_ases_path)

with open(caida_ases_path, 'rb') as handle:
    caida_ases = pickle.load(handle)

print "Length of caida_ases: " + str(len(caida_ases))

print "Loading interesting_ases dictionnary..."

interesting_ases_path = pickle_dir + "interesting_ases.pickle"
interesting_ases_path = os.path.relpath(interesting_ases_path)

with open(interesting_ases_path, 'rb') as handle6:
    interesting_ases = pickle.load(handle6)

print "Length of interesting_ases: " + str(len(interesting_ases))

print "Loading caida_edges dictionnary..."

caida_edges_path = pickle_dir + "caida_edges.pickle"
caida_edges_path = os.path.relpath(caida_edges_path)

with open(caida_edges_path, 'rb') as handle2:
    caida_edges = pickle.load(handle2)

print "Length of caida_edges: " + str(len(caida_edges))

print "Loading pop_as dictionnary..."

pop_as_path = pickle_dir + "pop_as.pickle"
pop_as_path = os.path.relpath(pop_as_path)

with open(pop_as_path, 'rb') as handle3:
    pop_as = pickle.load(handle3)

print "Length of pop_as: " + str(len(pop_as))

print "Loading as_pops dictionnary..."

as_pops_path = pickle_dir + "as_pops.pickle"
as_pops_path = os.path.relpath(as_pops_path)

with open(as_pops_path, 'rb') as handle4:
    as_pops = pickle.load(handle4)

print "Length of as_pops: " + str(len(as_pops))

######################################################################## STEP 2

print "Step 2: parsing inter_pop_links txt files..."

# dir_path = '../Data/20150713/test-1/inter_pop_links/'
dir_path = '../Data/20150713/inter_pop_links/'

for dirname, dirnames, filenames in os.walk(dir_path):
    for filename in filenames:
        if not filename.startswith('.'):

            print "File: " + filename

            with open(os.path.join(dirname, filename), 'rb') as txt:
                while True:
                    line = txt.readline()
                    if not line:
                        break

                    link_elements = line.split(" ")
                    pop_1 = link_elements[0]
                    asn_1 = link_elements[1]
                    pop_2 = link_elements[2]
                    asn_2 = link_elements[3]

                    # Dealing with pop-AS association innacuracies
                    precondition_1_1 = not pop_1 in pop_as
                    precondition_1_2 = asn_1 == "3303"
                    precondition_1 = precondition_1_1 and precondition_1_2
                    precondition_2_1 = not pop_2 in pop_as
                    precondition_2_2 = asn_2 == "3303"
                    precondition_2 = precondition_2_1 and precondition_2_2

                    if precondition_1 or precondition_2:
                        continue

                    as_list_1 = []
                    if pop_1 in pop_as:
                        as_list_1 = pop_as[pop_1]
                    else:
                        print "PoP not in pop_as " + pop_1
                        as_list_1 = [asn_1]

                    as_list_2 = []
                    if pop_2 in pop_as:
                        as_list_2 = pop_as[pop_2]
                    else:
                        print "PoP not in pop_as " + pop_2
                        as_list_2 = [asn_2]

                    crosspairs = [(a, b) for a in as_list_1 for b in as_list_2]

                    for pair in crosspairs:
                        asn_1 = pair[0]
                        asn_2 = pair[1]

                        condition_1 = asn_1 in interesting_ases
                        condition_2 = asn_2 in interesting_ases
                        if condition_1 and condition_2:

                            latency = link_elements[4].rstrip('\r\n')
                            latency = int(latency)

                            popedge_1 = pop_1 + "-" + asn_1
                            popedge_2 = pop_2 + "-" + asn_2

                            # Put each pop in one another's
                            # pop_relatedpops dictionnary
                            if not popedge_1 in pop_relatedpops:
                                pop_relatedpops[popedge_1] = {}
                            pop_relatedpops[popedge_1][popedge_2] = popedge_2

                            if not popedge_2 in pop_relatedpops:
                                pop_relatedpops[popedge_2] = {}
                            pop_relatedpops[popedge_2][popedge_1] = popedge_1

                            # add the two directed edge in edges dictionnary if
                            # necessary

                            # The first one...
                            first_edge_name = popedge_1 + "-" + popedge_2
                            if not first_edge_name in edges:
                                first_edge = [popedge_1,
                                              popedge_2,
                                              0,
                                              0,
                                              0]
                                edges[first_edge_name] = first_edge
                            first_edge = edges[first_edge_name]
                            if latency >= 0:
                                first_edge[2] += latency
                                first_edge[3] += 1
                            if asn_1 != asn_2:
                                caida_edge_name = asn_1 + "-" + asn_2
                                # See if this raises an issue
                                if not caida_edge_name in caida_edges:
                                    first_edge[4] = 5
                                else:
                                    caida_edge = caida_edges[caida_edge_name]
                                    first_edge_relationship = caida_edge[2]
                                    first_edge[4] = int(first_edge_relationship)

                            # The second one...
                            second_edge_name = popedge_2 + "-" + popedge_1
                            if not second_edge_name in edges:
                                second_edge = [popedge_2,
                                               popedge_1,
                                               0,
                                               0,
                                               0]
                                edges[second_edge_name] = second_edge
                            second_edge = edges[second_edge_name]
                            if latency >= 0:
                                second_edge[2] += latency
                                second_edge[3] += 1
                            if asn_1 != asn_2:
                                caida_edge_name = asn_2 + "-" + asn_1
                                # See if this raises an issue
                                if not caida_edge_name in caida_edges:
                                    second_edge[4] = 5
                                else:
                                    caida_edge = caida_edges[caida_edge_name]
                                    second_edge_relationship = caida_edge[2]
                                    second_edge[4] = int(second_edge_relationship)

######################################################################## STEP 3

print "Step 3: write edges dictionnary in iPlane_edges.pickle..."

edges_path = os.path.relpath(pickle_dir + "iPlane_edges.pickle")

with open(edges_path, 'wb') as handle5:
    pickle.dump(edges, handle5)

print "Step 3 DONE, " + str(len(edges)) + " edges in iPlane_edges dictionnary"

######################################################################## STEP 4

print "Step 4: write pop_relatedpops dict in iPlane_pop_relatedpops.pickle..."

pop_relatedpops_path = pickle_dir + "iPlane_pop_relatedpops.pickle"
pop_relatedpops_path = os.path.relpath(pop_relatedpops_path)

with open(pop_relatedpops_path, 'wb') as handle6:
    pickle.dump(pop_relatedpops, handle6)

l_p = str(len(pop_relatedpops))
print "Step 4 DONE, " + l_p + " pops in pop_relatedpops dictionnary"
