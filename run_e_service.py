__author__ = 'dexter'

# This script is called from the command line to run the enrichment server with the persisted e_sets
#
# The script reads all of the e_sets and then starts the bottle server
#
# The optional argument 'verbose' specifies verbose logging for testing
#

#
# python run_e_service.py
#
# python run_e_service.py --verbose
#

# body

import argparse
from bottle import route, run, template, default_app, request, response
import data_model as dm
import json
import term2gene_mapper

parser = argparse.ArgumentParser(description='run the enrichment server')

parser.add_argument('--verbose', dest='verbose', action='store_const',
                    const=True, default=False,
                    help='verbose mode')

arg = parser.parse_args()

if arg.verbose:
    print "Starting enrichment server in verbose mode"
else:
    print "Starting enrichment server"


e_data = dm.EnrichmentData("e_sets")
e_data.load()
app = default_app()
app.config['enrichment_data'] = e_data
app.config['enrichment_verbose'] = arg.verbose


class EnableCors(object):
    name = 'enable_cors'
    api = 2

    def apply(self, fn, context):
        def _enable_cors(*args, **kwargs):
            # set CORS headers
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'

            if request.method != 'OPTIONS':
                # actual request; reply with the actual response
                return fn(*args, **kwargs)

        return _enable_cors


@route('/hello/<name>',method=['OPTIONS','GET'])
def index(name):
    verbose_mode = app.config.get("enrichment_verbose")
    if verbose_mode:
        return template('<b>This is the test method saying Hello verbosely to {{name}}</b>!', name=name)
    else:
        return template('<b>Hello {{name}}</b>!', name=name)

# GET the list of all the loaded e_sets
@route('/esets', method=['OPTIONS','GET'])
def get_e_sets():
    e_data = app.config.get("enrichment_data")
    result = []
    url=request.url
    for eset_name in e_data.get_e_set_names() :
       result.append(url + "/" + eset_name)
    return { "e_sets": result}   # json.dumps(result)

# GET the information for one e_set, all the id_set names and meta information
@route('/esets/<esetname>', method=['OPTIONS','GET'])
def get_id_sets(esetname):
    e_data = app.config.get("enrichment_data")
    return e_data.get_id_set_names(esetname, url=request.url)

# GET the information for one id_set
@route('/esets/<esetname>/idsets/<idsetid>' , method=['OPTIONS','GET'] )
def get_id_set(esetname, idsetid):
    e_data = app.config.get("enrichment_data")
    id_set = e_data.get_id_set(esetname, idsetid)
    if not id_set:
        return {}
    return id_set.to_dict()

@route('/esets/query', method=['OPTIONS','POST'])
def run_query():
    verbose_mode = app.config.get("enrichment_verbose")
    e_data = app.config.get("enrichment_data")
    data = request.body
    t = type(data)
    s = str(data)
    dict = json.load(data)
    esetname = dict.get("eset")
    query_ids = dict.get('ids')
 #   query_id_set = dm.IdentifierSet({"ids": query_ids})
    term_mapper = term2gene_mapper.Term2gene_mapper()
    standardized_search_terms = term_mapper.standarize_terms(query_ids)
    result = e_data.get_scores_on_stardarized_query_terms(esetname, standardized_search_terms, verbose_mode)
    return result

app.install(EnableCors())
app.run(host='0.0.0.0', port=8090)