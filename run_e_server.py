__author__ = 'dexter'

# This script is called from the command line to run the enrichment server with the persisted e_sets
#
# The script reads all of the e_sets and then starts the bottle server
#
# The optional argument 'verbose' specifies verbose logging for testing
#

# body

import argparse
from bottle import route, run, template, default_app
import data_model as dm

parser = argparse.ArgumentParser(description='run the enrichment server')

parser.add_argument('verbose', action='store')

arg = parser.parse_args()

if arg.verbose.lower() == "true":
    print "Starting enrichment server in verbose mode"
    verbose = True
else:
    print "Starting enrichment server"
    verbose = False

e_data = dm.EnrichmentData("e_sets")
e_data.load()
app = default_app()
app.config['enrichment_data'] = e_data
app.config['enrichment_verbose'] = verbose

@route('/hello/<name>')
def index(name):
    verbose_mode = app.config.get("enrichment_verbose")
    if verbose_mode:
        return template('<b>This is the test method saying Hello verbosely to {{name}}</b>!', name=name)
    else:
        return template('<b>Hello {{name}}</b>!', name=name)

# GET the list of all the loaded e_sets
@app.route('/esets')
def get_e_sets():
    e_data = app.config.get("enrichment_data")
    return e_data.get_e_set_names()

# GET the information for one e_set, all the id_set names and meta information
@app.route('/esets/<esetname>')
def get_id_sets(esetname):
    e_data = app.config.get("enrichment_data")
    return e_data.get_id_set_names(esetname)

# GET the information for one id_set
@app.route('/esets/<esetname>/idsets/<idsetname>')
def get_id_set(esetname, idsetname):
    e_data = app.config.get("enrichment_data")
    print "e_set: " + esetname
    print "id_set:" + idsetname
    id_set = e_data.get_id_set(esetname, idsetname)
    return id_set.to_dict()


run(app, host='localhost', port=5601)