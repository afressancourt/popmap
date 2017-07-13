import os
import pickle

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
# Value: Dictionnary containing the ASes
ixp_confirmed_ases = {}

# Dictionnary containing the PoPs associated to an IXP
# Key: IXP Public id according to PeeringDB
# Value: Dictionnary containing the PoPs
ixp_pops = {}

pickle_dir = "pickle/confirmed/"
# pickle_dir = "pickle/"

min_confirmed_as_participant = 1

print "\n=== PoP-As-Association-Confirmed ===\n"

######################################################################## STEP 1

print "Step 1: load data..."
print "--> Pickle Directory: " + pickle_dir

print "Loading ixp_ases dictionnary..."

ixp_ases_path = pickle_dir + "ixp_ases_3.pickle"
ixp_ases_path = os.path.relpath(ixp_ases_path)

with open(ixp_ases_path, 'rb') as handle:
    ixp_ases = pickle.load(handle)

print "Length of ixp_ases: " + str(len(ixp_ases))

print "Loading ixp_missing_ases dictionnary..."

ixp_missing_ases_path = pickle_dir + "ixp_missing_ases_3.pickle"
ixp_missing_ases_path = os.path.relpath(ixp_missing_ases_path)

with open(ixp_missing_ases_path, 'rb') as handle2:
    ixp_missing_ases = pickle.load(handle2)

print "Length of ixp_missing_ases: " + str(len(ixp_missing_ases))

print "Loading ixp_confirmed_ases dictionnary..."

ixp_confirmed_ases_path = pickle_dir + "ixp_confirmed_ases_3.pickle"
ixp_confirmed_ases_path = os.path.relpath(ixp_confirmed_ases_path)

with open(ixp_confirmed_ases_path, 'rb') as handle3:
    ixp_confirmed_ases = pickle.load(handle3)

print "Length of ixp_confirmed_ases: " + str(len(ixp_confirmed_ases))

print "Loading ixp_pops dictionnary..."

ixp_pops_path = pickle_dir + "ixp_pops_3.pickle"
ixp_pops_path = os.path.relpath(ixp_pops_path)

with open(ixp_pops_path, 'rb') as handle4:
    ixp_pops = pickle.load(handle4)

print "Length of ixp_pops: " + str(len(ixp_pops))

######################################################################## STEP 2

# Here we try to look at the IXPs which will be useful for our architecture.
# We keep IXP that:
# * have more than 1 confirmed partcipant AS
# * have more than 1 PoP
# We count the maximum number of PoPs in an IXP

print "Step 2: determine the number of proper IXP"

eligible_ixps = {}
max_PoP = 0
max_ASN = 0

for ixp in ixp_ases:

    len_as_dict = len(ixp_ases[ixp])
    len_confirmed_as_dict = len(ixp_confirmed_ases[ixp])
    len_missing_as_dict = len(ixp_missing_ases[ixp])
    if not ixp in ixp_pops:
        continue
    len_pop_dict = len(ixp_pops[ixp])

    if len_pop_dict != len_confirmed_as_dict:
        print "Difference between AS and Pop dictionnaries for IXP: " + ixp

    if len_confirmed_as_dict > min_confirmed_as_participant:
        eligible_ixps[ixp] = ixp

        if len_pop_dict > max_PoP:
            max_PoP = len_pop_dict

        if len_as_dict > max_ASN:
            max_ASN = len_as_dict

print "### SUMMARY ###"
print "Number of eligible IXPs: " + str(len(eligible_ixps))
print "Max number of PoPs: " + str(max_PoP)
print "Max number of ASes: " + str(max_ASN)

######################################################################## STEP 3

print "Step 3: write eligible_ixps dict in eligible_ixps.pickle..."

eligible_ixps_path = pickle_dir + "eligible_ixps.pickle"
eligible_ixps_path = os.path.relpath(eligible_ixps_path)

with open(eligible_ixps_path, 'wb') as handle5:
    pickle.dump(eligible_ixps, handle5)

print "Step 3 DONE, " + str(len(eligible_ixps)) + " eligible IXPs in the dict."
