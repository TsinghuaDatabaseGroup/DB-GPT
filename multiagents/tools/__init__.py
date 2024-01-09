
# from .metrics import knowledge_matcher

from .metrics import get_workload_statistics, get_slow_queries, WORKLOAD_FILE_NAME

from .metrics import current_diag_time, db

from .api_retrieval import APICaller, register_functions_from_module