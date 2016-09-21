
import mygeneinfo
import data_model as dm

class Term2gene_mapper():
    def __init__(self):
        # a map to hold the term to gene mapping to speed the query.
        self.term_to_gene_map = {}

    def reset(self):
        self.term_to_gene_map = {}

    def add_network_nodes(self, node_table):
        query_string =""
        for node_id, node in node_table.items():
            query_string = query_string + " " + list(node.get('name'))[0]
        gene_list = mygeneinfo.query_batch(query_string)
        for hit in gene_list:
            term = hit.get('query')
            symbol = hit.get('symbol')
            id = hit.get('entrezgene')
            if symbol and id:
                gene = dm.Gene(hit.get('symbol'), hit.get('entrezgene'))
                self.term_to_gene_map[term] = gene
            else:
                print "no symbol and id for " + term
        return gene_list

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


    # a variation of the function above. Returns the Gene object rather than a gene symbol
    # returns None if term can't be mapped to a gene.
    def gene_symbol_and_id_from_term(self, term):
        gene = self.term_to_gene_map.get(term)
        if gene:
            return gene
        else:
            # look for term on external service
            gene = mygeneinfo.query_standard_to_gene_quick(term)
            if gene:
                self.term_to_gene_map[term] = gene
                return gene
            else :
                print term + " doesn't map to any gene"
                return None

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

