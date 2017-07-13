import os
from netaddr import *
from igraph import *
import pickle

# GOAL:
# Build IP-PoP dictionnaries
# The idea is to determine quickly which PoP has which IP
# and which IPs are associated to a given PoP
# To do so, we parse :
# * ip_to_pop_mapping.txt

# Dictionnary containing the PoP associated to an IP
# Key: IP address
# Value: PoP number
ip_pop = {}

# Dictionnary containing the IXPs belonging to an AS
# Key: PoP number
# Value: Dictionnary containing the IP addresses
pop_ips = {}

pickle_dir = "pickle/confirmed/"
# pickle_dir = "pickle/"

print "\n=== IP-PoP-Dict-Build ===\n"
print "Looking at PoP - IP association..."

print "--> Pickle Directory: " + pickle_dir

print "Step 1: parsing ip_to_pop_mapping.txt..."

file_path = os.path.relpath("../Data/20150713/ip_to_pop_mapping.txt")

with open(file_path, 'rb') as txt:

    while True:
        line = txt.readline()
        if not line:
            break
        #print line

        ip_pop_element = line.split(" ")

        ip_pop_element[1] = ip_pop_element[1].lstrip()
        ip_pop_element[1] = ip_pop_element[1].rstrip('\r\n')

        #print "IP: " + ip_pop_element[0] + " And PoP: " + ip_pop_element[1]

        if not ip_pop_element[0] in ip_pop:
            ip_pop[ip_pop_element[0]] = ip_pop_element[1]

        if not ip_pop_element[1] in pop_ips:
            pop_ips[ip_pop_element[1]] = {}

        pop_dictionnary = pop_ips[ip_pop_element[1]]

        if not ip_pop_element[0] in pop_dictionnary:
            pop_dictionnary[ip_pop_element[0]] = [ip_pop_element[0]]

print "Step 1 DONE"

print "Step 2: write ip_pop dictionnary in ip_pop.pickle..."

ip_pop_path = os.path.relpath(pickle_dir + "ip_pop.pickle")

with open(ip_pop_path, 'wb') as handle:
    pickle.dump(ip_pop, handle)

print "Step 2 DONE, " + str(len(ip_pop)) + " IPs in the dictionnary"

print "Step 3: write pop_ips dictionnary in pop_ips.pickle..."

pop_ips_path = os.path.relpath(pickle_dir + "pop_ips.pickle")

with open(pop_ips_path, 'wb') as handle2:
    pickle.dump(pop_ips, handle2)

print "Step 3 DONE, " + str(len(pop_ips)) + " PoPs in the dictionnary"
