import logging


# Class that encapsulates simulated/WhatIf-Indexes.
# This is usually used by the CostEvaluation class and there should be no need
# to use it manually.
# Uses hypopg for postgreSQL

class WhatIfIndexCreation:
    def __init__(self, db_connector):
        logging.debug("Init WhatIfIndexCreation")

        self.simulated_indexes = {}
        self.db_connector = db_connector

    def simulate_index(self, potential_index, store_size=False):
        result = self.db_connector.simulate_index(potential_index)
        index_oid = result[0]
        index_name = result[1]
        self.simulated_indexes[index_oid] = index_name
        potential_index.hypopg_name = index_name
        potential_index.hypopg_oid = index_oid

        if store_size:
            potential_index.estimated_size = self.estimate_index_size(index_oid)

    def drop_simulated_index(self, index):
        oid = index.hypopg_oid
        self.db_connector.drop_simulated_index(oid)
        del self.simulated_indexes[oid]

    def all_simulated_indexes(self):
        # todo: `()` or not.
        # if self.db_connector.config["postgresql"]["host"] in ["10.24.82.151", "10.24.82.152"]:
        #     statement = "select * from hypopg_list_indexes"
        # else:
        #     statement = "select * from hypopg_list_indexes()"

        # todo: newly added.
        try:
            statement = "select * from hypopg_list_indexes"
            indexes = self.db_connector.exec_fetch(statement, one=False)
        except:
            statement = "select * from hypopg_list_indexes()"
            indexes = self.db_connector.exec_fetch(statement, one=False)

        return indexes

    def estimate_index_size(self, index_oid):
        statement = f"select hypopg_relation_size({index_oid})"
        result = self.db_connector.exec_fetch(statement)[0]
        assert result > 0, "Hypothetical index does not exist."

        return result

    # TODO: refactoring
    # This is never used, we keep it for debugging reasons.
    def index_names(self):
        indexes = self.all_simulated_indexes()

        # Apparently, x[1] is the index' name
        return [x[1] for x in indexes]

    def drop_all_simulated_indexes(self):
        for key in self.simulated_indexes:
            self.db_connector.drop_simulated_index(key)
        self.simulated_indexes = {}
