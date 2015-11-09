import requests
import data_model as dm

def query_list(queries, tax_id='9606'):
    results = []
    for q in queries:
        results.append(query(q, tax_id))
    return results

def query(q, tax_id='9606', entrezonly=True):
    if entrezonly:
        r = requests.get('http://mygene.info/v2/query?q='+q+'&species='+tax_id+'&entrezonly=true')
    else:
        r = requests.get('http://mygene.info/v2/query?q='+q+'&species='+tax_id)
    result = r.json()
    result['query'] = q
    return result

def query_symbol(q, tax_id='9606'):
    return query_to_gene("symbol:" + q, tax_id)

def query_uniprot(q, tax_id='9606'):
    return query_to_gene("uniprot:" + q, tax_id)

def query_entrez_gene(q, tax_id='9606'):
    return query_to_gene("entrezgene:" + q, tax_id)

def query_ensemble(q, tax_id='9606'):
    return query_to_gene("ensemble:" + q, tax_id)

def query_to_gene(q, tax_id='9606'):
    hits = query(q, tax_id).get("hits")
    if hits and len(hits) > 0:
        hit = hits[0]
        gene = dm.Gene(hit.get('symbol'), hit.get('entrezgene'))
        return gene
    return False

def query_standard_to_gene(q, tax_id='9606'):
    return query_symbol(q, tax_id) or query_entrez_gene(q, tax_id) or query_uniprot(q, tax_id) or query_ensemble(q, tax_id)



#print query_list(['symbol:brca1','symbol:brca2'])