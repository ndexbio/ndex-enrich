#!/usr/bin/python

'''
This script takes a CX network from stdin and print out a set of gene symbols found in node names,
represents, alias and function terms.
Gene Symbols are normallized to human genes using mygene.info services.

'''

import sys,json
import requests

def terms_from_function_term(function_term, term_set):
    # if it is a function term, process all genes mentioned
    for parameter in function_term['args']:

        if type(parameter) in (str, unicode):
            add_term( term_set,parameter)
        else:
            terms_from_function_term(parameter, term_set)

def query_to_gene_all(q, tax_id='9606'):
    r = requests.get('http://mygene.info/v2/query?q='+q+'&fields=symbol%2Centrezgene%2Censemblgene%2Cuniprot%2Calias&species='+tax_id+'&entrezonly=true')
    result = r.json()
    hits = result.get("hits")
    if hits and len(hits) > 0:
        hit = hits[0]
        gene =  hit.get('symbol')
        return gene
    return None

def add_term (term_set,term):
    term_set.add(term)
    words = term.split(":")
    if ( len(words)>1) :
        del words[0]
        term_set.add(":".join(words))


def main():
    data = json.load(sys.stdin)
 #   f = open("/Users/abc/Downloads/S1P5 pathway.cx","r")
 #   data = json.load(f)

    namespaces = {}

    terms = set()

    for aspect in data:
        if '@context' in aspect:
            elements = aspect['@context']
            if len(elements) > 0:
                if len(elements) > 1 or namespaces:
                    raise RuntimeError('@context aspect can only have one element')
                else:
                    namespaces = elements[0]
        elif 'nodes' in aspect:
            for node in aspect.get('nodes'):
                if 'n' in node and node['n']:
                    add_term(terms,node['n'])
                if 'r' in node and node['r']:
                    add_term(terms,node['r'])
        elif "nodeAttributes" in aspect:
            for attr in aspect ["nodeAttributes"]:
                if attr["n"] == "name" :
                    add_term(terms, attr["v"])
                elif attr["n"] == "alias":
                    for alias in attr['v']:
                        add_term (terms, alias)
        elif "functionTerms" in aspect:
            for functionTerm in aspect['functionTerms']:
                terms_from_function_term(functionTerm,terms)


    genes =set()
    for term in terms :
        gene =query_to_gene_all(term)
        if gene :
            genes.add(gene)

    for gene in genes:
        sys.stdout.write(gene+ "\n")


    sys.stdout.flush()



if __name__ == '__main__':
    main()