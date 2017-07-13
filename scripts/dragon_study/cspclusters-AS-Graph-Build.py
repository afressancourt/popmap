import os
import pickle

# dir_path = '../Data/20150713/inter_pop_links-test/'
dir_path = '../Data/20150713/inter_pop_links/'

csp_path = '../Data/CSP_AS-complementary.txt'

# pickle_dir = "pickle/"
pickle_dir = "pickle/confirmed/"

dragon_edges = {}

##### New data #####

csp_cluster_relatednodes = {}

csp_cluster_edges = {}

print "\n=== cspclusters-AS-Graph-Build ===\n"

######################################################################## STEP 1

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

print "Loading dragon_edges dictionnary..."

dragon_edges_path = pickle_dir + "dragon_edges.pickle"
dragon_edges_path = os.path.relpath(dragon_edges_path)

with open(dragon_edges_path, 'rb') as handle:
    dragon_edges = pickle.load(handle)

print "Length of dragon_edges: " + str(len(dragon_edges))

######################################################################## STEP 2

print "Step 2: Gathering information about CSP ASes"

csp_path = os.path.relpath(csp_path)

provider_asns = {}
asn_provider = {}

with open(csp_path, 'rb') as txt:
    while True:
        line = txt.readline()
        if not line:
            break
        line = line.rstrip('\r\n')
        line_elements = line.split(';')
        asn = line_elements[0]
        provider = line_elements[1]

        if provider not in provider_asns:
            provider_asns[provider] = {}
        provider_asns[provider][asn] = asn
        asn_provider[asn] = provider

        if asn not in interesting_ases:
            interesting_ases[asn] = asn

print "Step 2 DONE"

######################################################################## STEP 3

print "Step 3: Building the cspclusters-AS-Graph per provider..."


def analyzeLine(line):

    link_elements = line.split(" ")
    pop_1 = link_elements[0]
    asn_1 = link_elements[1]
    pop_2 = link_elements[2]
    asn_2 = link_elements[3]
    latency = int(link_elements[4])

    # Dealing with pop-AS association innacuracies
    precondition_1 = not pop_1 in pop_as
    precondition_2 = not pop_2 in pop_as

    if precondition_1 or precondition_2:
        return

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

        condition_1 = not asn_1 in interesting_ases
        condition_2 = not asn_2 in interesting_ases

        if condition_1 or condition_2:
            continue

        nodelist_1 = []
        if asn_1 in asn_dict:
            for cluster in best_pop_clusters[pop_1]:
                if cluster in best_as_clusters[asn_1]:
                    nodelist_1 = nodelist_1 + [cluster]
        else:
            nodelist_1 = [asn_1]

        nodelist_2 = []
        if asn_2 in asn_dict:
            for cluster in best_pop_clusters[pop_2]:
                if cluster in best_as_clusters[asn_2]:
                    nodelist_2 = nodelist_2 + [cluster]
        else:
            nodelist_2 = [asn_2]

        nodepairs = [(n1, n2) for n1 in nodelist_1 for n2 in nodelist_2]

        for nodepair in nodepairs:
            node_1 = nodepair[0]
            node_2 = nodepair[1]

            if not node_1 in node_relatednodes:
                node_relatednodes[node_1] = {}
            node_relatednodes[node_1][node_2] = node_2

            if not node_2 in node_relatednodes:
                node_relatednodes[node_2] = {}
            node_relatednodes[node_2][node_1] = node_1

            # add the two directed edge in edges dictionnary if
            # necessary

            # The first one...
            first_edge_name = node_1 + "-" + node_2
            if not first_edge_name in provider_edges:
                first_edge = [node_1,
                              node_2,
                              0,
                              0,
                              0]
                provider_edges[first_edge_name] = first_edge
            first_edge = provider_edges[first_edge_name]
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
            second_edge_name = node_2 + "-" + node_1
            if not second_edge_name in provider_edges:
                second_edge = [node_2,
                               node_1,
                               0,
                               0,
                               0]
                provider_edges[second_edge_name] = second_edge
            second_edge = provider_edges[second_edge_name]
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
    return


for provider in provider_asns:
    print provider
    node_relatednodes = {}
    provider_edges = {}
    asn_dict = provider_asns[provider]
    for dirname, dirnames, filenames in os.walk(dir_path):
        for filename in filenames:
            if not filename.startswith('.'):

                print "File: " + filename

                with open(os.path.join(dirname, filename), 'rb') as txt:
                    while True:
                        line = txt.readline()
                        line = line.rstrip('\r\n')
                        if not line:
                            break
                        analyzeLine(line)

    print "write node_relatednodes dict in csp_node_relatednodes.pickle..."

    node_relatednodes_path = pickle_dir + provider + "_node_relatednodes.pickle"
    node_relatednodes_path = os.path.relpath(node_relatednodes_path)

    with open(node_relatednodes_path, 'wb') as handle:
        pickle.dump(node_relatednodes, handle)

    print "DONE, " + str(len(node_relatednodes)) + " elements in dict"

    print "write provider_edges dictionnary in csp_provider_edges.pickle..."

    provider_edges_path = pickle_dir + provider + "_cluster_edges.pickle"
    provider_edges_path = os.path.relpath(provider_edges_path)

    with open(provider_edges_path, 'wb') as handle:
        pickle.dump(provider_edges, handle)

    print "DONE, " + str(len(provider_edges)) + " elements in dictionnary"

######################################################################## STEP 4

print "Step 4: write provider_asns dictionnary in provider_asns.pickle..."

provider_asns_path = os.path.relpath(pickle_dir + "provider_asns.pickle")

with open(provider_asns_path, 'wb') as handle:
    pickle.dump(provider_asns, handle)

print "Step 4 DONE, " + str(len(provider_asns)) + " elements in dictionnary"

######################################################################## STEP 5

print "Step 5: write asn_provider dictionnary in asn_provider.pickle..."

asn_provider_path = os.path.relpath(pickle_dir + "asn_provider.pickle")

with open(asn_provider_path, 'wb') as handle:
    pickle.dump(asn_provider, handle)

print "Step 5 DONE, " + str(len(asn_provider)) + " elements in dictionnary"
