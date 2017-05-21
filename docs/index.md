## PoPmap: a PoP-level Internet topology

### What is PoPmap?

In the course of my PhD work, I worked on an overlay network architecture, Kumori. This architecture aims at improving the resiliency of inter-datacenter connections over the Internet by enhancing the available path diversity between those datacenters.

In order to evaluate the path diversity gain offered by the Kumori architecture, I looked after topological representations of the Internet, and I fell short finding an appropriate topology:
- Several initiatives such as iPlane or RIPE Atlas publish data allowing researchers to build **router-level** internet representations. Those representations are interesting but they represent at the same level links between routers located at an operator's point of presence and between remote routers. Yet, we know that operators tend to connect routers at their points of presence in order to provide resiliency.
- CAIDA publishes an **AS-level** Internet topology. This topology is very interesting as it tags inter-AS relationships with the type of relationship linking the ASes, which allows researchers to determine which are the routable paths in the topology according to a given routing policy such as Gao Rexford's.
- In the DIMES project, Yuval Shavitt and Dima Feldman have proposed a **PoP-level** topology representing the Internet. While the publications made by the authors are very interesting to understand the way they built their PoP-level Internet topology, the data that are now available from the DIMES website are from 2012, and thus don't represent the Internet as it is today. 

With PoPmap, our goal is to provide the tools to generate up-to-date, PoP-level Internet topologies from available data sources.

The data and code is coming soon...
