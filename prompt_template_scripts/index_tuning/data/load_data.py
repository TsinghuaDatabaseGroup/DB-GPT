import json

def load_data(path, task, type):

    with open(path, 'r') as f:
        data = json.load(f)

    examples = data['examples']
    num_examples = len(examples)

    inputs, outputs = [], []
    for i in range(num_examples):
        data = examples[str(i + 1)]
        if task == 'query_rewrite':
            if type == 'train':
                input_, output_ = data['input'], data['output']
            else:
                input_, output_ = data['input'], {'output':data['output'], 'result':data['result'] if 'result' in data else None, 'result_len':data['result_len'], 'input_cost':data['input_cost'], 'output_cost':data['output_cost'], 'dataset':data['dataset'], 'input_latency':data['input_latency'], 'output_latency':data['output_latency']}

        inputs.append(input_)
        outputs.append(output_)
    return inputs, outputs

def load_data(path, type, task, use_schema):

    with open(path, 'r') as f:
        data = json.load(f)

    examples = data['examples']
    num_examples = len(examples)

    inputs, outputs = [], []
    for i in range(num_examples):
        data = examples[str(i + 1)]

        input_ = ""
        output_ = ""
        if 'index_tuning' in task:
            sqls, output_ = data['input'], data['output']
            
            schema = ""
            if "tpch" in data['database'] and use_schema == 1:
                schema = "TPC-H schema"
            elif "tpcds" in data['database'] and use_schema == 1:
                schema = "TCP-DS schema"
            elif "job" in data['database'] and use_schema == 1:
                schema = """the column name_pcode_cf owns 901343 rows and 0.01361302 distinct value ratio; the column name_pcode_nf owns 901343 rows and 0.01133198 distinct value ratio; the column surname_pcode owns 901343 rows and 0.00286794 distinct value ratio; the column imdb_index owns 361472 rows and 0.00001937 distinct value ratio; the column kind_id owns 361472 rows and 0.00001660 distinct value ratio; the column production_year owns 361472 rows and 0.00033751 distinct value ratio; the column phonetic_code owns 361472 rows and 0.03382558 distinct value ratio; the column episode_of_id owns 361472 rows and 0.00042050 distinct value ratio; the column season_nr owns 361472 rows and 0.00004980 distinct value ratio; the column episode_nr owns 361472 rows and 0.00013279 distinct value ratio; the column note owns 361472 rows and 0.00335296 distinct value ratio; the column person_id owns 36244300 rows and 0.00199888 distinct value ratio; the column movie_id owns 36244300 rows and 0.02623337 distinct value ratio; the column person_role_id owns 36244300 rows and 0.00036439 distinct value ratio; the column note owns 36244300 rows and 0.00009157 distinct value ratio; the column nr_order owns 36244300 rows and 0.00000400 distinct value ratio; the column role_id owns 36244300 rows and 0.00000030 distinct value ratio; the column name_pcode_nf owns 3140340 rows and 0.00392282 distinct value ratio; the column surname_pcode owns 3140340 rows and 0.00156607 distinct value ratio; the column country_code owns 234997 rows and 0.00068512 distinct value ratio; the column name_pcode_nf owns 234997 rows and 0.04896233 distinct value ratio; the column name_pcode_sf owns 234997 rows and 0.04506866 distinct value ratio; the column subject_id owns 135086 rows and 0.00001481 distinct value ratio; the column status_id owns 135086 rows and 0.00001481 distinct value ratio; the column phonetic_code owns 134170 rows and 0.07899680 distinct value ratio; the column company_id owns 2609130 rows and 0.00759679 distinct value ratio; the column company_type_id owns 2609130 rows and 0.00000077 distinct value ratio; the column note owns 2609130 rows and 0.00201293 distinct value ratio; the column movie_id owns 14835700 rows and 0.02428493 distinct value ratio; the column info_type_id owns 14835700 rows and 0.00000472 distinct value ratio; the column info owns 14835700 rows and 0.00137257 distinct value ratio; the column note owns 14835700 rows and 0.00008803 distinct value ratio; the column info_type_id owns 1380040 rows and 0.00000290 distinct value ratio; the column info owns 1380040 rows and 0.00811861 distinct value ratio; the column movie_id owns 4523930 rows and 0.02189313 distinct value ratio; the column keyword_id owns 4523930 rows and 0.00331261 distinct value ratio; the column link_type_id owns 29997 rows and 0.00053339 distinct value ratio; the column imdb_index owns 4167490 rows and 0.00001944 distinct value ratio; the column gender owns 4167490 rows and 0.00000048 distinct value ratio; the column name_pcode_cf owns 4167490 rows and 0.00296221 distinct value ratio; the column name_pcode_nf owns 4167490 rows and 0.00258885 distinct value ratio; the column surname_pcode owns 4167490 rows and 0.00065627 distinct value ratio; the column person_id owns 2963660 rows and 0.03834043 distinct value ratio; the column info_type_id owns 2963660 rows and 0.00000742 distinct value ratio; the column info owns 2963660 rows and 0.05158891 distinct value ratio; the column note owns 2963660 rows and 0.00022641 distinct value ratio; the column title owns 2528310 rows and 0.05521475 distinct value ratio; the column imdb_index owns 2528310 rows and 0.00000316 distinct value ratio; the column kind_id owns 2528310 rows and 0.00000237 distinct value ratio; the column production_year owns 2528310 rows and 0.00004825 distinct value ratio; the column phonetic_code owns 2528310 rows and 0.00426055 distinct value ratio; the column episode_of_id owns 2528310 rows and 0.00471738 distinct value ratio; the column season_nr owns 2528310 rows and 0.00002610 distinct value ratio; the column episode_nr owns 2528310 rows and 0.00044892 distinct value ratio; the column series_years owns 2528310 rows and 0.00007673 distinct value ratio."""                

            if use_schema == 1:
                input_ = "The data statistics are {} The storage space for created indexes is limited (500MB).\n The queries are ".format(schema)
            else:
                input_ = "The queries are ".format(schema)
            max_num_sql = 8
            for i,sql in enumerate(sqls):
                input_ = input_ + sql + " "
                if i+1 >= max_num_sql:
                    break


        inputs.append(input_)
        outputs.append(output_)
    return inputs, outputs



