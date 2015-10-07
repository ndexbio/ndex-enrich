__author__ = 'dexter'

from scipy.stats import hypergeom

# createEnrichmentSet(setName)
# deleteEnrichmentSet(setName)
# updateEnrichmentSet(setName)
# addNetworkToEnrichmentSet(setName, NDExURI, networkId)
# removeNetworkFromEnrichmentSet(setName, networkId)
#
# getEnrichmentSet(setName)
# getEnrichmentSets()
# getEnrichmentScores(setName, IDList) => scores, status

class EnrichmentEngine():


    def calc_pvalue(query_id_set, reference_id_set, M):
        query_id_set = set(query_id_set)
        reference_id_set = set(reference_id_set)
        N = len(query_id_set)
        n = len(reference_id_set)
        overlap = query_id_set & reference_id_set
        k = len(overlap)
        return hypergeom(M, n, N).sf(k), list(overlap)

    def get_enrichment_scores(self, query_id_set, enrichment_set):
        return None

    def get_enrichment_scores(self, query_id_set, enrichment_set_name):
        enrichment_set = self.get_enrichment_set(enrichment_set_name)
        return None


# def gene_set_enrichment(gene_list, M=None):
#     '''
#     :param gene_list: list of gene symbols
#     :param M: total number of genes (derived from database, if None)
#     :return: filtered list of GO terms with p-value, q-value, and size of overlap
#     '''
#     client = pymongo.MongoClient()
#     if not M:
#         M = len(client.go.genes.distinct('gene'))
#     terms = list(client.go.genes.find({'gene': {'$in': list(gene_list)}}).distinct('go'))
#     terms = list(client.go.terms.find({'go': {'$in': terms}, 'n_genes': {'$gt': 2}}))
#     enriched = [dict(term.items() + zip(('pvalue', 'overlap'), calc_pvalue(gene_list, term['genes'], M))) for term in terms]
#     enriched.sort(key=lambda it: it['pvalue'])
#     for qvalue, it in itertools.izip(fdr([it['pvalue'] for it in enriched], presorted=True), enriched):
#         it['qvalue'] = qvalue
#
#     return enriched