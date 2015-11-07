import requests

def query_list(queries, tax_id='9606'):
    results = []
    for q in queries:
        results.append(query(q, tax_id))
    return results

def query(q, tax_id='9606'):
    r = requests.get('http://mygene.info/v2/query?q='+q+'&species='+tax_id)
    result = r.json()
    result['query'] = q
    return result


print query_list(['symbol:brca1','symbol:brca2'])