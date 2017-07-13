import os
from netaddr import *

# file_path = "../Data/20150713/test/weekly_origin_as_mapping.txt"
file_path = "../Data/20150713/weekly_origin_as_mapping.txt"
file_path = os.path.relpath(file_path)

manual_policy_path = "../Data/20150713/manual-policy.txt"
manual_policy_path = os.path.relpath(manual_policy_path)

result_path = "../Data/20150713/weekly_origin_as_mapping_clean.txt"
result_path = os.path.relpath(result_path)

manual_policy = {}

with open(manual_policy_path, 'rb') as policy:

    while True:
        line = policy.readline()
        if not line:
            break
        line = line.rstrip('\r\n')
        policy_elements = line.split(' ')
        manual_policy[policy_elements[0]] = policy_elements[1]

with open(file_path, 'rb') as txt, open(result_path, 'wb') as result:
    while True:
        line = txt.readline()
        if not line:
            break
        line = line.rstrip('\r\n')
        ip_as_element = line.split(' ')
        if ip_as_element[1] in manual_policy:
            ip_as_element[1] = manual_policy[ip_as_element[1]]
        if not '_' in ip_as_element[1]:
            if not '.' in ip_as_element[1]:
                int_asn = int(ip_as_element[1])
                if int_asn > 64511 and int_asn < 65535:
                    # print "Single private ASN " + ip_as_element[1]
                    continue
        if '_' in ip_as_element[1]:
            # TODO removal of the private ASNs
            as_path_elements = ip_as_element[1].split('_')
            new_elements = []
            for as_path_element in as_path_elements:
                if not '.' in as_path_element:
                    int_asn = int(as_path_element)
                    if int_asn < 64512 or int_asn > 65534:
                        new_elements = new_elements + [as_path_element]
                else:
                    new_elements = new_elements + [as_path_element]
            if len(new_elements) == 0:
                continue
            ip_as_element[1] = ''
            for new_element in new_elements:
                ip_as_element[1] = ip_as_element[1] + new_element + '_'
            ip_as_element[1] = ip_as_element[1].rstrip('_')

        new_line = ip_as_element[0] + ' ' + ip_as_element[1]
        result.write(new_line + '\n')
