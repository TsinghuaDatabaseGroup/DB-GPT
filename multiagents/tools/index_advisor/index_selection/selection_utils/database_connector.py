import logging
import time

import traceback


class DatabaseConnector:
    def __init__(self, config, autocommit=False):
        self.db_name = config
        self.config = config
        self.autocommit = autocommit

        # This does not reflect the number of unique simulated indexes
        # but the number of simulate_index calls
        self.simulated_indexes = 0
        self.cost_estimations = 0
        self.cost_estimation_duration = 0
        self.index_simulation_duration = 0

    def exec_only(self, statement):
        self._cursor.execute(statement)

    def exec_fetch(self, statement, one=True):
        self._cursor.execute(statement)
        # try:
        #     self._cursor.execute(statement)
        # except:
        #     print(statement)
        #     raise AssertionError
        if one:
            return self._cursor.fetchone()
        return self._cursor.fetchall()

    def enable_simulation(self):
        raise NotImplementedError

    def commit(self):
        self._connection.commit()

    def close(self):
        self._connection.close()
        logging.debug("Database connector closed: {}".format(self.db_name))

    def rollback(self):
        self._connection.rollback()

    def drop_index(self, index):
        statement = f"drop index {index.index_idx()}"
        self.exec_only(statement)

    def _prepare_query(self, query):
        if "create view" in query.text:
            for query_statement in query.text.split(";"):
                if "create view" in query_statement:
                    try:
                        self.exec_only(query_statement)
                    except Exception as e:
                        logging.error(e)
                        logging.error(traceback.format_exc())
                elif "select" in query_statement or "SELECT" in query_statement:
                    return query_statement
                    # queries.append(query_statement)
        else:
            return query.text

    def simulate_index(self, index):
        self.simulated_indexes += 1

        start_time = time.time()
        result = self._simulate_index(index)
        end_time = time.time()
        self.index_simulation_duration += end_time - start_time

        return result

    def drop_simulated_index(self, identifier):
        start_time = time.time()
        self._drop_simulated_index(identifier)
        end_time = time.time()
        self.index_simulation_duration += end_time - start_time

    def get_cost(self, query):
        self.cost_estimations += 1

        start_time = time.time()
        cost = self._get_cost(query)
        end_time = time.time()
        self.cost_estimation_duration += end_time - start_time

        return cost

    # This is very similar to get_cost() above. Some algorithms need to directly access
    # get_plan. To not exclude it from costing, we add the instrumentation here.
    def get_plan(self, query):
        self.cost_estimations += 1

        start_time = time.time()
        plan = self._get_plan(query)
        end_time = time.time()
        self.cost_estimation_duration += end_time - start_time

        return plan

    def table_exists(self, table_name):
        raise NotImplementedError

    def database_exists(self, database_name):
        raise NotImplementedError

    def drop_database(self, database_name):
        raise NotImplementedError

    def create_statistics(self):
        raise NotImplementedError

    def set_random_seed(self, value):
        raise NotImplementedError

    def _get_cost(self, query):
        raise NotImplementedError

    def _get_plan(self, query):
        raise NotImplementedError

    def _simulate_index(self, index):
        raise NotImplementedError

    def _drop_simulated_index(self, identifier):
        raise NotImplementedError
