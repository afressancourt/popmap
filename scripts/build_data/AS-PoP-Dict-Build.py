import os
from netaddr import *
from igraph import *
import pickle

# GOAL:
# Build AS-PoP dictionnaries
# From the IP - PoP dictionnary and the origin AS mapping
# The idea is to determine quickly the AS a PoP belongs to
# and which PoPs are associated to a given AS
# To do so, we use :
# * ip_pop dictionnary
# And we parse:
# * ip_to_as_mapping.txt

# Dictionnary containing the PoP associated to an IP
# Key: IP address
# Value: PoP number
ip_pop = {}

# Dictionnary containing the IXPs belonging to an AS
# Key: PoP number
# Value: Dictionnary containing the IP addresses
pop_ips = {}
size_pop_ips = 0

# Dictionnary containing the PoP associated to an IP
# Key: PoP number
# Value: AS number
pop_as = {}

# Dictionnary containing the IXPs belonging to an AS
# Key: AS number
# Value: Dictionnary containing the PoP numbers
as_pops = {}

# Dictionnary containing the IP classes and associated IP ranges with their AS
# Key: IP class
# Value: Dictionnary containing the IP ranges and associated AS
class_ipranges = {}

pickle_dir = "pickle/confirmed/"
# pickle_dir = "pickle/"

print "\n=== AS-PoP-Build ===\n"

print "--> Pickle Directory: " + pickle_dir

print "Step 1: load data..."

print "Loading ip_pop dictionnary..."

ip_pop_path = os.path.relpath(pickle_dir + "ip_pop.pickle")

with open(ip_pop_path, 'rb') as handle:
    ip_pop = pickle.load(handle)

print "Loading pop_ips dictionnary..."

pop_ips_path = os.path.relpath(pickle_dir + "pop_ips.pickle")

with open(pop_ips_path, 'rb') as handle2:
    pop_ips = pickle.load(handle2)

size_pop_ips = len(pop_ips)

print "Number of PoPs: " + str(size_pop_ips)

print "Step 1 DONE"

print "Step 2: parsing origin_as_mapping.txt..."

# file_path = "../Data/20150713/test/weekly_origin_as_mapping_clean.txt"
file_path = "../Data/20150713/weekly_origin_as_mapping_clean.txt"
file_path = os.path.relpath(file_path)

with open(file_path, 'rb') as txt:

    i = 0

    while True:
        line = txt.readline()
        i = i + 1
        if i % 1000 == 0:
            print "--> Line " + str(i)

        if not line:
            break

        ip_as_element = line.split(" ")
        ip_class = ip_as_element[0]
        as_path = ip_as_element[1].rstrip('\r\n')

        ip_element = ip_class.split("/")

        if not ip_element[1] in class_ipranges:
            class_ipranges[ip_element[1]] = {}

        iprange_as_dictionnary = class_ipranges[ip_element[1]]

        if not ip_class in iprange_as_dictionnary:
            as_list = []
            as_path_elements = as_path.split('_')
            for as_path_element in as_path_elements:
                as_list = as_list + [as_path_element]
            iprange_as_dictionnary[ip_class] = as_list

print "Step 2 DONE"

print "Step 3: Going down the class_ipranges dictionnary..."

i = 32

while i > 0 and len(pop_as) < size_pop_ips:

    ip_class = str(i)

    print "Looking at IP class: " + ip_class

    if ip_class in class_ipranges:

        iprange_as_dictionnary = class_ipranges[ip_class]

        for iprange in iprange_as_dictionnary:

            as_list = iprange_as_dictionnary[iprange]

            try:
                for ip_addr in IPNetwork(iprange):

                    ip_addr = str(ip_addr)

                    if ip_addr in ip_pop:
                        pop = ip_pop[ip_addr]

                        if not pop in pop_as:
                            pop_as[pop] = as_list

                        for asn in as_list:
                            if not asn in as_pops:
                                as_pops[asn] = {}

                            pop_dictionnary = as_pops[asn]
                            if not pop in pop_dictionnary:
                                pop_dictionnary[pop] = [pop]

            except AddrFormatError:
                pass

    i = i-1

print "Step 3 DONE"

print "Step 3 Bis: Parsing inter_pop link files to add as-pop relationships"

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

                    as_pop_element = line.split(" ")

                    pop_1 = as_pop_element[0]
                    asn_1 = as_pop_element[1]
                    pop_2 = as_pop_element[2]
                    asn_2 = as_pop_element[3]

                    if asn_1 != "3303":
                        if not pop_1 in pop_as:
                            pop_as[pop_1] = []

                        # We chose to keep the AS value for the PoP even
                        # if we didn't find it while matching IPs
                        if not asn_1 in pop_as[pop_1]:
                            pop_as[pop_1] = pop_as[pop_1] + [asn_1]

                        if not asn_1 in as_pops:
                            as_pops[asn_1] = {}
                        pop_dictionnary = as_pops[asn_1]
                        if not pop_1 in pop_dictionnary:
                            pop_dictionnary[pop_1] = [pop_1]

                    if asn_2 != "3303":
                        if not pop_2 in pop_as:
                            pop_as[pop_2] = []

                        # We chose to keep the AS value for the PoP even
                        # if we didn't find it while matching IPs
                        if not asn_2 in pop_as[pop_2]:
                            pop_as[pop_2] = pop_as[pop_2] + [asn_2]

                        if not asn_2 in as_pops:
                            as_pops[asn_2] = {}
                        pop_dictionnary = as_pops[asn_2]
                        if not pop_2 in pop_dictionnary:
                            pop_dictionnary[pop_2] = [pop_2]

print "Step 4: write pop_as dictionnary in pop_as.pickle..."

pop_as_path = os.path.relpath(pickle_dir + "pop_as.pickle")

with open(pop_as_path, 'wb') as handle3:
    pickle.dump(pop_as, handle3)

print "Step 3 DONE, " + str(len(pop_as)) + " PoPs in the dictionnary"

print "Step 4: write as_pops dictionnary in as_pops.pickle..."

as_pops_path = os.path.relpath(pickle_dir + "as_pops.pickle")

with open(as_pops_path, 'wb') as handle4:
    pickle.dump(as_pops, handle4)

print "Step 4 DONE, " + str(len(as_pops)) + " ASes in the dictionnary"
