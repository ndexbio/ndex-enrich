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
from bottle import route, run, template, default_app, request, post,  hook, response
import data_model as dm
import json

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

@hook('after_request')
def enable_cors():
    response.headers['Access-Control-Allow-Origin'] = '*'

@route('/hello/<name>')
def index(name):
    verbose_mode = app.config.get("enrichment_verbose")
    if verbose_mode:
        return template('<b>This is the test method saying Hello verbosely to {{name}}</b>!', name=name)
    else:
        return template('<b>Hello {{name}}</b>!', name=name)

# GET the list of all the loaded e_sets
@route('/esets')
def get_e_sets():
    e_data = app.config.get("enrichment_data")
    return e_data.get_e_set_names()

# GET the information for one e_set, all the id_set names and meta information
@route('/esets/<esetname>')
def get_id_sets(esetname):
    e_data = app.config.get("enrichment_data")
    return e_data.get_id_set_names(esetname, url=request.url)

# GET the information for one id_set
@route('/esets/<esetname>/idsets/<idsetid>')
def get_id_set(esetname, idsetid):
    e_data = app.config.get("enrichment_data")
    id_set = e_data.get_id_set(esetname, idsetid)
    if not id_set:
        return {}
    return id_set.to_dict()

@route('/esets/<esetname>/query', method='POST')
def run_query(esetname):
    verbose_mode = app.config.get("enrichment_verbose")
    e_data = app.config.get("enrichment_data")
    data = request.body
    t = type(data)
    s = str(data)
    dict = json.load(data)
    query_ids = dict.get('ids')
    query_id_set = dm.IdentifierSet({"ids": query_ids})
    result = e_data.get_scores(esetname, query_id_set, verbose_mode)
    return result

run(app, host='localhost', port=5601)