'''
NATION: This table contains information about different nations. The columns in the table are: N_NATIONKEY (integer, unique identifier), N_NAME (char(25), name of the nation), N_REGIONKEY (integer, foreign key referring to the region to which the nation belongs), and N_COMMENT (varchar(152), a comment about the nation).
REGION: This table contains information about different regions. The columns in the table are: R_REGIONKEY (integer, unique identifier), R_NAME (char(25), name of the region), and R_COMMENT (varchar(152), a comment about the region).
PART: This table contains information about different parts. The columns in the table are: P_PARTKEY (integer, unique identifier), P_NAME (varchar(55), name of the part), P_MFGR (char(25), the manufacturer of the part), P_BRAND (char(10), the brand of the part), P_TYPE (varchar(25), the type of the part), P_SIZE (integer, the size of the part), P_CONTAINER (char(10), the type of container used for the part), P_RETAILPRICE (decimal(15,2), the retail price of the part), and P_COMMENT (varchar(23), a comment about the part).
SUPPLIER: This table contains information about different suppliers. The columns in the table are: S_SUPPKEY (integer, unique identifier), S_NAME (char(25), name of the supplier), S_ADDRESS (varchar(40), address of the supplier), S_NATIONKEY (integer, foreign key referring to the nation to which the supplier belongs), S_PHONE (char(15), phone number of the supplier), S_ACCTBAL (decimal(15,2), account balance of the supplier), and S_COMMENT (varchar(101), a comment about the supplier).
PARTSUPP: This table contains information about the supply of different parts by different suppliers. The columns in the table are: PS_PARTKEY (integer, foreign key referring to the part that is supplied), PS_SUPPKEY (integer, foreign key referring to the supplier that supplies the part), PS_AVAILQTY (integer, the quantity of the part that is available), PS_SUPPLYCOST (decimal(15,2), the cost of supplying the part), and PS_COMMENT (varchar(199), a comment about the supply).
CUSTOMER: This table contains information about different customers. The columns in the table are: C_CUSTKEY (integer, unique identifier), C_NAME (varchar(25), name of the customer), C_ADDRESS (varchar(40), address of the customer), C_NATIONKEY (integer, foreign key referring to the nation to which the customer belongs), C_PHONE (char(15), phone number of the customer), C_ACCTBAL (decimal(15,2), account balance of the customer), C_MKTSEGMENT (char(10), the market segment to which the customer belongs), and C_COMMENT (varchar(117), a comment about the customer).
ORDERS: This table contains information about different orders placed by customers. The columns in the table are: O_ORDERKEY (integer, unique identifier), O_CUSTKEY (integer, foreign key referring to the customer who placed the order), O_ORDERSTATUS (char(1), the status of the order), O_TOTALPRICE (decimal(15,2), the total price of the order), O_ORDERDATE (date, the date the order was placed), O_ORDERPRIORITY (char(15), the priority of the order), O_CLERK (char(15), the name of the clerk who processed the order, O_SHIPPRIORITY (integer, the shipping priority of the order), and O_COMMENT (varchar(79), a comment about the order). 
LINEITEM: This table contains information about the line items included in different orders. The columns in the table are: L_ORDERKEY (integer, foreign key referring to the order to which the line item belongs), L_PARTKEY (integer, foreign key referring to the part in the line item), L_SUPPKEY (integer, foreign key referring to the supplier of the part in the line item), L_LINENUMBER (integer, the line number of the item), L_QUANTITY (decimal(15,2), the quantity of the item), L_EXTENDEDPRICE (decimal(15,2), the extended price of the item), L_DISCOUNT (decimal(15,2), the discount applied to the item), L_TAX (decimal(15,2), the tax applied to the item), L_RETURNFLAG (char(1), the return flag for the item), L_LINESTATUS (char(1), the line status for the item), L_SHIPDATE (date, the shipping date of the item), L_COMMITDATE (date, the date the item was committed), L_RECEIPTDATE (date, the date the item was received), L_SHIPINSTRUCT (char(25), the shipping instructions for the item), L_SHIPMODE (char(10), the shipping mode for the item), and L_COMMENT (varchar(44), a comment about the item).
'''

