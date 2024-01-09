import re
from automatic_prompt_engineer import ape, config, template, utils
from utils.database import Database, DBArgs
from utils.db_utils import preprocess_execute_sql
from time import sleep
import psycopg2

def get_sql_cost(prediction, answers, args, timeout=-1):
    db = Database(args, timeout=timeout)
    flag, prediction = preprocess_execute_sql(prediction)
    if flag == 0:
        return [0, -1]
    flag, res = db.execute_sql(prediction)
    if flag == 0 or len(res) != int(answers['result_len']):
        return [0, -2]
    if len(res) == 1 and str(res[0]) != answers['result']:
        return [0, -3]
    cost = db.cost_estimation(prediction)
    return [1, cost]

def get_sql_latc_cost(prediction, answers, args, timeout=-1):
    db = Database(args, timeout=timeout)
    flag, prediction = preprocess_execute_sql(prediction)
    if flag == 0:
        return [0, -1, -1]
    db = Database(args, timeout=timeout)
    latency = db.pgsql_actual_time(prediction)
    if latency == -1:
        return [0, -1, -1]
    flag, res = db.execute_sql(prediction)
    if flag == 0 or len(res) != int(answers['result_len']):
        return [0, -2, -2]
    if len(res) == 1 and str(res[0]) != answers['result']:
        return [0, -3, -3]
    cost = db.cost_estimation(prediction)
    assert cost != -1
    return [1, cost, latency]


def get_sql_score_index_tuning(prediction, vald_data, args):
    args = DBArgs("pgsql", utils.get_conf(args.db_conf, 'pgsql_server'), args.eval_dataset)
    db = Database(args, timeout=-1)

    with_index_cost = 0
    no_index_cost = 0
    
    # Regular expression to match CREATE INDEX statements
    regex = r'CREATE INDEX.*?;'
    # Extract CREATE INDEX statements
    indexes = re.findall(regex, prediction, re.IGNORECASE | re.DOTALL)
    for index in indexes:
        print(index)
        
    ## create the indexes
    index_ids = []
    index_stat = ""
    for index in indexes:
        success = 1
        try:
            res = db.simulate_index(index)
        except Exception as e:
            print("fail to build the index: {}".format(index))
            success = 0
            sleep(1)
            
        if success == 1:
            print("success!")
            index_ids.append(res[0])
            index_stat = index_stat + index
            sleep(.5)

    if index_ids != []:

        for sql in vald_data:
            # cost = db.pgsql_cost_estimation("SELECT c_phone, o_custkey, l_quantity, ps_availqty FROM customer JOIN orders ON o_custkey = c_custkey JOIN lineitem ON l_orderkey = o_orderkey JOIN partsupp ON ps_partkey = l_suppkey WHERE l_orderkey > 1105060 AND c_acctbal = -364.16 AND l_comment > 'efully blithely idle depos'")
            with_index_cost = with_index_cost + db.pgsql_cost_estimation(sql)
            print(with_index_cost)

        for iid in index_ids:
            try:
                res = db.drop_simulated_index(iid)
            except Exception as e:
                #print("fail to drop the index {}".format(iid))
                pass

        for sql in vald_data:
            #cost2 = db.pgsql_cost_estimation("SELECT c_phone, o_custkey, l_quantity, ps_availqty FROM customer JOIN orders ON o_custkey = c_custkey JOIN lineitem ON l_orderkey = o_orderkey JOIN partsupp ON ps_partkey = l_suppkey WHERE l_orderkey > 1105060 AND c_acctbal = -364.16 AND l_comment > 'efully blithely idle depos'")    
            no_index_cost = no_index_cost + db.pgsql_cost_estimation(sql)
            print(no_index_cost)

        return [1, -(no_index_cost - with_index_cost)]

    else:
        return [0, 0]

    '''
    args = DBArgs("", "pgsql")
    db = Database(args, timeout=timeout)
    prediction = re.sub(r'(create|CREATE)\s+(table|TABLE).+;','',prediction, count=2)
    if prediction.rstrip()[-1] != ';':
        prediction += ';'

    flag, res = db.execute_sql(prediction)
    print(prediction, flag, res)
    if flag == 0:
        return [0, 0]
    cost = db.cost_estimation(prediction)
    return [1, cost]    
    '''

def check_index_query(query):
    try:

        # 
        conn = psycopg2.connect("dbname=imdbload user=postgres host=166.111.121.62 password=3b3cf6777213")
        cur = conn.cursor()
        cur.execute(query)
        cur.close()
        conn.commit()
        conn.close()
        return True
    except psycopg2.Error as e:
        #print(e)
        return False

def create_indexes(indexes, budget):
    for index in indexes:
        if check_index_query(index) == False:
            print("create index failure!")
            print(index)            

def drop_indexes(indexes):
    for index in indexes:
        check_index_query("drop index IF EXISTS {}".format(index.split()[2]))
