__author__ = 'aarongary'


import pickle

class EnrichmentPersistence:


    def save_file(self, my_file_contents, file_id):
        save_this_file = open(r'./persistence/' + file_id + '.pkl', 'wb')
        pickle.dump(my_file_contents, save_this_file)
        save_this_file.close()

    def get_file(self, file_id):
        return_this_file = open(r'./persistence/' + file_id + '.pkl', 'rb')
        return_this_content = pickle.load(return_this_file)
        return_this_file.close()

        return return_this_content