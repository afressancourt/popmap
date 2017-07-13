import os
from netaddr import *
from igraph import *
import pickle
import geoip2.database
import utils

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

# Dictionnary containing the PoPs belonging to an AS
# Key: AS number
# Value: Dictionnary containing the PoP numbers
as_pops = {}

pop_as = {}

# Dictionnary containing the IXPs belonging to an AS
# Key: PoP number
# Value: Dictionnary containing the IP addresses
pop_ips = {}

# Dictionnary containing the IPs belonging to an IXP
# Key: IXP public id
# Value: Dictionnary containing the IP addresses
ixp_ips = {}

##### New data #####

pickle_dir = "pickle/confirmed/"
# pickle_dir = "pickle/"

max_number_pop_ixp_as = 10

max_distance_ixp = 100

print "\n=== PoP-As-Association-Geo ===\n"

######################################################################## STEP 1

print "Step 1: load data..."
print "--> Pickle Directory: " + pickle_dir

print "Loading ixp_ases dictionnary..."

ixp_ases_path = pickle_dir + "ixp_ases_2.pickle"
ixp_ases_path = os.path.relpath(ixp_ases_path)

with open(ixp_ases_path, 'rb') as handle:
    ixp_ases = pickle.load(handle)

print "Length of ixp_ases: " + str(len(ixp_ases))

print "Loading ixp_missing_ases dictionnary..."

ixp_missing_ases_path = pickle_dir + "ixp_missing_ases_2.pickle"
ixp_missing_ases_path = os.path.relpath(ixp_missing_ases_path)

with open(ixp_missing_ases_path, 'rb') as handle2:
    ixp_missing_ases = pickle.load(handle2)

print "Length of ixp_missing_ases: " + str(len(ixp_missing_ases))

print "Loading ixp_pops dictionnary..."

ixp_pops_path = pickle_dir + "ixp_pops_2.pickle"
ixp_pops_path = os.path.relpath(ixp_pops_path)

with open(ixp_pops_path, 'rb') as handle3:
    ixp_pops = pickle.load(handle3)

print "Length of ixp_pops: " + str(len(ixp_pops))

print "Loading ixp_confirmed_ases dictionnary..."

ixp_confirmed_ases_path = pickle_dir + "ixp_confirmed_ases_2.pickle"
ixp_confirmed_ases_path = os.path.relpath(ixp_confirmed_ases_path)

with open(ixp_confirmed_ases_path, 'rb') as handle4:
    ixp_confirmed_ases = pickle.load(handle4)

print "Length of ixp_confirmed_ases: " + str(len(ixp_confirmed_ases))

print "Loading as_pops dictionnary..."

as_pops_path = os.path.relpath(pickle_dir + "as_pops.pickle")

with open(as_pops_path, 'rb') as handle5:
    as_pops = pickle.load(handle5)

print "Length of as_pops: " + str(len(as_pops))

print "Loading pop_as dictionnary..."

pop_as_path = os.path.relpath(pickle_dir + "pop_as.pickle")

with open(pop_as_path, 'rb') as handle55:
    pop_as = pickle.load(handle55)

print "Length of pop_as: " + str(len(pop_as))

print "Loading pop_ips dictionnary..."

pop_ips_path = os.path.relpath(pickle_dir + "pop_ips.pickle")

with open(pop_ips_path, 'rb') as handle6:
    pop_ips = pickle.load(handle6)

print "Length of pop_ips: " + str(len(pop_ips))

print "Loading ixp_ips dictionnary..."

ixp_ips_path = os.path.relpath(pickle_dir + "ixp_ips.pickle")

with open(ixp_ips_path, 'rb') as handle7:
    ixp_ips = pickle.load(handle7)

print "Length of ixp_ips: " + str(len(ixp_ips))

print "Step 1 DONE"

######################################################################## STEP 2

print "Step 2: creating the GeoIP database reader object..."

