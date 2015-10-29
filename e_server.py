__author__ = 'dexter'

from bottle import route, run, template, default_app
import data_model as dm

verbose_mode = False


e_data = {}



# GET the list of all the loaded e_sets
@route('/esets')
def get_e_sets():
    #e_data = app.config.get("enrichment_data")
    return e_data.get_e_set_names()

# GET the information for one e_set, all the id_set names and meta information
@route('/esets/<esetname>')
def get_id_sets(esetname):
    return e_data.get_id_set_names()

# GET the information for one id_set
@route('/esets/<esetname>/idsets/<idsetname>')
def get_id_set(esetname, idsetname):
    id_set = e_data.get_id_set(esetname, idsetname)
    return id_set.to_dict()

# POST an enrichment query for all e_sets
#@post
#@route()

# POST an enrichment query for one e_set
# @route('/esets/<esetname>/query')
# def query_e_set(esetname, query_string):
#     ids = query_string.split()
#     e_set = e_data.get_e_set(esetname)
#     return e_set.query_e_set(ids)

