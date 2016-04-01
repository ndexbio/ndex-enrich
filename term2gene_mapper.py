
import mygeneinfo

class Term2gene_mapper():
    def __init__(self):
        # a map to hold the term to gene mapping to speed the query.
        self.term_to_gene_map = {}

    def reset(self):
        self.term_to_gene_map = {}

    # standardize a term to a gene symbol
    # input: search term as a single string
    # return: Single string if found a gene symbol for the input term, otherwise return None
    def gene_from_term(self, term):
        gene = self.term_to_gene_map.get(term)
        if gene:
            return gene
        else:
            # look for term on external service
            gene = mygeneinfo.query_term_to_gene(term)
            if gene:
                self.term_to_gene_map[term] = gene
            else :
                print term + " doesn't map to any gene"
            return gene

    # returns a set of gene symbols found in the given function term
    def genes_from_function_term(self, function_term):
        # if it is a function term, process all genes mentioned
        result = set ([])
        for parameter in function_term['args']:
            if type(parameter) == 'str':
                gene = self.gene_from_term(parameter)
                if gene:
                    result.add(gene)
            else:
                result.union(self.genes_from_function_term(parameter))
        return result

    # input: a collection of genes, we assume there is no dupicates in it.
    # returns: a nested hash table contains the mapping of search terms and mapped genes
    # returned data structure: {'matched': { gene_symbol: [search terms]}, 'unmatched':[search_term]}
    def standarize_terms (self, terms):
        result = {'matched': {}, 'unmatched':[]}
        for term in terms:
            symbol = self.gene_from_term(term)
            if symbol:
                matched_genes = result['matched']
                if symbol in matched_genes :
                    matched_genes[symbol].append(term)
                else:
                    matched_genes[symbol] = [term]
            else:
                result['unmatched'].append(term)

        return result

