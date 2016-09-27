import mygeneinfo
import data_model as dm
import re


class Term2gene_mapper():
    def __init__(self):
        # a map to hold the term to gene mapping to speed the query.
        self.term_to_gene_map = {}
        self.excluded_id_regex = re.compile('[(),\'\"\s]+')

    def reset(self):
        self.term_to_gene_map = {}

    def get_identifier_without_prefix(self, string):
        # remove the prefix, if there is one

        elements = string.split(':')
        length = len(elements)
        if length is 2:
            return str(elements[1])
        elif length > 2:
            return None
        else:
            return string

    def exclude_id(self, id):
        #if len(id) > 10:
        #    return None
        #if id == "3',5'-cyclic GMP":
        #   print "test!"
        result = self.excluded_id_regex.search(id)
        return result

    def add_network_nodes(self, node_table):
        query_string = ""
        for node_id, node in node_table.items():
            name = list(node.get('name'))[0]
            if self.exclude_id(name) is None:
                query_string = query_string + " " + name
            if node.get('alias'):
                for alias in node.get('alias'):
                    id = self.get_identifier_without_prefix(alias)
                    if id:
                        if self.exclude_id(id) is None:
                            query_string = query_string + " " + id
                        else:
                            print "skipping " + id

        gene_list = mygeneinfo.query_batch(query_string)
        for hit in gene_list:
            term = hit.get('query')
            symbol = hit.get('symbol')
            id = hit.get('entrezgene')
            if symbol and id:
                gene = dm.Gene(hit.get('symbol'), hit.get('entrezgene'))
                self.term_to_gene_map[term] = gene
                # else:
                # print "no symbol and id for " + term
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
            else:
                print term + " doesn't map to any gene"
            return gene

    def get_gene_from_identifier(self, identifier):
        key = self.get_identifier_without_prefix(identifier)
        gene = self.term_to_gene_map.get(key)
        if gene:
            return gene
        else:
            # print key + " doesn't map to any gene"
            return None

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
            else:
                print term + " doesn't map to any gene"
                return None

    # returns a set of gene symbols found in the given function term
    def genes_from_function_term(self, function_term):
        # if it is a function term, process all genes mentioned
        result = set([])
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
    def standarize_terms(self, terms):
        result = {'matched': {}, 'unmatched': []}
        for term in terms:
            symbol = self.gene_from_term(term)
            if symbol:
                matched_genes = result['matched']
                if symbol in matched_genes:
                    matched_genes[symbol].append(term)
                else:
                    matched_genes[symbol] = [term]
            else:
                result['unmatched'].append(term)

        return result
