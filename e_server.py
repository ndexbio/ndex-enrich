__author__ = 'dexter'

from bottle import route, run, template

verbose_mode = False

@route('/hello/<name>')
def index(name):
    if verbose_mode:
        return template('<b>This is the test method saying Hello verbosely to {{name}}</b>!', name=name)
    else:
        return template('<b>Hello {{name}}</b>!', name=name)

def run_e_server(verbose = False):
    verbose_mode = verbose
    run(host='localhost', port=5601)

# GET the list of all the loaded e_sets
@route('/esets')
def get_e_sets():
    return []

# GET the information for one e_set, all the id_set names and meta information
@route('/esets/<esetname>')
def get_e_set(esetname):
    return {}


# GET the information for one id_set
@route('/esets/<esetname>/idsets/<idsetname>')
def get_id_set(esetname, idesetname):
    return {}

# POST an enrichment query