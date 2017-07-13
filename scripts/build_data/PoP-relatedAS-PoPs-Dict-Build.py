import os
from netaddr import *
from igraph import *
import pickle

# GOAL:
# Build a PoP - Related AS - Relationship PoPs dictionnary
# To do so, we parse :
# * inter_pop_links.txt

# Dictionnary containing the PoP associated to an IP
# Key: PoP number
# Value: Dictionnary containing related ASes and a dictionnary of the PoPs
# through which this relationship is observed
pop_relatedas_pops = {}

pickle_dir = "pickle/confirmed/"
# pickle_dir = "pickle/"

print "\n=== PoP-relatedAS-PoPs-Dict-Build ===\n"
print "Looking at PoP - AS association..."

print "Loading pop_as dictionnary..."

pop_as_path = os.path.relpath(pickle_dir + "pop_as.pickle")

with open(pop_as_path, 'rb') as handle:
    pop_as = pickle.load(handle)

print "Length of pop_as: " + str(len(pop_as))

print "--> Pickle Directory: " + pickle_dir

print "Step 1: parsing inter_pop_links.txt..."

dir_path = '../Data/20150713/inter_pop_links/'

for dirname, dirnames, filenames in os.walk(dir_path):

    for filename in filenames:
        if not filename.startswith('.'):

            print "File: " + filename

            with open(os.path.join(dirname, filename), 'rb') as txt:
                while True:
                    line = txt.readline()
                    if not line:
                        break
                    #print line

                    as_pop_element = line.split(" ")

                    # First, we look at the relationship for the first PoP
                    pop = as_pop_element[0]
                    asn_related = as_pop_element[3]
                    related_pop = as_pop_element[2]

                    if (not related_pop in pop_as) and (asn_related == "3303"):
                        continue

                    related_as_list = []
                    if related_pop in pop_as:
                        related_as_list = pop_as[related_pop]

                    if not pop in pop_relatedas_pops:
                        pop_relatedas_pops[pop] = {}

                    relatedas_pops_dict = pop_relatedas_pops[pop]

                    for rel_as in related_as_list:
                        if not rel_as in relatedas_pops_dict:
                            relatedas_pops_dict[rel_as] = {}

                        related_pop_dictionnary = relatedas_pops_dict[rel_as]

                        if not related_pop in related_pop_dictionnary:
                            related_pop_dictionnary[related_pop] = related_pop

                    # Working with the second part of the line...
                    pop = as_pop_element[2]
                    asn_related = as_pop_element[1]
                    related_pop = as_pop_element[0]

                    if (not related_pop in pop_as) and (asn_related == "3303"):
                        continue

                    related_as_list = []
                    if related_pop in pop_as:
                        related_as_list = pop_as[related_pop]

                    if not pop in pop_relatedas_pops:
                        pop_relatedas_pops[pop] = {}

                    relatedas_pops_dict = pop_relatedas_pops[pop]

                    for rel_as in related_as_list:
                        if not rel_as in relatedas_pops_dict:
                            relatedas_pops_dict[rel_as] = {}

                        related_pop_dictionnary = relatedas_pops_dict[rel_as]

                        if not related_pop in related_pop_dictionnary:
                            related_pop_dictionnary[related_pop] = related_pop


print "Step 1 DONE"

print "Step 2: write pop_relatedas_pops dict in pop_relatedas_pops.pickle..."

pop_relatedas_pops_path = os.path.relpath(pickle_dir + "pop_relatedas_pops.pickle")

with open(pop_relatedas_pops_path, 'wb') as handle:
    pickle.dump(pop_relatedas_pops, handle)

print "Step 2 DONE, " + str(len(pop_relatedas_pops)) + " PoPs in the dict"
