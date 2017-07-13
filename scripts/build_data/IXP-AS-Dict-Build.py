import os
from netaddr import *
from igraph import *
import pickle

# GOAL:
# Build IXP-ASes dictionnaries
# The idea is to determine quickly which AS is in which IXP
# and which IXP an AS is in
# To do so, we parse :
# * peerParticipantsPublics.csv

# Dictionnary containing the ASes belonging to an IXP
# Key: IXP public id
# Value: Dictionnary containing the AS numbers
ixp_ases = {}

# Dictionnary containing the IXPs belonging to an AS
# Key: AS number
# Value: Dictionnary containing the IXP public ids
as_ixps = {}

pickle_dir = "pickle/confirmed/"
# pickle_dir = "pickle/"

print "\n=== IXP-AS-Dict-Build ===\n"
print "Looking at AS membership to IXPs..."

print "--> Pickle Directory: " + pickle_dir

print "Step 1: parsing peerParticipantsPublics.csv..."

file_path = os.path.relpath("../Data/20150713/peerParticipantsPublics.csv")

with open(file_path, 'rb') as txt:

    while True:
        line = txt.readline()
        if not line:
            break
        #print line

        pp_element = line.split(";")

        # Adding the AS to appropriate IXP dictionnary
        if not pp_element[2] in ixp_ases:
            ixp_ases[pp_element[2]] = {}

        as_dictionnary = ixp_ases[pp_element[2]]

        if not pp_element[3] in as_dictionnary:
            as_dictionnary[pp_element[3]] = pp_element[3]

        # Adding the IXP to appropriate AS dictionnary
        if not pp_element[3] in as_ixps:
            as_ixps[pp_element[3]] = {}

        ixp_dictionnary = as_ixps[pp_element[3]]

        if not pp_element[2] in ixp_dictionnary:
            ixp_dictionnary[pp_element[2]] = pp_element[2]

print "Step 1 DONE"

print "Step 2: write ixp_ases dictionnary in ixp_ases.pickle..."

#print ixp_ases

ixp_ases_path = os.path.relpath(pickle_dir + "ixp_ases.pickle")

with open(ixp_ases_path, 'wb') as handle:
    pickle.dump(ixp_ases, handle)

print "Step 2 DONE, " + str(len(ixp_ases)) + " IXPs in the dictionnary"

print "Step 3: write as_ixps dictionnary in as_ixps.pickle..."

#print as_ixps

as_ixps_path = os.path.relpath(pickle_dir + "as_ixps.pickle")

with open(as_ixps_path, 'wb') as handle2:
    pickle.dump(as_ixps, handle2)

print "Step 3 DONE, " + str(len(as_ixps)) + " ASes in the dictionnary"
