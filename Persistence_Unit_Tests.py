__author__ = 'aarongary'

import unittest
from persistence import EnrichmentPersistence

class Dev_Uint_Tests(unittest.TestCase):
    def test_persistence(self):
        try:
            my_json = {
                'termClassification': [{
                        'status': 'unknown',
                        'geneSymbol': '',
                        'termId': 'RATTUS',
                        'probabilitiesMap': {
                            'icd10': '0.0',
                            'gene': '0.0',
                            'disease': '0.0',
                            'drug': '0.0',
                            'genome': '1.0'
                        },
                        'desc': ''
                    }, {
                        'status': 'success',
                        'geneSymbol': 'ENSG00000230855',
                        'termId': 'OR2J3',
                        'probabilitiesMap': {
                            'icd10': '0.0',
                            'gene': '1.0',
                            'disease': '0.0',
                            'drug': '0.0',
                            'genome': '0.0'
                        },
                        'desc': 'olfactory receptor, family 2, subfamily J, member 3 [Source:HGNC Symbol;Acc:HGNC:8261]'
                    }, {
                        'status': 'success',
                        'geneSymbol': 'ENSG00000129673',
                        'termId': 'AANAT',
                        'probabilitiesMap': {
                            'icd10': '0.0',
                            'gene': '1.0',
                            'disease': '0.0',
                            'drug': '0.0',
                            'genome': '0.0'
                        },
                        'desc': 'aralkylamine N-acetyltransferase [Source:HGNC Symbol;Acc:HGNC:19]'
                    }, {
                        'status': 'success',
                        'geneSymbol': '',
                        'termId': 'LYMPHATIC',
                        'probabilitiesMap': {
                            'icd10': '1.0',
                            'gene': '0.0',
                            'disease': '0.0',
                            'drug': '0.0',
                            'genome': '0.0'
                        },
                        'desc': ''
                    }, {
                        'status': 'success',
                        'geneSymbol': 'ENSG00000163749',
                        'termId': 'CCDC158',
                        'probabilitiesMap': {
                            'icd10': '0.0',
                            'gene': '1.0',
                            'disease': '0.0',
                            'drug': '0.0',
                            'genome': '0.0'
                        },
                        'desc': 'coiled-coil domain containing 158 [Source:HGNC Symbol;Acc:HGNC:26374]'
                    }, {
                        'status': 'success',
                        'geneSymbol': 'ENSG00000173261',
                        'termId': 'PLAC8L1',
                        'probabilitiesMap': {
                            'icd10': '0.0',
                            'gene': '1.0',
                            'disease': '0.0',
                            'drug': '0.0',
                            'genome': '0.0'
                        },
                        'desc': 'PLAC8-like 1 [Source:HGNC Symbol;Acc:HGNC:31746]'
                    }, {
                        'status': 'success',
                        'geneSymbol': '',
                        'termId': 'CAFFEINE',
                        'probabilitiesMap': {
                            'icd10': '0.5',
                            'gene': '0.0',
                            'disease': '0.0',
                            'drug': '0.5',
                            'genome': '0.0'
                        },
                        'desc': ''
                    }, {
                        'status': 'success',
                        'geneSymbol': '',
                        'termId': 'HUMAN',
                        'probabilitiesMap': {
                            'icd10': '1.0',
                            'gene': '0.0',
                            'disease': '0.0',
                            'drug': '0.0',
                            'genome': '0.0'
                        },
                        'desc': ''
                    }, {
                        'status': 'unknown',
                        'geneSymbol': '',
                        'termId': 'ASLFDKJDS',
                        'probabilitiesMap': {
                            'icd10': '0.0',
                            'gene': '0.0',
                            'disease': '0.0',
                            'drug': '0.0',
                            'genome': '0.0'
                        },
                        'desc': ''
                    }]
            }

            ep = EnrichmentPersistence()
            ep.save_file(my_json, 'my_test_6')
            ep.save_file(my_json, 'my_test_7')
            ep.save_file(my_json, 'my_test_8')
            ep.save_file(my_json, 'my_test_9')
            ep.save_file(my_json, 'my_test_10')

            print ep.get_file('my_test_8')
            self.assertTrue(1 == 1)
        except Exception as e:
            print e.message
            self.assertTrue(1 == 0)

if __name__ == '__main__':
    unittest.main()
