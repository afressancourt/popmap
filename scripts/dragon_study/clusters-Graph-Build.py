import os
import pickle

# dir_path = '../Data/20150713/inter_pop_links-test/'
dir_path = '../Data/20150713/inter_pop_links/'

# pickle_dir = "pickle/"
pickle_dir = "pickle/confirmed/"

best_clusters = {}
best_cluster_pops = {}
best_pop_clusters = {}
best_as_clusters = {}
best_cluster_as = {}

dragon_edges = {}

##### New data #####

cluster_relatedclusters = {}

# Dictionnary containing the edges
# Key: Edge name
# Value: Edge vector
# [0:source pop, 1:target pop, 2:latency total, 3:number of occurences,
#  4: relationship]
cluster_edges = {}

print "\n=== clusters-Graph-Build ===\n"

######################################################################## STEP 2

print "Step 1: loading data..."

print "Loading best_cluster_pops dictionnary..."

best_cluster_pops_path = pickle_dir + "best_cluster_pops.pickle"
best_cluster_pops_path = os.path.relpath(best_cluster_pops_path)

with open(best_cluster_pops_path, 'rb') as handle:
    best_cluster_pops = pickle.load(handle)

print "Length of best_cluster_pops: " + str(len(best_cluster_pops))

print "Loading best_pop_clusters dictionnary..."

best_pop_clusters_path = pickle_dir + "best_pop_clusters.pickle"
best_pop_clusters_path = os.path.relpath(best_pop_clusters_path)

with open(best_pop_clusters_path, 'rb') as handle:
    best_pop_clusters = pickle.load(handle)

print "Length of best_pop_clusters: " + str(len(best_pop_clusters))

print "Loading best_as_clusters dictionnary..."

best_as_clusters_path = pickle_dir + "best_as_clusters.pickle"
best_as_clusters_path = os.path.relpath(best_as_clusters_path)

with open(best_as_clusters_path, 'rb') as handle:
    best_as_clusters = pickle.load(handle)

print "Length of best_as_clusters: " + str(len(best_as_clusters))

print "Loading best_cluster_as dictionnary..."

best_cluster_as_path = pickle_dir + "best_cluster_as.pickle"
best_cluster_as_path = os.path.relpath(best_cluster_as_path)

with open(best_cluster_as_path, 'rb') as handle:
    best_cluster_as = pickle.load(handle)

print "Length of best_cluster_as: " + str(len(best_cluster_as))

print "Loading dragon_edges dictionnary..."

dragon_edges_path = pickle_dir + "dragon_edges.pickle"
dragon_edges_path = os.path.relpath(dragon_edges_path)

with open(dragon_edges_path, 'rb') as handle:
    dragon_edges = pickle.load(handle)

print "Length of dragon_edges: " + str(len(dragon_edges))

######################################################################## STEP 2

print "Step 2: parsing inter_pop_links txt files..."

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
                    pop_2 = link_elements[2]

                    # Dealing with pop-AS association innacuracies

                    precondition_1 = not pop_1 in best_pop_clusters
                    precondition_2 = not pop_2 in best_pop_clusters

                    if precondition_1 or precondition_2:
                        continue

                    clusters_1 = best_pop_clusters[pop_1]
                    clusters_2 = best_pop_clusters[pop_2]

                    cross = [(a, b) for a in clusters_1 for b in clusters_2]

                    for pair in cross:
                        cluster_1 = pair[0]
                        cluster_2 = pair[1]

                        asn_1 = best_cluster_as[cluster_1]
                        asn_2 = best_cluster_as[cluster_2]

                        latency = link_elements[4].rstrip('\r\n')
                        latency = int(latency)

                        # Put each cluster in one another's
                        # cluster_relatedclusters dictionnary
                        if not cluster_1 in cluster_relatedclusters:
                            cluster_relatedclusters[cluster_1] = {}
                        cluster_relatedclusters[cluster_1][cluster_2] = cluster_2

                        if not cluster_2 in cluster_relatedclusters:
                            cluster_relatedclusters[cluster_2] = {}
                        cluster_relatedclusters[cluster_2][cluster_1] = cluster_1

                        # add the two directed edge in edges dictionnary if
                        # necessary

                        # The first one...
                        first_edge_name = cluster_1 + "-" + cluster_2
                        if not first_edge_name in cluster_edges:
                            first_edge = [cluster_1,
                                          cluster_2,
                                          0,
                                          0,
                                          0]
                            cluster_edges[first_edge_name] = first_edge
                        first_edge = cluster_edges[first_edge_name]
                        if latency >= 0:
                            first_edge[2] += latency
                            first_edge[3] += 1
                        if asn_1 != asn_2:
                            dragon_edge_name = asn_1 + "-" + asn_2
                            # See if this raises an issue
                            if not dragon_edge_name in dragon_edges:
                                first_edge[4] = 5
                            else:
                                dragon_edge = dragon_edges[dragon_edge_name]
                                first_edge_relationship = dragon_edge[2]
                                first_edge[4] = int(first_edge_relationship)

                        # The second one...
                        second_edge_name = cluster_2 + "-" + cluster_1
                        if not second_edge_name in cluster_edges:
                            second_edge = [cluster_2,
                                           cluster_1,
                                           0,
                                           0,
                                           0]
                            cluster_edges[second_edge_name] = second_edge
                        second_edge = cluster_edges[second_edge_name]
                        if latency >= 0:
                            second_edge[2] += latency
                            second_edge[3] += 1
                        if asn_1 != asn_2:
                            dragon_edge_name = asn_2 + "-" + asn_1
                            # See if this raises an issue
                            if not dragon_edge_name in dragon_edges:
                                second_edge[4] = 5
                            else:
                                dragon_edge = dragon_edges[dragon_edge_name]
                                second_edge_relationship = dragon_edge[2]
                                second_edge[4] = int(second_edge_relationship)

                        # print "##############"
                        # print cluster_1 + ": " + asn_1
                        # print cluster_2 + ": " + asn_2
                        # print "first_edge: " + str(first_edge)
                        # print "second_edge: " + str(second_edge)

######################################################################## STEP N

print "Step 3: write cluster_relatedclusters dictionnary in cluster_relatedclusters.pickle..."

cluster_relatedclusters_path = pickle_dir + "cluster_relatedclusters.pickle"
cluster_relatedclusters_path = os.path.relpath(cluster_relatedclusters_path)

with open(cluster_relatedclusters_path, 'wb') as handle:
    pickle.dump(cluster_relatedclusters, handle)

print "Step 3 DONE, " + str(len(cluster_relatedclusters)) + " elements in dictionnary"

######################################################################## STEP N

print "Step 4: write cluster_edges dictionnary in cluster_edges.pickle..."

cluster_edges_path = os.path.relpath(pickle_dir + "cluster_edges.pickle")

with open(cluster_edges_path, 'wb') as handle:
    pickle.dump(cluster_edges, handle)

print "Step 4 DONE, " + str(len(cluster_edges)) + " elements in dictionnary"
