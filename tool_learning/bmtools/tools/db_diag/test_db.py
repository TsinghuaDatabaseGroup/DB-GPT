import json
import os
import requests
import numpy as np
import openai

from bmtools.tools.database.utils.db_parser import get_conf
from bmtools.tools.database.utils.database import DBArgs, Database

# load db settings
script_path = os.path.abspath(__file__)
script_dir = os.path.dirname(script_path)
script_dir = os.path.dirname(script_dir)
config = get_conf(script_dir + '/my_config.ini', 'postgresql')
dbargs = DBArgs("postgresql", config=config)  # todo assign database name

# send request to database
db = Database(dbargs, timeout=-1)

db.obtain_historical_slow_queries()