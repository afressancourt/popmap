import math
from igraph import *


def distance_on_unit_sphere(lat1, long1, lat2, long2):

    # Convert latitude and longitude to
    # spherical coordinates in radians.
    degrees_to_radians = math.pi/180.0

    # phi = 90 - latitude
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians

    # theta = longitude
    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians

    # Compute spherical distance from spherical coordinates.

    # For two locations in spherical coordinates
    # (1, theta, phi) and (1, theta, phi)
    # cosine( arc length ) =
    #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
    # distance = rho * arc length

    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) +
           math.cos(phi1)*math.cos(phi2))
    arc = math.acos(cos)

    # Remember to multiply arc by the radius of the earth
    # in your favorite set of units to get length.
    return arc


def ipToInt(ip):
    o = map(int, ip.split('.'))
    res = (16777216 * o[0]) + (65536 * o[1]) + (256 * o[2]) + o[3]
    return res


def isIpInSubnet(ip, ipNetwork, maskLength):
    # my test ip, in int form
    ipInt = ipToInt(ip)

    maskLengthFromRight = 32 - maskLength

    #convert the ip network into integer form
    ipNetworkInt = ipToInt(ipNetwork)

    #convert that into into binary (string format)
    binString = "{0:b}".format(ipNetworkInt)

    #find out how much of that int I need to cut off
    chopAmount = 0

    for i in range(maskLengthFromRight):
        if i < len(binString):
            chopAmount += int(binString[len(binString)-1-i]) * 2**i

    minVal = ipNetworkInt-chopAmount
    maxVal = minVal + 2 ** maskLengthFromRight - 1

    return minVal <= ipInt and ipInt <= maxVal


def edge_name(first_string, second_string):

    first_int = int(first_string)
    second_int = int(second_string)

    result = str(min(first_int, second_int)) + "-"
    result += str(max(first_int, second_int))
    return result

# Kind of relationships:
# 0: internal AS link
# 1: provider => customer
# 2: peer => peer
# 3: customer => provider
# 5: node => node, edge absent from currated CAIDA dataset


def as_dfs_gao_rexford(graph,
                       start_node,
                       visited_set={}):
    if not start_node in visited_set:
        visited_set[start_node] = 0
    neighbors = graph.neighbors(start_node, mode=OUT)
    for neighbor in neighbors:
        subcondition_1 = visited_set[start_node] == 3
        subcondition_2 = visited_set[start_node] == 0
        condition_1 = subcondition_1 or subcondition_2
        edge = graph.get_eid(start_node, neighbor)
        edge_relationship = graph.es[edge]["relationship"]
        condition_2 = edge_relationship == 1
        if not neighbor in visited_set and (condition_1 or condition_2):
            visited_set[neighbor] = edge_relationship
            as_dfs_gao_rexford(graph, neighbor, visited_set)
    return visited_set


def full_as_dfs_gao_rexford(graph):
    visited_sets = {}
    for vertex in graph.vs:
        index = vertex.index
        visited_sets[index] = as_dfs_gao_rexford(graph,
                                                 index,
                                                 {})
    return visited_sets

# Kind of relationships:
# 0: internal AS link
# 1: provider => customer
# 2: peer => peer
# 3: customer => provider
# 5: node => node, edge absent from currated CAIDA dataset


def pop_dfs_gao_rexford(pop_graph,
                        start_node,
                        as_path_set={},
                        visited_set={}):

    # Put the start_node in the visited set if needed
    if not start_node in visited_set:
        visited_set[start_node] = 3
    asn = pop_graph.vs[start_node]["as"]

    neighbors = pop_graph.neighbors(start_node, mode=OUT)
    for neighbor in neighbors:

        edge = pop_graph.get_eid(start_node, neighbor)
        edge_relationship = pop_graph.es[edge]["relationship"]
        neighbor_asn = pop_graph.vs[neighbor]["as"]

        # Work on transition conditions
        # In AS transition
        inner_1 = not neighbor in visited_set
        inner_2 = edge_relationship == 0
        inner_condition = inner_1 and inner_2

        # Outside AS condition
        outter_1 = not neighbor in visited_set
        outter_2 = asn != neighbor_asn
        outter_3 = not neighbor_asn in as_path_set
        sub_outter_4_1 = edge_relationship == 1
        sub_outter_4_2 = visited_set[start_node] == 3
        outter_4 = sub_outter_4_1 or sub_outter_4_2
        outter_condition = outter_1 and outter_2 and outter_3 and outter_4

        if inner_condition:
            # We have a transition inside the same AS
            visited_set[neighbor] = visited_set[start_node]
            pop_dfs_gao_rexford(pop_graph,
                                neighbor,
                                as_path_set,
                                visited_set)

        if outter_condition:
            # We have a transition between AS
            visited_set[neighbor] = edge_relationship
            as_path_set[asn] = asn
            pop_dfs_gao_rexford(pop_graph,
                                neighbor,
                                as_path_set,
                                visited_set)

    return visited_set


