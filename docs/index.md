## PoPmap: a PoP-level Internet toplogy

### What is PoPmap?

In the course of my PhD work, I worked on an overlay network architecture, Kumori. This architecture aims at improving the resiliency of inter-datacenter connections over the Internet by enhancing the available path diversity between those datacenters.

In order to evaluate the path diversity gain offered by the Kumori architecture, I looked after topological representations of the Internet, and I fell short finding an appropriate topology:
- Several initiatives such as iPlane or RIPE Atlas publish data allowing researchers to build router-level internet representations. Those representations are interesting but they represent at the same level links between routers located at an operator's point of presence and between remote routers. Yet, we know that operators tend to connect routers at their points of presence in order to provide resiliency.
- CAIDA publishes an AS-level Internet topology. This topology is very interesting as it tags inter-AS relationships with the type of relationship linking the ASes, which allows researchers to determine which are the routable paths in the topology according to a given routing policy such as Gao Rexford's.


### Markdown

Markdown is a lightweight and easy-to-use syntax for styling your writing. It includes conventions for

```markdown
Syntax highlighted code block

# Header 1
## Header 2
### Header 3

- Bulleted
- List

1. Numbered
2. List

**Bold** and _Italic_ and `Code` text

[Link](url) and ![Image](src)
```

For more details see [GitHub Flavored Markdown](https://guides.github.com/features/mastering-markdown/).

### Jekyll Themes

Your Pages site will use the layout and styles from the Jekyll theme you have selected in your [repository settings](https://github.com/afressancourt/popmap/settings). The name of this theme is saved in the Jekyll `_config.yml` configuration file.

### Support or Contact

Having trouble with Pages? Check out our [documentation](https://help.github.com/categories/github-pages-basics/) or [contact support](https://github.com/contact) and we’ll help you sort it out.
