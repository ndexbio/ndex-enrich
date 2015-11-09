# ndex-enrich
Python-based enrichment service (e_service) that uses NDEx networks as the source of identifier sets (id_sets).

An enrichment query gives a response of ranked NDEx network ids, plus meta-information.

The service is run using the script run_e_service.py:

python run_e_service.py

When the service starts, it loads an enrichment data (e_data) structure of enrichment sets (e_sets) from the persistence service.

Each e_set is a set of id_sets.

The e_data is created and updated by the script update_e_data.py

The e_sets comprising the e_data is specified by a JSON configuration document that is loaded from the persistence service.

The file e_service_configuration/config_example is an example configuration structure.

The following command line runs the update with the config_example.json file 
the --rebuild option forces a full rebuild of all e_sets, whether or not the specified networks have changed since the last update

python update_e_data.py config_example --rebuild

Note that while the persistence service is currently implemented by local file operations, 
the long-term plan is to abstract it as a web service to make it easier to package the e_service
in a Docker container for deployment.

---

A REST query to the service running on localhost:

POSTURL: http://localhost:5601/esets/Cravat NCI/query

POSTDATA: {"ids":["AKT1", "PTK2B", "VGFR1", "CAV1", "CALM2", "PIK3CA", "KPCD", "KPCA"]}


___

ndex-enrich also includes the script create_gene_report.py 

This script takes an e_service_configuration and analyzes all of the specified networks to create a tab-delimited report.

The report has the following columns:

Gene Symbol	
Entrez Gene Id	
Network Id	
Network Name	
Network Sets

"Network Sets" is a comma-separated list of the e_sets in which the network appeared, for cases where e_sets overlap.

Usage:

python create_gene_report.py test_bel_nci 

This script uses the mygene.info REST API to normalize identifiers in networks to genes
It attempts to map identifiers found attached to the nodes as gene symbols, entrez gene ids, uniprot ids, and ensemble ids.
It is currently limited to human genes and does not perform any orthology mapping on ids. 
Identifiers matching human gene symbols are currently assumed to be human.

Status as of 11/9/15: slow operation, successful testing on NCI networks in SIF format

