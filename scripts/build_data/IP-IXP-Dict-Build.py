import os
from netaddr import *
from igraph import *
import pickle

# GOAL:
# Build IP-IXP dictionnaries
# The idea is to determine quickly which IP is in which IXP
# To do so, we parse two files:
# * mgmtPublicsIPs.csv
# * peerParticipantsPublics.csv

# Dictionnary containing the IPs belonging to an IXP
# Key: IP address
# Value: IXP Public id according to PeeringDB
ip_ixp = {}

# Dictionnary containing the ASes belonging to an IXP
# Key: IXP public id
# Value: Dictionnary containing the IP addresses
ixp_ips = {}

pickle_dir = "pickle/confirmed/"
# pickle_dir = "pickle/"

print "\n=== IP-IXP-Dict-Build ===\n"
print "Looking at IPs that could be in an IXP..."

print "--> Pickle Directory: " + pickle_dir

first_path = os.path.relpath("../Data/20150713/mgmtPublicsIPs.csv")

print "Step 1: Reading from mgmtPublicsIPs.csv..."

with open(first_path, 'rb') as txt:

    while True:
        line = txt.readline()
        if not line:
            break
        ip_ixp_element = line.split(";")
        if ip_ixp_element[2].startswith('IPv4'):

            ip = "/N"

            try:
                for ip in IPNetwork(ip_ixp_element[3]):

                    if not str(ip) in ip_ixp:
                        ip_ixp[str(ip)] = ip_ixp_element[1]

                    if not ip_ixp_element[1] in ixp_ips:
                        ixp_ips[ip_ixp_element[1]] = {}

                    ixp_dictionnary = ixp_ips[ip_ixp_element[1]]

                    if not str(ip) in ixp_dictionnary:
                        ixp_dictionnary[str(ip)] = str(ip)

            except AddrFormatError:
                pass

print "Step 1 DONE, "
print str(len(ip_ixp)) + " IPs in dictionnary"
print str(len(ixp_ips)) + " IXPs in dictionnary"

to_deal_with = {}

print "Step 2: Reading from mgmtPublics.csv..."

mgmtPublics_path = os.path.relpath("../Data/20150713/mgmtPublics.csv")

# Read the file and put the various IP ranges in a temporary dictionnary

iprange_ixp_temp = {}

with open(mgmtPublics_path, 'rb') as txt2:

    while True:
        line = txt2.readline()
        if not line:
            break

        ixp_ip_elements = line.split(";")
        ixp = ixp_ip_elements[0]
        ip_element = ixp_ip_elements[1].rstrip('\r\n')

        if ',' in ip_element:
            ip_element = ip_element.split(",")
            for iprange in ip_element:
                if not iprange in iprange_ixp_temp:
                    iprange_ixp_temp[iprange] = ixp
        else:
            if not ip_element in iprange_ixp_temp:
                iprange_ixp_temp[ip_element] = ixp

# Parse the temporary dictionnary to add all the IPs in the ixp_ips and ip_ixp
# dictionnary

ixp = ""

for iprange in iprange_ixp_temp:
    ixp = iprange_ixp_temp[iprange]
    ip = "NULL"
    try:
        for ip in IPNetwork(iprange):

            if not str(ip) in ip_ixp:
                ip_ixp[str(ip)] = ixp

            if not ixp in ixp_ips:
                ixp_ips[ixp] = {}

            ixp_dictionnary = ixp_ips[ixp]

            if not str(ip) in ixp_dictionnary:
                ixp_dictionnary[str(ip)] = str(ip)

    except AddrFormatError:
        print "ERROR: " + iprange
        pass


print "Step 2 DONE, "
print str(len(ip_ixp)) + " IPs in dictionnary"
print str(len(ixp_ips)) + " IXPs in dictionnary"

print "Step 3: Reading from peerParticipantsPublics.csv..."

second_path = os.path.relpath("../Data/20150713/peerParticipantsPublics.csv")

with open(second_path, 'rb') as txt3:

    while True:
        line = txt3.readline()
        if not line:
            break
        #print line

        pp_element = line.split(";")
        pp_element[4] = pp_element[4].lstrip()
        pp_element[4] = pp_element[4].rstrip('\r\n')

        ## Try to clean the string...
        pp_element[4] = pp_element[4].replace(',', '+')
        pp_element[4] = pp_element[4].replace(' ', '+')

        if '.' in pp_element[4] and '+' in pp_element[4]:
            pp_detailed_elements = pp_element[4].split('+')

            for pp_detailed_element in pp_detailed_elements:

                if '.' in pp_detailed_element:

                    pp_detailed_element = pp_detailed_element.lstrip()
                    pp_detailed_element = pp_detailed_element.rstrip()
                    to_deal_with[pp_detailed_element] = pp_element[2]

        elif '.' in pp_element[4]:
            pp_element[4] = pp_element[4].lstrip()
            pp_element[4] = pp_element[4].rstrip()
            to_deal_with[pp_element[4]] = pp_element[2]

i = 0

for element in to_deal_with:
    #print element
    try:
        for ip in IPNetwork(element):
            #print str(ip)
            if not str(ip) in ip_ixp:
                ip_ixp[str(ip)] = to_deal_with[element]

            if not to_deal_with[element] in ixp_ips:
                ixp_ips[to_deal_with[element]] = {}

            ixp_dictionnary = ixp_ips[to_deal_with[element]]

            if not str(ip) in ixp_dictionnary:
                ixp_dictionnary[str(ip)] = str(ip)

    except AddrFormatError:
        i = i+1
        print "Issue " + str(i) + ": " + element

print str(i) + " issues detected"

print "Step 3 DONE"

print "Step 4: write ip_ixp dictionnary in ip_ixp.pickle..."

result_path = os.path.relpath(pickle_dir + "ip_ixp.pickle")

with open(result_path, 'wb') as handle:
    pickle.dump(ip_ixp, handle)

print "Step 3 DONE, " + str(len(ip_ixp)) + " IP addresses in dictionnary"

print "Step 4: write ixp_ips dictionnary in ixp_ips.pickle..."

ixp_ips_path = os.path.relpath(pickle_dir + "ixp_ips.pickle")

with open(ixp_ips_path, 'wb') as handle2:
    pickle.dump(ixp_ips, handle2)

print "Step 4 DONE, " + str(len(ixp_ips)) + " IXPs in dictionnary"
