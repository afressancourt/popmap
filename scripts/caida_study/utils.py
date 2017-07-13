import math
from igraph import *
import Queue


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


def find_all_gaorexford_iter(graph,
                             source,
                             destination,
                             limit=0):
    # Find paths from node index "source" to "destination" in graph "graph"
    node_paths = []

    node_path = [source]
    incoming = 3
    as_path = []

    node_vector = [source,
                   node_path,
                   incoming,
                   as_path]

    node_queue = Queue.Queue()
    node_queue.put(node_vector)

    gsuccessors = graph.successors
    nqget = node_queue.get
    nqempty = node_queue.empty
    nqput = node_queue.put
    gget_eid = graph.get_eid
    ges = graph.es
    gvs = graph.vs

    while not nqempty():

        node_vector = nqget()
        node = node_vector[0]
        node_path = node_vector[1]

        if node == destination:
            node_paths = node_paths + [node_path]
            continue

        if limit > 1 and len(node_path) > (limit - 1):
            continue

        incoming = node_vector[2]
        as_path = node_vector[3]
        node_asn = gvs[node]["as"]

        for child in gsuccessors(node):
            edge = gget_eid(node, child)
            edge_relationship = ges[edge]["relationship"]

            if child in node_path:
                continue

            if edge_relationship == 0:
                child_vector = [child,
                                node_path + [child],
                                incoming,
                                as_path]
                nqput(child_vector)
            # Outside AS condition
            elif gvs[child]["as"] in as_path:
                continue
            elif (edge_relationship == 1) or (incoming == 3):
                # We have a transition between AS
                child_vector = [child,
                                node_path + [child],
                                edge_relationship,
                                as_path + [node_asn]]
                nqput(child_vector)

    return node_paths


def find_all_gaorexford_caida_iter(graph,
                                   source,
                                   destination,
                                   limit=0):
    # Find paths from node index "source" to "destination" in graph "graph"
    node_paths = []

    node_path = [source]
    incoming = 3
    as_path = []

    node_vector = [source,
                   node_path,
                   incoming,
                   as_path]

    node_queue = Queue.Queue()
    node_queue.put(node_vector)

    gsuccessors = graph.successors
    nqget = node_queue.get
    nqempty = node_queue.empty
    nqput = node_queue.put
    gget_eid = graph.get_eid
    ges = graph.es
    gvs = graph.vs

    while not nqempty():

        node_vector = nqget()
        node = node_vector[0]
        node_path = node_vector[1]

        if node == destination:
            node_paths = node_paths + [node_path]
            continue

        if limit > 1 and len(node_path) > (limit - 1):
            continue

        incoming = node_vector[2]
        as_path = node_vector[3]
        node_asn = gvs[node]["as"]

        for child in gsuccessors(node):
            edge = gget_eid(node, child)
            edge_relationship = ges[edge]["relationship"]

            # Change to exclude non-CAIDA paths
            if edge_relationship > 3:
                continue

            if child in node_path:
                continue

            if edge_relationship == 0:
                child_vector = [child,
                                node_path + [child],
                                incoming,
                                as_path]
                nqput(child_vector)
            # Outside AS condition
            elif gvs[child]["as"] in as_path:
                continue
            elif (edge_relationship == 1) or (incoming == 3):
                # We have a transition between AS
                child_vector = [child,
                                node_path + [child],
                                edge_relationship,
                                as_path + [node_asn]]
                nqput(child_vector)

    return node_paths


def gaorexford_reachability(graph,
                            source):

    reach = {}
    incoming = 3
    reach[source] = incoming
    as_path = []

    node_vector = [source,
                   incoming,
                   as_path]

    node_queue = Queue.Queue()
    node_queue.put(node_vector)

    gsuccessors = graph.successors
    nqget = node_queue.get
    nqempty = node_queue.empty
    nqput = node_queue.put
    gget_eid = graph.get_eid
    ges = graph.es
    gvs = graph.vs

    while not nqempty():

        node_vector = nqget()
        node = node_vector[0]
        incoming = node_vector[1]
        as_path = node_vector[2]
        node_asn = gvs[node]["as"]

        for child in gsuccessors(node):
            edge = gget_eid(node, child)
            edge_relationship = ges[edge]["relationship"]

            if edge_relationship == 0:
                if child in reach:
                    last_incoming = reach[child]
                    if incoming > last_incoming:
                        child_vector = [child,
                                        incoming,
                                        as_path]
                        reach[child] = incoming
                        nqput(child_vector)
                else:
                    child_vector = [child,
                                    incoming,
                                    as_path]
                    reach[child] = incoming
                    nqput(child_vector)

            elif edge_relationship < 4:
                if child in reach:
                    last_incoming = reach[child]
                    child_asn = gvs[child]["as"]

                    cond_1 = edge_relationship > last_incoming
                    cond_2 = child_asn not in as_path
                    if cond_1 and cond_2:
                        child_as_path = as_path + [node_asn]
                        child_vector = [child,
                                        edge_relationship,
                                        child_as_path]
                        reach[child] = edge_relationship
                        nqput(child_vector)

                elif (edge_relationship == 1) or (incoming == 3):
                    child_as_path = as_path + [node_asn]
                    child_vector = [child,
                                    edge_relationship,
                                    child_as_path]
                    reach[child] = edge_relationship
                    nqput(child_vector)
    return reach
