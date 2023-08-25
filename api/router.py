from api.db_diag import bp as db_diag_api
from api.config import bp as config_api

router = [
    db_diag_api,
    config_api
]
