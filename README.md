# ndex-enrich
Python-based enrichment service (e_service) that uses NDEx networks as the source of identifier sets (id_sets).

An enrichment query gives a response of ranked NDEx network ids, plus meta-information.

The service is run using the script run_e_service.py

python run_e_service.py

When the service starts, it loads an enrichment data (e_data) structure of enrichment sets (e_sets) from the persistence service.

Each e_set is a set of id_sets.

The e_data is created and updated by the script update_e_data.py

python update_e_data.py config_example --rebuild

The e_data is specified by a JSON configuration document that is loaded from the persistence service.

The file e_service_configuration/cravat_test is an example configuration structure.

Note that while the persistence service is currently implemented by local file operations, 
the long-term plan is to abstract it as a web service to make it easier to package the e_service
in a Docker container for deployment.

---

A REST query to the service running on localhost:

POSTURL: http://localhost:5601/esets/Cravat NCI/query

POSTDATA: {"ids":["AKT1", "PTK2B", "VGFR1", "CAV1", "CALM2", "PIK3CA", "KPCD", "KPCA"]}

