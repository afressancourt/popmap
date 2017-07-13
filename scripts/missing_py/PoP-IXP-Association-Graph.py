import os
from netaddr import *
from igraph import *
import pickle
import Queue

# GOAL:
# For each IXP, we look at AS for which we didn't find a PoP, and try to
# associate the closest PoP to the IXP

##### Retrieved data #####

# Dictionnary containing the ASes belonging to an IXP
# Key: IXP public id
# Value: Dictionnary containing the AS numbers
ixp_ases = {}

# Dictionnary containing the ASes associated to an IXP that could not be found
# using the iPlane dataset. We are going to dig in those ASes to find the most
# appropriate PoP candidate.
# Key: IXP Public id according to PeeringDB
# Value: Dictionnary containing the ASes (used temporarily, not to be saved)
ixp_missing_ases = {}

# Dictionnary containing the ASes associated to an IXP that are present in the
# iPlane dataset
# Key: IXP Public id according to PeeringDB
# Value: Dictionnary containing the ASes (used temporarily, not to be saved)
ixp_confirmed_ases = {}

# Dictionnary containing the PoPs associated to an IXP
# Key: IXP Public id according to PeeringDB
# Value: Dictionnary containing the PoPs
ixp_pops = {}

# Dictionnary containing the PoP associated to an IP
# Key: PoP number
# Value: Dictionnary containing related ASes and a dictionnary of the PoPs
# through which this relationship is observed
pop_relatedas_pops = {}

##### New data #####

pickle_dir = "pickle/confirmed/"
# pickle_dir = "pickle/"

print "\n=== PoP-As-Association-Graph ===\n"

######################################################################## STEP 1

print "Step 1: load data..."
print "--> Pickle Directory: " + pickle_dir

print "Loading ixp_ases dictionnary..."

ixp_ases_path = pickle_dir + "ixp_ases_1.pickle"
ixp_ases_path = os.path.relpath(ixp_ases_path)

with open(ixp_ases_path, 'rb') as handle:
    ixp_ases = pickle.load(handle)

print "Length of ixp_ases: " + str(len(ixp_ases))

print "Loading ixp_missing_ases dictionnary..."

ixp_missing_ases_path = pickle_dir + "ixp_missing_ases_1.pickle"
ixp_missing_ases_path = os.path.relpath(ixp_missing_ases_path)

with open(ixp_missing_ases_path, 'rb') as handle2:
    ixp_missing_ases = pickle.load(handle2)

print "Length of ixp_missing_ases: " + str(len(ixp_missing_ases))

print "Loading ixp_pops dictionnary..."

ixp_pops_path = pickle_dir + "ixp_pops_1.pickle"
ixp_pops_path = os.path.relpath(ixp_pops_path)

with open(ixp_pops_path, 'rb') as handle3:
    ixp_pops = pickle.load(handle3)

print "Length of ixp_pops: " + str(len(ixp_pops))

print "Loading pop_relatedas_pops dictionnary..."

long_path = pickle_dir + "pop_relatedas_pops.pickle"
pop_relatedas_pops_path = os.path.relpath(long_path)

with open(pop_relatedas_pops_path, 'rb') as handle4:
    pop_relatedas_pops = pickle.load(handle4)

print "Length of pop_relatedas_pops: " + str(len(pop_relatedas_pops))

print "Loading ixp_confirmed_ases dictionnary..."

ixp_confirmed_ases_path = pickle_dir + "ixp_confirmed_ases_1.pickle"
ixp_confirmed_ases_path = os.path.relpath(ixp_confirmed_ases_path)

with open(ixp_confirmed_ases_path, 'rb') as handle5:
    ixp_confirmed_ases = pickle.load(handle5)

print "Length of ixp_confirmed_ases: " + str(len(ixp_confirmed_ases))

print "Step 1 DONE"

######################################################################## STEP 2

print "Step 2: looking at associated PoPs..."