"""\"Table aka_name:
* id: integer (NOT NULL, PRIMARY KEY)
* person_id: integer (NOT NULL)
* name: varchar(512)
* imdb_index: varchar(3)
* name_pcode_cf: varchar(11)
* name_pcode_nf: varchar(11)
* surname_pcode: varchar(11)
* md5sum: varchar(65)
Table aka_title:
* id: integer (NOT NULL, PRIMARY KEY)
* movie_id: integer (NOT NULL)
* title: varchar(1000)
* imdb_index: varchar(4)
* kind_id: integer (NOT NULL)
* production_year: integer
* phonetic_code: varchar(5)
* episode_of_id: integer
* season_nr: integer
* episode_nr: integer
* note: varchar(72)
* md5sum: varchar(32)
Table cast_info:
* id: integer (NOT NULL, PRIMARY KEY)
* person_id: integer (NOT NULL)
* movie_id: integer (NOT NULL)
* person_role_id: integer
* note: varchar(1000)
* nr_order: integer
* role_id: integer (NOT NULL)
Table char_name:
* id: integer (NOT NULL, PRIMARY KEY)
* name: varchar(512) (NOT NULL)
* imdb_index: varchar(2)
* imdb_id: integer
* name_pcode_nf: varchar(5)
* surname_pcode: varchar(5)
* md5sum: varchar(32)
Table comp_cast_type:
* id: integer (NOT NULL, PRIMARY KEY)
* kind: varchar(32) (NOT NULL)
Table company_name:
* id: integer (NOT NULL, PRIMARY KEY)
* name: varchar(512) (NOT NULL)
* country_code: varchar(6)
* imdb_id: integer
* name_pcode_nf: varchar(5)
* name_pcode_sf: varchar(5)
* md5sum: varchar(32)
Table company_type:
* id: integer (NOT NULL, PRIMARY KEY)
* kind: varchar(32)
Table complete_cast:
* id: integer (NOT NULL, PRIMARY KEY)
* movie_id: integer
* subject_id: integer (NOT NULL)
* status_id: integer (NOT NULL)
Table info_type:
* id: integer (NOT NULL, PRIMARY KEY)
* info: varchar(32) (NOT NULL)
Table keyword:
* id: integer (NOT NULL, PRIMARY KEY)
* keyword: varchar(512) (NOT NULL)
* phonetic_code: varchar(5)
Table kind_type:
* id: integer (NOT NULL, PRIMARY KEY)
* kind: varchar(15)
Table link_type:
* id: integer (NOT NULL, PRIMARY KEY)
* link: varchar(32) (NOT NULL)
Table movie_companies:
* id: integer (NOT NULL, PRIMARY KEY)
* movie_id: integer (NOT NULL)
* company_id: integer (NOT NULL)
* company_type_id: integer (NOT NULL)
* note: text
Table movie_info_idx:
* id: integer (NOT NULL, PRIMARY KEY)
* info_type_id: integer (NOT NULL)
* info: text (NOT NULL)
* note: text
Table movie_keyword:
* id: integer (NOT NULL, PRIMARY KEY)
* movie_id: integer (NOT NULL)
* keyword_id: integer (NOT NULL)
Table movie_link:
* id: integer (NOT NULL, PRIMARY KEY)
* movie_id: integer (NOT NULL)
* linked_movie_id: integer (NOT NULL)
* link_type_id: integer (NOT NULL)
Table name:
* id: integer (NOT NULL, PRIMARY KEY)
* name: varchar(512) (NOT NULL)
* imdb_index: varchar(9)
* imdb_id: integer
* gender: varchar(1)
* name_pcode_cf: varchar(5)
* name_pcode_nf: varchar(5)
* surname_pcode: varchar(5)
* md5sum: varchar(32)
Table role_type:
* id: integer (NOT NULL, PRIMARY KEY)
* role: varchar(32) (NOT NULL)
Table title:
* id: integer (NOT NULL, PRIMARY KEY)
* title: varchar(512) (NOT NULL)
* imdb_index: varchar(5)
* kind_id: integer (NOT NULL)
* production_year: integer
* imdb_id: integer
* phonetic_code: varchar(5)
* episode_of_id: integer
* season_nr: integer
* episode_nr: integer
* series_years: varchar(49)
* md5sum: varchar(32)
Table movie_info:
* id: integer (NOT NULL, PRIMARY KEY)
* movie_id: integer (NOT NULL)
* info_type_id: integer (NOT NULL)
* info: text (NOT NULL)
* note: text
Table person_info:
* id: integer (NOT NULL, PRIMARY KEY)
* person_id: integer (NOT NULL)
* info_type_id: integer (NOT NULL)
* info: text (NOT NULL)
* note: text\"
"""