def full_pop_dfs_gao_rexford(graph):
    visited_sets = {}
    for vertex in graph.vs:
        index = vertex.index
        visited_sets[index] = pop_dfs_gao_rexford(graph,
                                                  index,
                                                  {},
                                                  {})
    return visited_sets


def find_all_gaorexford_paths(graph,
                              source,
                              destination,
                              limit,
                              node_path=[],
                              as_predecessor={},
                              origin_as_link={}):
    # Find paths from node index "source" to "destination" in graph "graph"
    if not source in origin_as_link:
        origin_as_link[source] = 3
    asn = graph.vs[source]["as"]
    as_dict = {}
    if asn in as_predecessor:
        as_dict = as_predecessor[asn]
    node_path = node_path + [source]

    if limit > 0 and len(node_path) > limit:
        return []

    if source == destination:
        return [node_path]

    node_paths = []

    for child in graph.successors(source):
        # This is where we should add the conditions
        edge = graph.get_eid(source, child)
        edge_relationship = graph.es[edge]["relationship"]
        child_asn = graph.vs[child]["as"]

        # Work on transition conditions
        # In AS transition
        inner_1 = not child in node_path
        inner_2 = edge_relationship == 0
        inner_condition = inner_1 and inner_2

        # Outside AS condition
        outter_1 = not child in node_path
        outter_2 = asn != child_asn
        outter_3 = not child_asn in as_dict
        sub_outter_4_1 = edge_relationship == 1
        sub_outter_4_2 = origin_as_link[source] == 3
        outter_4 = sub_outter_4_1 or sub_outter_4_2
        outter_condition = outter_1 and outter_2 and outter_3 and outter_4

        if inner_condition:
            origin_as_link[child] = origin_as_link[source]
            child_node_paths = find_all_gaorexford_paths(graph,
                                                         child,
                                                         destination,
                                                         limit,
                                                         node_path,
                                                         as_dict,
                                                         origin_as_link)
            for child_node_path in child_node_paths:
                node_paths.append(child_node_path)

        if outter_condition:
            # We have a transition between AS
            origin_as_link[child] = edge_relationship
            as_predecessor[child_asn] = {}
            for as_name in as_dict:
                as_predecessor[child_asn][as_name] = as_name
            as_predecessor[child_asn][asn] = asn
            child_node_paths = find_all_gaorexford_paths(graph,
                                                         child,
                                                         destination,
                                                         limit,
                                                         node_path,
                                                         as_predecessor,
                                                         origin_as_link)
            for child_node_path in child_node_paths:
                node_paths.append(child_node_path)
    return node_paths


def get_gaorexford_graph(graph, source, destination, limit):
    gaorexford_graph = Graph(directed=True)
    nodes = {}
    edges = {}

    node_paths = find_all_gaorexford_paths(graph,
                                           source,
                                           destination,
                                           limit)

    for node_path in node_paths:
        for node in node_path:
            node = graph.vs[node]
            i_d = node["id"]
            name = node["name"]
            a_s = node["as"]
            node_element = [i_d,
                            name,
                            a_s]
            if not node["name"] in nodes:
                nodes[node["name"]] = node_element

        for i in range(1, len(node_path)):
            source = node_path[i-1]
            source_name = graph.vs[source]["name"]
            target = node_path[i]
            target_name = graph.vs[target]["name"]
            initial_edge = graph.get_eid(source, target)
            initial_edge = graph.es[initial_edge]
            latency_total = initial_edge["latency_total"]
            latency = initial_edge["latency"]
            occurences = initial_edge["occurences"]
            relationship = initial_edge["relationship"]
            edge_name = source_name + "-" + target_name
            if not edge_name in edges:
                edge = [source_name,
                        target_name,
                        latency_total,
                        latency,
                        occurences,
                        relationship]
                edges[edge_name] = edge

    for node in nodes:
        gaorexford_graph.add_vertex(id=nodes[node][0],
                                    name=nodes[node][1]
                                    )
        vertex = gaorexford_graph.vs.find(name=nodes[node][1])
        vertex["as"] = nodes[node][2]

    edgeVector = []
    for edge in edges:
        source = edges[edge][0]
        source = gaorexford_graph.vs.find(name=source).index
        destination = edges[edge][1]
        destination = gaorexford_graph.vs.find(name=destination).index
        edgeVector += [(source, destination)]

    gaorexford_graph.add_edges(edgeVector)

    for edge in gaorexford_graph.es:
        source_name = gaorexford_graph.vs[edge.source]["name"]
        target_name = gaorexford_graph.vs[edge.target]["name"]
        edge_name = source_name + "-" + target_name
        edge["latency_total"] = edges[edge_name][2]
        edge["latency"] = edges[edge_name][3]
        edge["occurences"] = edges[edge_name][4]
        edge["relationship"] = edges[edge_name][5]

    return gaorexford_graph
