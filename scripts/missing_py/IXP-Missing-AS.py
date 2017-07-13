import os
from netaddr import *
from igraph import *
import pickle

# GOAL:
# 1/ Look at PoPs that are in an IXP
# 2/ Build a dictionnary with the ASes that are confirmed in each IXP
# 3/ Build a dictionnary with the ASes that were not confirmed in each IXP

##### Retrieved data #####

# Dictionnary containing the IPs belonging to an IXP
# Key: IP address
# Value: IXP Public id according to PeeringDB
ip_ixp = {}

# Dictionnary containing the PoP associated to an IP
# Key: IP address
# Value: PoP number
ip_pop = {}

# Dictionnary containing the PoP associated to an IP
# Key: PoP number
# Value: AS number
pop_as = {}

# Dictionnary containing the ASes belonging to an IXP
# Key: IXP public id
# Value: Dictionnary containing the AS numbers
ixp_ases = {}

##### New data #####

# Dictionnary containing the PoPs associated to an IXP
# Key: IXP Public id according to PeeringDB
# Value: Dictionnary containing the PoPs
ixp_pops = {}

# Dictionnary containing the ASes associated to an IXP that are present in the
# iPlane dataset
# Key: IXP Public id according to PeeringDB
# Value: Dictionnary containing the ASes (used temporarily, not to be saved)
ixp_confirmed_ases = {}

# Dictionnary containing the ASes associated to an IXP that could not be found
# using the iPlane dataset. We are going to dig in those ASes to find the most
# appropriate PoP candidate.
# Key: IXP Public id according to PeeringDB
# Value: Dictionnary containing the ASes
ixp_missing_ases = {}

pickle_dir = "pickle/confirmed/"
# pickle_dir = "pickle/"

print "\n=== IXP-Missing-AS ===\n"

######################################################################## STEP 1

print "Step 1: load data..."
print "--> Pickle Directory: " + pickle_dir

print "Loading ip_ixp dictionnary..."

ip_ixp_path = os.path.relpath(pickle_dir + "ip_ixp.pickle")

with open(ip_ixp_path, 'rb') as handle:
    ip_ixp = pickle.load(handle)

print "Loading ip_pop dictionnary..."

ip_pop_path = os.path.relpath(pickle_dir + "ip_pop.pickle")

with open(ip_pop_path, 'rb') as handle2:
    ip_pop = pickle.load(handle2)

print "Loading pop_as dictionnary..."

pop_as_path = os.path.relpath(pickle_dir + "pop_as.pickle")

with open(pop_as_path, 'rb') as handle3:
    pop_as = pickle.load(handle3)

print "Loading ixp_ases dictionnary..."

ixp_ases_path = os.path.relpath(pickle_dir + "ixp_ases.pickle")

with open(ixp_ases_path, 'rb') as handle4:
    ixp_ases = pickle.load(handle4)

print str(len(ixp_ases)) + " IXPs in the dict."

print "Step 1 DONE"

######################################################################## STEP 2

print "Step 2: looking into dictionnaries for matching IPs..."

for ip_addr in ip_ixp:

    if ip_addr in ip_pop:
        ixp = ip_ixp[ip_addr]
        pop = ip_pop[ip_addr]
        as_list = []
        if pop in pop_as:
            as_list = pop_as[pop]

        if len(as_list) > 0:

            # Put the pop in the according ixp_pops dictionnary
            if not ixp in ixp_pops:
                ixp_pops[ixp] = {}
            pop_dictionnary = ixp_pops[ixp]

            if not pop in pop_dictionnary:
                pop_dictionnary[pop] = pop

            # Put the AS in the according ixp_ases_temp dictionnary
            if not ixp in ixp_confirmed_ases:
                ixp_confirmed_ases[ixp] = {}

            confirmed_as_dictionnary = ixp_confirmed_ases[ixp]

            for asn in as_list:
                if not asn in confirmed_as_dictionnary:
                    confirmed_as_dictionnary[asn] = {}
                confirmed_as_dictionnary[asn][pop] = pop

                if not ixp in ixp_ases:
                    ixp_ases[ixp] = {}
                as_dictionnary = ixp_ases[ixp]

                if not asn in as_dictionnary:
                    as_dictionnary[asn] = asn

print "Step 2 DONE"

######################################################################## STEP 3

print "Step 3: looking at ASes for which no PoP has been identified..."

for ixp in ixp_ases:

    as_dictionnary = ixp_ases[ixp]

    if not ixp in ixp_missing_ases:
        ixp_missing_ases[ixp] = {}

    missing_as_dictionnary = ixp_missing_ases[ixp]

    if not ixp in ixp_confirmed_ases:
        ixp_confirmed_ases[ixp] = {}

    confirmed_as_dictionnary = ixp_confirmed_ases[ixp]

    for asn in as_dictionnary:
        if not asn in confirmed_as_dictionnary:
            missing_as_dictionnary[asn] = asn

    len_as_dict = len(ixp_ases[ixp])
    len_confirmed_as_dict = len(ixp_confirmed_ases[ixp])
    len_missing_as_dict = len(ixp_missing_ases[ixp])
    if len_as_dict != len_confirmed_as_dict + len_missing_as_dict:
        print "========> PROBLEM with IXP " + ixp

print "Step 3 DONE"

######################################################################## STEP 4

print "Step 4: write ixp_pops dictionnary in ixp_pops_1.pickle..."

ixp_pops_path = pickle_dir + "ixp_pops_1.pickle"
ixp_pops_path = os.path.relpath(ixp_pops_path)

with open(ixp_pops_path, 'wb') as handle5:
    pickle.dump(ixp_pops, handle5)

print "Step 4 DONE, " + str(len(ixp_pops)) + " IXPs in the dictionnary"

######################################################################## STEP 5

print "Step 5: write ixp_missing_ases dict in ixp_missing_ases_1.pickle..."

ixp_missing_ases_path = pickle_dir + "ixp_missing_ases_1.pickle"
ixp_missing_ases_path = os.path.relpath(ixp_missing_ases_path)

with open(ixp_missing_ases_path, 'wb') as handle6:
    pickle.dump(ixp_missing_ases, handle6)

print "Step 5 DONE, " + str(len(ixp_missing_ases)) + " IXPs in the dictionnary"

######################################################################## STEP 6

print "Step 6: write ixp_confirmed_ases dict in ixp_confirmed_ases_1.pickle..."

ixp_confirmed_ases_path = pickle_dir + "ixp_confirmed_ases_1.pickle"
ixp_confirmed_ases_path = os.path.relpath(ixp_confirmed_ases_path)

with open(ixp_confirmed_ases_path, 'wb') as handle7:
    pickle.dump(ixp_confirmed_ases, handle7)

print "Step 6 DONE, " + str(len(ixp_confirmed_ases)) + " IXPs in the dict."

######################################################################## STEP 7

print "Step 7: write ixp_ases dict in ixp_ases_1.pickle..."

ixp_ases_path = pickle_dir + "ixp_ases_1.pickle"
ixp_ases_path = os.path.relpath(ixp_ases_path)

with open(ixp_ases_path, 'wb') as handle8:
    pickle.dump(ixp_ases, handle8)

print "Step 7 DONE, " + str(len(ixp_ases)) + " IXPs in the dict."
