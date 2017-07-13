import os
import pickle

pickle_dir = "../pickle/confirmed/"
# pickle_dir = "pickle/"

for i in range(1, 4):

    print "Step ", i

    ixp_ases_path = pickle_dir + "ixp_ases_" + str(i) + ".pickle"
    ixp_ases_path = os.path.relpath(ixp_ases_path)

    with open(ixp_ases_path, 'rb') as handle:
        ixp_ases = pickle.load(handle)

    ixp_missing_ases_path = pickle_dir + "ixp_missing_ases_" + str(i) + ".pickle"
    ixp_missing_ases_path = os.path.relpath(ixp_missing_ases_path)

    with open(ixp_missing_ases_path, 'rb') as handle2:
        ixp_missing_ases = pickle.load(handle2)

    ixp_confirmed_ases_path = pickle_dir + "ixp_confirmed_ases_" + str(i) + ".pickle"
    ixp_confirmed_ases_path = os.path.relpath(ixp_confirmed_ases_path)

    with open(ixp_confirmed_ases_path, 'rb') as handle5:
        ixp_confirmed_ases = pickle.load(handle5)

    total = 0
    for element in ixp_ases:
        # print ixp_ases[element]
        total += len(ixp_ases[element])

    print "Total number of AS at IXPs (PeeringDB): ", total

    confirmed = 0
    for element in ixp_confirmed_ases:
        # print ixp_ases[element]
        confirmed += len(ixp_confirmed_ases[element])

    print "Total number of confirmed AS at IXPs (PeeringDB): ", confirmed

    missing = 0
    for element in ixp_missing_ases:
        # print ixp_ases[element]
        missing += len(ixp_missing_ases[element])

    print "Total number of missing AS at IXPs (PeeringDB): ", missing
    print "Sum: ", missing + confirmed

    print "Completion percentage: ", float(confirmed) * 100 / total