# This creates a Reader object. You should use the same object
# across multiple requests as creation of it is expensive.

geodb_path = os.path.relpath('../Data/20150713/GeoLite2-City.mmdb')
reader = geoip2.database.Reader(geodb_path)

print "Step 2 DONE"

######################################################################## STEP 3

print "Step 3: See whether there are multiple locations for each IXP"

i = 0

for ixp in ixp_ases:

    i = i + 1

    print "\n## IXP number " + str(i) + ": " + ixp + " ##"

    len_as_dict = len(ixp_ases[ixp])
    len_confirmed_as_dict = len(ixp_confirmed_ases[ixp])
    len_missing_as_dict = len(ixp_missing_ases[ixp])
    if len_as_dict != len_confirmed_as_dict + len_missing_as_dict:
        print "========> BEFORE PROBLEM with IXP " + ixp

    # First, we retrieve the various IXP locations in order to compute
    # the distance to the various PoPs

    if not ixp in ixp_ips:
        continue
    ixp_ips_dictionnary = ixp_ips[ixp]

    if not ixp in ixp_pops:
        ixp_pops[ixp] = {}
    pop_dictionnary = ixp_pops[ixp]

    ixp_lat_lon_dict = {}

    for ip in ixp_ips_dictionnary:
        try:
            response = reader.city(ip)
            geoip_lat = response.location.latitude

            geoip_lon = response.location.longitude

            lat_lon = str(geoip_lat) + ";" + str(geoip_lon)

            if not lat_lon in ixp_lat_lon_dict:
                ixp_lat_lon_dict[lat_lon] = [geoip_lat, geoip_lon]

        except geoip2.errors.AddressNotFoundError:
            # print "Address not found error for IXP"
            pass

    # print "Number of locations: " + str(len(ixp_lat_lon_dict))
    # print "IP: " + ixp_ips_dictionnary.keys()[0]

    # Then, we need to look at the missing ASes
    missing_as_dictionnary = ixp_missing_ases[ixp]
    confirmed_as_dictionnary = ixp_confirmed_ases[ixp]
    dict_ases = ixp_ases[ixp]

    if len(missing_as_dictionnary) == 0:
        # print "===> No missing AS for this IXP"
        continue

    missing_ases_to_remove = {}

    for asn in missing_as_dictionnary:

        # print "### ASN " + asn + " ###"

        min_distance = 41000
        elected_pop = {}

        # For each AS, we retrieve their PoPs,
        if not asn in as_pops:
            # print "===> No Pop for ASN: " + asn
            continue

        pop_dictionnary = as_pops[asn]

        for pop in pop_dictionnary:

            # print "#### PoP: " + pop + " ####"

            # Look at each of their IP address,
            if not pop in pop_ips:
                # print "Pop not in pop_ips"
                continue
            ip_dictionnary = pop_ips[pop]

            for pop_ip in ip_dictionnary:
                # Compute the distance from the locations,
                try:
                    response = reader.city(pop_ip)
                except geoip2.errors.AddressNotFoundError:
                    continue
                pop_lat = response.location.latitude
                pop_lon = response.location.longitude

                if (pop_lat is None) or (pop_lon is None):
                    continue

                for location in ixp_lat_lon_dict:
                    ref_lat = ixp_lat_lon_dict[location][0]
                    #print "ref_lat: " + str(ref_lat)
                    ref_lon = ixp_lat_lon_dict[location][1]
                    #print "ref_lon: " + str(ref_lon)

                    if (ref_lat is None) or (ref_lon is None):
                        # print "None lat and lon found for reference Pop"
                        continue

                    cond_1 = pop_lat == ref_lat
                    cond_2 = pop_lon == ref_lon

                    if cond_1 and cond_2:
                        distance = 0
                    else:
                        distance = utils.distance_on_unit_sphere(pop_lat,
                                                                 pop_lon,
                                                                 ref_lat,
                                                                 ref_lon)

                    distance = 6371 * distance
                    if distance == min_distance:
                        elected_pops[pop] = pop
                    if distance < min_distance:
                        min_distance = distance
                        elected_pops = {}
                        elected_pops[pop] = pop

        # If there are less than max_number_pop_ixp_as candidates and the
        # distance is lower than max_distance_ixp, then we add the elected
        # pops in the pop dictionnary and in the confirmed AS one.

        cond_1 = len(elected_pops) < max_number_pop_ixp_as
        cond_2 = min_distance < max_distance_ixp

        if cond_1 and cond_2:

            print "Candidates for addition for AS " + asn + " in IXP " + ixp

            for elected_pop in elected_pops:
                for asn in pop_as[elected_pop]:
                    # We put the ASN in the confirmed AS dictionnary
                    cond_as_1 = not asn in dict_ases
                    if cond_as_1:
                        continue
                    cond_as_2 = not asn in confirmed_as_dictionnary
                    if cond_as_2:
                        confirmed_as_dictionnary[asn] = {}
                    if asn in missing_as_dictionnary:
                        missing_ases_to_remove[asn] = asn
                    # Keep the minimal distance and associated PoP
                    pop_dictionnary[elected_pop] = elected_pop

                    # And we add the PoP in according dictionnary
                    confirmed_as_dictionnary[asn][elected_pop] = elected_pop

    # We then remove all the ASN in the temp dictionnary from the missing AS
    # dictionnary

    for asn in missing_ases_to_remove:
        missing_as_dictionnary.pop(asn)

    len_as_dict = len(ixp_ases[ixp])
    len_confirmed_as_dict = len(ixp_confirmed_ases[ixp])
    len_missing_as_dict = len(ixp_missing_ases[ixp])
    if len_as_dict != len_confirmed_as_dict + len_missing_as_dict:
        print "========> AFTER PROBLEM with IXP " + ixp

