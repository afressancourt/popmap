import os
from igraph import *
import pickle
import utils

# pickle_dir = "pickle/"
pickle_dir = "pickle/confirmed/"

dir_path = '../Data/20150713/inter_pop_links/'
# dir_path = '../Data/20150713/inter_pop_links-test/'

csp_path = '../Data/CSP_AS-complementary.txt'

##### Retrieved data #####

interesting_ases = {}

pop_as = {}

as_pops = {}

##### New data #####

interesting_graph_nodes = {}
interesting_graph_edges = {}
interesting_pops = {}

best_clusters = {}
best_cluster_pops = {}
best_pop_clusters = {}
best_as_clusters = {}
best_cluster_as = {}

##### Function #####


def fix_dendrogram(graph, cl):
    already_merged = set()
    for merge in cl.merges:
        already_merged.update(merge)

    num_dendrogram_nodes = graph.vcount() + len(cl.merges)
    not_merged_yet = sorted(set(xrange(num_dendrogram_nodes)) - already_merged)
    if len(not_merged_yet) < 2:
        return

    v1, v2 = not_merged_yet[:2]
    cl._merges.append((v1, v2))
    del not_merged_yet[:2]

    missing_nodes = xrange(num_dendrogram_nodes,
                           num_dendrogram_nodes + len(not_merged_yet))
    cl._merges.extend(izip(not_merged_yet, missing_nodes))
    cl._nmerges = graph.vcount()-1

print "\n=== csp-AS-clusters ===\n"

######################################################################## STEP 1

print "Step 1: load data..."

print "Loading interesting_ases from interesting_ases.pickle..."

interesting_ases_path = pickle_dir + "interesting_ases.pickle"
interesting_ases_path = os.path.relpath(interesting_ases_path)

with open(interesting_ases_path, 'rb') as handle:
    interesting_ases = pickle.load(handle)

print "Length of interesting_ases: " + str(len(interesting_ases))

print "Loading pop_as dictionnary..."

pop_as_path = pickle_dir + "pop_as.pickle"
pop_as_path = os.path.relpath(pop_as_path)

with open(pop_as_path, 'rb') as handle2:
    pop_as = pickle.load(handle2)

print "Length of pop_as: " + str(len(pop_as))

print "Loading as_pops dictionnary..."

as_pops_path = pickle_dir + "as_pops.pickle"
as_pops_path = os.path.relpath(as_pops_path)

with open(as_pops_path, 'rb') as handle3:
    as_pops = pickle.load(handle3)

print "Length of as_pops: " + str(len(as_pops))

print "Step 1 DONE"

print "Step 1 bis: making sure that CSP ASes are in interesting_ases..."

csp_path = os.path.relpath(csp_path)

with open(csp_path, 'rb') as txt:
    while True:
        line = txt.readline()
        if not line:
            break
        line = line.rstrip('\r\n')
        line_elements = line.split(';')
        asn = line_elements[0]

        if not asn in interesting_ases:
            print "Problem in Interesting ASN " + asn
            interesting_ases[asn] = asn

######################################################################## STEP 2

print "Step 2: Building intra-AS graphes to find clusters..."

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
                    precondition_1 = not pop_1 in pop_as
                    precondition_2 = not pop_2 in pop_as

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

                        latency = link_elements[4].rstrip('\r\n')
                        latency = int(latency)

                        if asn_1 in interesting_ases:
                            if not asn_1 in interesting_graph_nodes:
                                interesting_graph_nodes[asn_1] = {}
                            interesting_graph_nodes[asn_1][pop_1] = pop_1
                            if not pop_1 in interesting_pops:
                                interesting_pops[pop_1] = asn_1

                        if asn_2 in interesting_ases:
                            if not asn_2 in interesting_graph_nodes:
                                interesting_graph_nodes[asn_2] = {}
                            interesting_graph_nodes[asn_2][pop_2] = pop_2
                            if not pop_2 in interesting_pops:
                                interesting_pops[pop_2] = asn_2

                            if asn_1 == asn_2:
                                if not asn_2 in interesting_graph_edges:
                                    interesting_graph_edges[asn_2] = {}
                                edge_name = utils.edge_name(pop_1, pop_2)
                                if not edge_name in interesting_graph_edges[asn_2]:
                                    edge = [pop_1,
                                            pop_2,
                                            0,
                                            0,
                                            1]
                                    interesting_graph_edges[asn_2][edge_name] = edge
                                interesting_graph_edge = interesting_graph_edges[asn_2][edge_name]
                                if latency >= 0:
                                    interesting_graph_edge[2] += latency
                                    interesting_graph_edge[3] += 1
                                    if latency > interesting_graph_edge[4]:
                                        interesting_graph_edge[4] = latency

print "Step 2 DONE"

######################################################################## STEP 3

print "Step 3: Building pop clusters in each AS..."

