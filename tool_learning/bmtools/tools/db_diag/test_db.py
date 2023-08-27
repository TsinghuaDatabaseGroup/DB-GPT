import json
import os
import requests
import numpy as np
import openai

from bmtools.tools.db_diag.utils.db_parser import get_conf
from bmtools.tools.db_diag.utils.database import DBArgs, Database

# load db settings
from utils.core import read_yaml

script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(script_path)
script_dir = os.path.dirname(script_dir)

postgresql_conf = read_yaml('POSTGRESQL', 'config/tool_config.yaml')
dbargs = DBArgs("postgresql", config=postgresql_conf)  # todo assign database name

# send request to database
db = Database(dbargs, timeout=-1)

db.obtain_historical_slow_queries()