for ixp in ixp_pops:

    if not ixp in ixp_missing_ases:
        ixp_missing_ases[ixp] = {}
    if not ixp in ixp_ases:
        ixp_ases[ixp] = {}
    if not ixp in ixp_confirmed_ases:
        ixp_confirmed_ases[ixp] = {}

    condition_1 = len(ixp_missing_ases[ixp]) == 0
    condition_2 = len(ixp_ases[ixp]) == 0

    if condition_1 or condition_2:
        continue

    pop_dictionnary = ixp_pops[ixp]
    missing_as_dictionnary = ixp_missing_ases[ixp]
    confirmed_as_dictionnary = ixp_confirmed_ases[ixp]

    pop_queue = Queue.Queue()

    for pop in pop_dictionnary:
        pop_queue.put(pop)

    while not pop_queue.empty():

        pop = pop_queue.get()

        if not pop in pop_relatedas_pops:
            continue

        relatedas_pops_dictionnary = pop_relatedas_pops[pop]

        for asn in relatedas_pops_dictionnary:

            if not asn in missing_as_dictionnary:
                continue

            related_pop_dictionnary = relatedas_pops_dictionnary[asn]

            if not asn in confirmed_as_dictionnary:
                # We add the AS in the confirmed_as dictionnary
                confirmed_as_dictionnary[asn] = {}
                # And we remove it from missing_as_dictionnary
                missing_as_dictionnary.pop(asn)

            for related_pop in related_pop_dictionnary:
                # We add the PoP to the ixp_pops dictionnary
                pop_dictionnary[related_pop] = related_pop
                # Then we add the PoP to the confirmed_AS dictionnary
                confirmed_as_dictionnary[asn][related_pop] = related_pop
                # And we put the PoP in the queue in case it helps accessing
                # missing ASes
                pop_queue.put(related_pop)

    len_as_dict = len(ixp_ases[ixp])
    len_confirmed_as_dict = len(ixp_confirmed_ases[ixp])
    len_missing_as_dict = len(ixp_missing_ases[ixp])
    if len_as_dict != len_confirmed_as_dict + len_missing_as_dict:
        print "========> PROBLEM with IXP " + ixp

######################################################################## STEP 3

print "Step 3: write ixp_pops dictionnary in ixp_pops_2.pickle..."

ixp_pops_path = pickle_dir + "ixp_pops_2.pickle"
ixp_pops_path = os.path.relpath(ixp_pops_path)

with open(ixp_pops_path, 'wb') as handle6:
    pickle.dump(ixp_pops, handle6)

print "Step 3 DONE, " + str(len(ixp_pops)) + " IXPs in the dictionnary"

######################################################################## STEP 4

print "Step 4: write ixp_missing_ases dict in ixp_missing_ases_2.pickle..."

ixp_missing_ases_path = pickle_dir + "ixp_missing_ases_2.pickle"
ixp_missing_ases_path = os.path.relpath(ixp_missing_ases_path)

with open(ixp_missing_ases_path, 'wb') as handle7:
    pickle.dump(ixp_missing_ases, handle7)

print "Step 4 DONE, " + str(len(ixp_missing_ases)) + " IXPs in the dictionnary"

######################################################################## STEP 5

print "Step 5: write ixp_confirmed_ases dict in ixp_confirmed_ases_2.pickle..."

ixp_confirmed_ases_path = pickle_dir + "ixp_confirmed_ases_2.pickle"
ixp_confirmed_ases_path = os.path.relpath(ixp_confirmed_ases_path)

with open(ixp_confirmed_ases_path, 'wb') as handle8:
    pickle.dump(ixp_confirmed_ases, handle8)

print "Step 5 DONE, " + str(len(ixp_confirmed_ases)) + " IXPs in the dict."

######################################################################## STEP 6

print "Step 6: write ixp_ases dict in ixp_ases_2.pickle..."

ixp_ases_path = pickle_dir + "ixp_ases_2.pickle"
ixp_ases_path = os.path.relpath(ixp_ases_path)

with open(ixp_ases_path, 'wb') as handle9:
    pickle.dump(ixp_ases, handle9)

print "Step 6 DONE, " + str(len(ixp_ases)) + " IXPs in the dict."
