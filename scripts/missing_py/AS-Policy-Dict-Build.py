import os
import pickle

# GOAL:
# Build AS-Policy dictionnaries
# The idea is to determien what is the policy of the AS to then build the
# missing IXP connections according to recent research results.
# To do so, we parse:
# * peerParticipants.csv

# Dictionnary containing the policies associated to an AS
# Key: AS number
# Value: Policy description
as_policy = {}

# Dictionnary containing the ASes using a given policy
# Key: Policy description
# Value: Dictionnary containing the ASes
policy_ases = {}

pickle_dir = "pickle/confirmed/"
# pickle_dir = "pickle/"

print "\n=== AS-Policy-Dict-Build ===\n"

print "--> Pickle Directory: " + pickle_dir

print "Step 1: parsing peerParticipants.csv..."

file_path = os.path.relpath("../Data/20150713/peerParticipants.csv")

with open(file_path, 'rb') as txt:

    while True:

        line = txt.readline()
        if not line:
            break

        policy_element = line.split(";")
        asn = policy_element[1]
        policy = policy_element[6]
        if "\N" in asn or "\N" in policy:
            continue

        as_policy[asn] = policy

        if policy not in policy_ases:
            policy_ases[policy] = {}
        policy_ases[policy][asn] = asn

print "Step 1 DONE"

print "Step 2: write as_policy dictionnary in as_policy.pickle..."

as_policy_path = os.path.relpath(pickle_dir + "as_policy.pickle")

with open(as_policy_path, 'wb') as handle:
    pickle.dump(as_policy, handle)

print "Step 2 DONE, " + str(len(as_policy)) + " ASes in the dictionnary"

print "Step 3: write policy_ases dictionnary in policy_ases.pickle..."

policy_ases_path = os.path.relpath(pickle_dir + "policy_ases.pickle")

with open(policy_ases_path, 'wb') as handle2:
    pickle.dump(policy_ases, handle2)

print "Step 3 DONE, " + str(len(policy_ases)) + " policies in the dictionnary"