for asn in interesting_graph_nodes:
    if asn in interesting_graph_edges:
        as_graph = Graph()
        nodes = interesting_graph_nodes[asn]
        for node in nodes:
            as_graph.add_vertex(name=node)

        edgeVector = []
        edges = interesting_graph_edges[asn]
        for edge in edges:
            source = edges[edge][0]
            source = as_graph.vs.find(name=source).index
            destination = edges[edge][1]
            destination = as_graph.vs.find(name=destination).index
            edgeVector += [(source, destination)]
        as_graph.add_edges(edgeVector)

        for edge in as_graph.es:
            source_name = as_graph.vs[edge.source]["name"]
            target_name = as_graph.vs[edge.target]["name"]
            edge_name = utils.edge_name(source_name, target_name)
            latency_total = edges[edge_name][2]
            occurences = edges[edge_name][3]
            max_latency = edges[edge_name][4]
            latency = 9999
            occurency_weight = 999
            if occurences > 0:
                latency = int(round(latency_total/occurences, 0)) + 1
                occurence_weight = int(round(100/occurences, 0)) + 1
            edge['latency_total'] = latency_total
            edge['occurences'] = occurences
            edge['latency'] = latency
            edge['max_latency'] = max_latency
            edge['occurence_weight'] = occurence_weight

        infomap_clusters = as_graph.community_infomap()
        dendrogram = as_graph.community_walktrap()
        try:
            walktrap_clusters = dendrogram.as_clustering()
        except InternalError:
            fix_dendrogram(as_graph, dendrogram)
            walktrap_clusters = dendrogram.as_clustering()
        if len(walktrap_clusters) > len(infomap_clusters):
            clusters = walktrap_clusters
        else:
            clusters = infomap_clusters
        best_clusters[asn] = clusters

        if not asn in best_as_clusters:
            best_as_clusters[asn] = {}

        for i in range(0, len(clusters)):
            cluster_name = asn + "++" + str(i)
            best_as_clusters[asn][cluster_name] = cluster_name
            best_cluster_as[cluster_name] = asn
            best_cluster_pops[cluster_name] = {}

            for pop in clusters[i]:
                pop_name = as_graph.vs[pop]["name"]
                best_cluster_pops[cluster_name][pop_name] = pop_name
                if not pop_name in best_pop_clusters:
                    best_pop_clusters[pop_name] = []
                best_pop_clusters[pop_name] = best_pop_clusters[pop_name] + [cluster_name]

        cluster_length = str(len(best_as_clusters[asn]))
        print "AS: " + asn + " has " + cluster_length + " clusters"

    else:
        # No internal edges
        pops = interesting_graph_nodes[asn]
        i = 0
        for pop in pops:
            i += 1
            cluster_name = asn + "++" + str(i)

            if not asn in best_as_clusters:
                best_as_clusters[asn] = {}

            best_as_clusters[asn][cluster_name] = cluster_name
            best_cluster_as[cluster_name] = asn

            best_cluster_pops[cluster_name] = {}
            best_cluster_pops[cluster_name][pop] = pop

            if not pop in best_pop_clusters:
                best_pop_clusters[pop] = []
            best_pop_clusters[pop] = best_pop_clusters[pop] + [cluster_name]

        cluster_length = str(len(best_as_clusters[asn]))
        print "AS: " + asn + " has " + cluster_length + " clusters"

print "Step 3 DONE"

######################################################################## STEP 4

print "Step 4: write best_clusters.pickle..."

best_clusters_path = pickle_dir + "best_clusters.pickle"
best_clusters_path = os.path.relpath(best_clusters_path)

with open(best_clusters_path, 'wb') as handle:
    pickle.dump(best_clusters, handle)

print "Step 4 DONE, " + str(len(best_clusters)) + " elements in the dict."

######################################################################## STEP 5

print "Step 5: write best_cluster_pops.pickle..."

best_cluster_pops_path = pickle_dir + "best_cluster_pops.pickle"
best_cluster_pops_path = os.path.relpath(best_cluster_pops_path)

with open(best_cluster_pops_path, 'wb') as handle:
    pickle.dump(best_cluster_pops, handle)

print "Step 5 DONE, " + str(len(best_cluster_pops)) + " elements in the dict."

######################################################################## STEP 6

print "Step 6: write best_pop_clusters.pickle..."

best_pop_clusters_path = pickle_dir + "best_pop_clusters.pickle"
best_pop_clusters_path = os.path.relpath(best_pop_clusters_path)

with open(best_pop_clusters_path, 'wb') as handle:
    pickle.dump(best_pop_clusters, handle)

print "Step 6 DONE, " + str(len(best_pop_clusters)) + " elements in the dict."

######################################################################## STEP 7

print "Step 7: write best_as_clusters.pickle..."

best_as_clusters_path = pickle_dir + "best_as_clusters.pickle"
best_as_clusters_path = os.path.relpath(best_as_clusters_path)

with open(best_as_clusters_path, 'wb') as handle:
    pickle.dump(best_as_clusters, handle)

print "Step 7 DONE, " + str(len(best_as_clusters)) + " elements in the dict."

######################################################################## STEP 8

print "Step 8: write best_cluster_as.pickle..."

best_cluster_as_path = pickle_dir + "best_cluster_as.pickle"
best_cluster_as_path = os.path.relpath(best_cluster_as_path)

with open(best_cluster_as_path, 'wb') as handle:
    pickle.dump(best_cluster_as, handle)

print "Step 8 DONE, " + str(len(best_cluster_as)) + " elements in the dict."
