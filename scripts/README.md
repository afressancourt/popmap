# Intercloud overlay architecture evaluation

This set of Python scripts has been developped in order to evaluate the Intercloud architecture described in the paper _A SDN-based network architecture for cloud resiliency_. This evaluation is trying to be more accurate than the evaluation presented in _Intercloud: Steering Cloud Traffic at IXPs to Improve Resiliency_ in that it takes into account the asymmetry of inter-AS relationships.

## Table of Contents

* [Datasets](#datasets)
* [Python scripts](#python-scripts)
  * [The build data script](#the-build-data-script)
    * [IP-IXP-Dict-Build.py](#ip-ixp-dict-buildpy)
    * [IXP-AS-Dict-Build.py](#ixp-as-dict-buildpy)
    * [IP-PoP-Dict-Build.py](#ip-pop-dict-buildpy)
    * [PoP-relatedAS-PoPs-Dict-Build.py](#pop-relatedas-pops-dict-buildpy)
    * [AS-PoP-Dict-Build.py](#as-pop-dict-buildpy)
  * [The missing script](#the-missing-script)
    * [IXP-Missing-AS.py](#ixp-missing-aspy)
    * [PoP-IXP-Association-Graph.py](#pop-ixp-association-graphpy)
    * [PoP-IXP-Association-Geo.py](#pop-ixp-association-geopy)
    * [PoP-IXP-Association-Confirmed.py](#pop-ixp-association-confirmedpy)
    * [AS-Policy-Dict-Build.py](#as-policy-dict-buildpy)
  * [The dragon-study script](#the-dragon-study-script)
    * [Dragon-AS-Build.py](#dragon-as-buildpy)
    * [Graph-AS-Directed-Build-method2.py](#graph-as-directed-build-method2py)
    * [Graph-AS-Directed-Study.py](#graph-as-directed-studypy)
    * [iPlane-Graph-Build.py](#iplane-graph-buildpy)
  * [Miscelaneous files](#miscelaneous-files)
    * [utils.py](#utilspy)
    * [consistency-IXP.py](#consistency-ixppy)
    * [Graph-AS-Directed-Reach](#graph-as-directed-reach)

=============================
## Datasets

In order to perform this evaluation, we use four datasets in a coordinated way:

* **The iPlane dataset**: this dataset has been presented in the paper _iPlane: An Information Plane for Distributed Services_. It gathers measurements on latency between PoPs that are routers in various ASes in the Internet. We use several files from this dataset:

  * **ip\_to\_pop\_mapping.txt**: This file contains a mapping of IP addresses to the various PoPs in the iPlane dataset.

  * **inter\_pop\_links** : This directory contains files logging the observed inter-PoP links on a given day, with their related AS and the observed mean latency.

  * **origin\_as\_mapping.txt**: This file contains the mapping between IP addresses sets and AS number that is used by iPlane to map the PoPs to the relevant AS.

* **The DRAGON dataset**: This dataset has been presented in the paper _Distributed Route Aggregation on the Global Network_. It gives a view of the relationship between ASes and tags the links between them to determine whether they are provider-customer, customer-provider or peer-to-peer. This dataset consists in one file:
  * **topology.201309.txt**: this file contains the declaration of the links between ASes as well as the relationship they have.

* **PeeringDB**: We use this open database to retrieve information about the various IXPs in the Internet: their IP addresses range, the ASes that participate in those IXPs. Note that this script has been written to be used with the 1st version of PeeringDB. As PeeringDB v2 is now online, those scripts might need to be adapted. Please also note that if you don't care about working with IXPs, you may not need to use this dataset. The PeeringDB SQL dump has been used to produce several data files:

  * **mgmtPublicsIPs.csv**: This file gathers the IP addresses of the public peering facilities present in the PeeringDB database.

  * **mgmtPublics.csv**: This file gathers IP addresses of public facilities present in PeeringDB. Those IP addresses are extracted from a table with a wider set of information.

  * **peerParticipantsPublics.csv**: This file gathers the information from the participants to public exchange facilities in the PeeringDB database.

  * **peerParticipants.csv**: This file gathers information from the participants to either public or private peering facilities. We use in particular this file to get information on ASes' peering policies.

* **The MaxMind GeoLite2-City database**: We use this database to retrieve a location of various IP addresses associated with PoPs or IXPs. Actual data can be retrieved from Maxmind's website.

* **The CSP\_AS-complementary.txt file**: This file contains the list of AS numbers for Cloud Services Providers (CSPs) we are interested in.

=============================
## Python scripts

=============================
### The build data script

This script, named *Build_data*, executes 5 python scripts to build data to be used in our evaluation.

### IP-IXP-Dict-Build.py

The goal of this script is to build two dictionnaries that will help us associate IP addresses belonging to an IXP to the relevant IXP, and retrieve all the IP addresses for a given IXP.

The script takes **three files** as data sources:

* **mgmtPublicsIPs.csv**
* **mgmtPublicsIPs.csv**
* **peerParticipantsPublics.csv**

It produces **two dictionnaries** stored as pickle files:

* **ip\_ixp.pickle** which associates each IP to the IXP it belongs to.
* **ixp\_ips.pickle** which associates each IXP to the IP addresses it has.

### IXP-AS-Dict-Build.py

The goal of this script is to build two dictionnaries that will help us associate ASes with the IXPs they participate in, and retrieve ths association quickly.

The script takes **one file** as data source:

* peerParticipantsPublics.csv

It produces **two dictionnaries** stored as pickle files:

* **ixp\_ases.pickle** which associates each IXP to the ASes that participate in it.
* **as\_ixps.pickle** which associates each AS to the IXPs it participates in.

### IP-PoP-Dict-Build.py

The goal of this script is to build two dictionnaries that will help us detremine quickly which IPs a given router (PoP in iPlane's terminology) has, and which router is associated to a given IP.

The script takes **one file** as data source:

* **ip\_to\_pop\_mapping.txt**

It produces **two dictionnaries** stored as pickle files:

* **ip\_pop.pickle** which associates each IP to the PoP it belongs to.
* **pop\_ips.pickle** which associates each PoP to the IPs it has.

### PoP-relatedAS-PoPs-Dict-Build.py

The goal of this script is, for each PoP in the iPlane dataset, to determine which ASes it has relationship with, and which PoPs in those ASes it is in relation with. The script produces a dictionnary containing itself dictionnaries, following the structure:
```
Pop
 |-> AS
      |-> PoP
      |-> PoP
```

The script takes as data source:

* **the inter\_pop\_links/ directory**

It produces **one dictionnary** stored as a pickle file:

* **pop\_relatedas\_pops.pickle** which is a dictionnary containing nested dictionnaries, as presented upper in this section.

### AS-PoP-Dict-Build.py

In order to get a clean view on which PoP belongs to which IP, we build two dictionnaries that associate PoPs with ASes using the PoPs' IP addresses to determine which AS they belong to. Executing this script is rather lengthy.

This sript takes **one file** as data source:

* **origin\_as\_mapping.txt**

It loads **two pickle dictionnaries**:

* **ip\_pop.pickle**
* **pop\_ips.pickle**

It produces **two dictionnaries** stored as pickle files:

* **pop\_as.pickle** which gives the association of one PoP with its AS
* **as\_pops.pickle** which gives all the PoPs belonging to a given AS

=============================
## The missing script

In _Anatomy of a Large European IXP_, the authors clearly state that the peering at IXPs is largely underestimated and misunderstood looking at routing tables. This script, named *missing*, executes 5 python scripts to prepare our future work on taking those missing peering links into account.

### IXP-Missing-AS.py

In the "Build data" phase, we have determined which IP addresses belong to each PoP, which IP addresses belong to an IXP and which ASes participate in each IXP. We observe a gap between the observed PoP membership and the declared AS participation for a number of IXPs. The goal of this specific script is to identify for which AS we lack a participating PoP for each IXP, and which AS have their participation confirmed by the presence of a PoP in each IXP.

This script loads **four dictionnaries**:

* **ip\_ixp.pickle**
* **ip\_pop.pickle**
* **pop\_as.pickle**
* **ixp\_ases.pickle**

It produces **four dictionnaries**. Those dictionnaries have their name suffixed by "_1" in order to keep track of what is happening at each step of the execution of the missing script:

* **ixp\_pops\_1.pickle** which contains the PoPs participating in each IXP
* **ixp\_ases\_1.pickle** which contains the ASes that declared a participation in each IXP
* **ixp\_missing\_ases\_1.pickle** which contains ASes for which we are missing information about the participating PoP in each IXP
* **ixp\_confirmed\_ases\_1.pickle** which contains ASes for which we have a confirmed participation in each IXP by knowing which PoP participates in the IXP.

### PoP-IXP-Association-Graph.py

With this script, we try to find information about the PoPs participating in each IXP by observing the iPlane graph. For each PoP participating in an IXP, we look at the PoPs with which it has links that belong to an AS whose presence has not been confirmed in the IXP. If we find some, we include them in the PoPS participating in the IXP, we remove associated ASes from the missing ASes and add the ASes in the confirmed ASes.

This script loads **five dictionnaries**:

* **ixp\_ases\_1.pickle**
* **ixp\_missing\_ases\_1.pickle**
* **ixp\_pops\_1.pickle**
* **ixp\_confirmed\_ases\_1.pickle**
* **pop\_relatedas\_pops.pickle**

It produces **four dictionnaries**. Those dictionnaries have their name suffixed by "_2" in order to keep track of what is happening at each step of the execution of the missing script:

* **ixp\_pops\_2.pickle**
* **ixp\_ases\_2.pickle**
* **ixp\_missing\_ases\_2.pickle**
* **ixp\_confirmed\_ases\_2.pickle**

### PoP-IXP-Association-Geo.py

With this script, we try to find additionnal information about the participation of PoPs to each IXP. For each IXP's missing AS, we look at the distance between each PoP and the IXP based on IP address geolocation information retrieved from MaxMind. For each PoP located less than 100 km from the IXP, if less than 10 PoP are in this vincinity for the AS, we declare that the PoP belongs to the IXP, add the related AS among the confirmed ASes and remove the AS from the missing ASes.

The distance criteria is given by the **max\_distance\_ixp** variable. The maximum number of PoPs in the vincinity is given by the **max\_number\_pop\_ixp\_as** variable.

This script loads **seven dictionnaries**:

* **ixp\_ases\_2.pickle**
* **ixp\_missing\_ases\_2.pickle**
* **ixp\_pops\_2.pickle**
* **ixp\_confirmed\_ases\_2.pickle**
* **as\_pops.pickle**
* **pop\_ips.pickle**
* **ixp\_ips.pickle**

It produces **four dictionnaries**. Those dictionnaries have their name suffixed by "_3" in order to keep track of what is happening at each step of the execution of the missing script:

* **ixp\_pops\_3.pickle**
* **ixp\_ases\_3.pickle**
* **ixp\_missing\_ases\_3.pickle**
* **ixp\_confirmed\_ases\_3.pickle**

### PoP-IXP-Association-Confirmed.py

We use this script to identify the IXPs which are interesting for our study. To do that, we look at IXPs for which the length of the confirmed AS dictionnary is strictly bigger than 1.

The minimum number of confirmed ASes allowing an IXP to be selected as a eligible IXP is given by the **min\_confirmed\_as\_participant** variable.

This script loads **four dictionnaries**:

* **ixp\_ases\_3.pickle**
* **ixp\_missing\_ases\_3.pickle**
* **ixp\_confirmed\_ases\_3.pickle**
* **ixp\_pops\_3.pickle**

It produces **one dictionnary**:

* **eligible\_ixps.pickle**, which contains the IXPs that are eligible to our study.

### AS-Policy-Dict-Build.py

This script looks at the peering policies for the various ASes listed in PeeringDB. We will use this information to determine the probability for a given PoP to establish an invisible missing link with another PoP at an IXP to take into consideration the results from the paper _Anatomy of a Large European IXP_.

The script takes **one file** as data source:

* **peerParticipants.csv**

It produces **two dictionnaries**:

* **as\_policy.pickle**, which gives the policy associated to a given AS
* **policy\_ases.pickle**, which gives the ASes following a given policy.

## The dragon-study script

This script, named *dragon-study*, executes the python scripts that we hav built in order to study the Dragon topology presented in the article _Distributed Route Aggregation on the Global Network_. This topology presents the link between ASes according to the nature of their link: customer-provider, provider-customer, peer-to-peer.

### Dragon-AS-Build.py

This python script builds a dictionnary of the ASes that are present in the Dragon topology.

The script takes **one file** as data source:

* **topology.201309.txt**

It produces **one dictionnary**:

* **dragon\_ases.pickle**, which contains the ASes that are present in the Dragon topology.

### Graph-AS-Directed-Build-method2.py

This python script builds a directed graph from the Dragon topology and a dictionnary containing the edges and associated relationship property. The file is suffixed "-method2" because the first version of the script added edges in the graph one by one with iGraph's "add edge()" method, which takes a very long time. This version adds the edges alltogether using iGraph's "add edges()" method which is much quicker, then associates relationship properties to the edges one by one.

The script takes **one file** as data source:

* **topology.201309.txt**

It produces **one dictionnary**:

* **dragon\_edges.pickle**, which contains the edges between ASes and associated relationship properties that are present in the Dragon topology.

It produces **one graph** stored as a pickle file:

* **as-directed-graph-method2.pickle**

### Graph-AS-Directed-Study.py

This python script computes the reachability of interesting ASes with regards to Gao-Rexford BGP routing policies. Interesting ASes are ASes of CSPs listed in the file "CSP_AS-complementary.txt" and ASes participating in at least one IXP. The computing of the Gao-Rexford policy is done by a method in utils.py file.

This script loads **two dictionnaries**:

* **ixp\_confirmed\_ases\_3.pickle**
* **dragon\_ases.pickle**

It produces **two dictionnaries**:

* **interesting\_ases.pickle** which contains the list of the interesting ASes.
* **interesting\_ases\_reach.pickle** which contains the number of ASes in the Dragon topology that each AS can reach.

### iPlane-Graph-Build.py

This python script parses the links of the iPlane topology and, for the PoPs belonging to an AS that is present in the Dragon topology, build an inter-PoP edge with associated relationship properties. When the two PoPs are in the same AS, the relationship property for the edge is set to "0". When the two PoPs are not in the same AS but the inter-AS link is not in the Dragon topology, the relationship property is set to "5".

The script takes **one directory** as data source:

* **inter\_pop\_links/**

It loads **two dictionnaries**:

* **dragon\_ases.pickle**
* **dragon\_edges.pickle**

It produces **three dictionnaries**:

* **iPlane\_edges.pickle**, which lists the edges of the directed graph to build with iPlane
* **iPlane\_pop\_relatedpops.pickle**, which is a dictionnary containing, for each PoP, a dictionnary of the PoPs it is related to.
* **iPlane\_pop\_as.pickle**, which is a dictionnary containing the PoPS and the AS they belong to according to iPlane.

## Miscelaneous files

### utils.py

This file contains several methods that are used along the scripts:

* **distance\_on\_unit\_sphere(lat1, long1, lat2, long2)**: This method is used to compute the distance between two points on a sphere of radius 1 given their respective latitude and longitude.

* **ipToInt(ip)**: This method converts IP addresses to an integer.

* **isIpInSubnet(ip, ipNetwork, maskLength)**: This method determines whether an IP address belongs to a given subnet.

* **edge\_name(first\_string, second\_string)**: This method is used to name edges in an undirected graph colliding the name of the two peer with the shortest identifier first.

* **depth\_first\_search\_gao\_rexford(graph, start\_node, visited\_set={})**: This method gives the reach of the node with index *start\_node* in the graph *graph* following Gao-Rexford's BGP routing policy. It returns the visited set.

* **full\_depth\_first\_search\_gao\_rexford(graph)**: This method does the full reach search for the graph *graph*. It returns a dictionnary with the visited sets indexed by the indexes of the nodes in the graph.