######################################################################## STEP 4

print "Step 4: write ixp_pops dictionnary in ixp_pops_3.pickle..."

ixp_pops_path = pickle_dir + "ixp_pops_3.pickle"
ixp_pops_path = os.path.relpath(ixp_pops_path)

with open(ixp_pops_path, 'wb') as handle8:
    pickle.dump(ixp_pops, handle8)

print "Step 4 DONE, " + str(len(ixp_pops)) + " IXPs in the dictionnary"

######################################################################## STEP 5

print "Step 5: write ixp_missing_ases dict in ixp_missing_ases_3.pickle..."

ixp_missing_ases_path = pickle_dir + "ixp_missing_ases_3.pickle"
ixp_missing_ases_path = os.path.relpath(ixp_missing_ases_path)

with open(ixp_missing_ases_path, 'wb') as handle9:
    pickle.dump(ixp_missing_ases, handle9)

print "Step 5 DONE, " + str(len(ixp_missing_ases)) + " IXPs in the dictionnary"

######################################################################## STEP 6

print "Step 6: write ixp_confirmed_ases dict in ixp_confirmed_ases_3.pickle..."

ixp_confirmed_ases_path = pickle_dir + "ixp_confirmed_ases_3.pickle"
ixp_confirmed_ases_path = os.path.relpath(ixp_confirmed_ases_path)

with open(ixp_confirmed_ases_path, 'wb') as handle10:
    pickle.dump(ixp_confirmed_ases, handle10)

print "Step 6 DONE, " + str(len(ixp_confirmed_ases)) + " IXPs in the dict."

######################################################################## STEP 7

print "Step 7: write ixp_ases dict in ixp_ases_3.pickle..."

ixp_ases_path = pickle_dir + "ixp_ases_3.pickle"
ixp_ases_path = os.path.relpath(ixp_ases_path)

with open(ixp_ases_path, 'wb') as handle11:
    pickle.dump(ixp_ases, handle11)

print "Step 7 DONE, " + str(len(ixp_ases)) + " IXPs in the dict."
