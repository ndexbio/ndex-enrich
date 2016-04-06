__author__ = 'dexter'


class GeneReport():
    def __init__(self, name):
        self.gene_network_pairs = {}
        self.name = name
        self.fields = [
            "Gene Symbol",
            "Entrez Gene Id",
            "Network Id",
            "Network Name",
            "Network Sets"
        ]

    def add_gene_network_pair(self, gene_id, gene_symbol, network_id, network_name, e_set_name):
        key = str(gene_id) + "_" + network_id
        pair = self.gene_network_pairs.get(key)
        if not pair:
            pair = {
                "Gene Symbol": gene_symbol,
                "Entrez Gene Id": gene_id,
                "Network Id": network_id,
                "Network Name": network_name,
                "e_sets": [e_set_name]
            }
            self.gene_network_pairs[key] = pair
        else:
            e_sets = pair["e_sets"]
            if e_set_name not in e_sets:
                e_sets.append(e_set_name)
                pair["e_sets"] = e_sets

    def get_rows(self):
        s = ", "
        for pair in self.gene_network_pairs.values():
            pair["Network Sets"] = s.join(pair.get("e_sets"))
        return self.gene_network_pairs.values()


