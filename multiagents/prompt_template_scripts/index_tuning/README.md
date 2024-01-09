# DB-GPT for Index Tuning

## Methods
### 1. APE
We generate the instruction from a small number of collected samples (splitting into training and evaluation sets), i.e., deriving several instructions using the LLM on training set and choosing the best instruction by evaluating on evaluation set. e.g.,

Prompt:
```
Instruction: """
Given a SQL query, create an index statement to reduce the execution latency. 

Create an index statement by examining the query and finding the columns which are frequently used in filters, joins, and ordering. The index statement should include the names of the columns and their order.

The create index statements should be executed on a PostgreSQL database.
""".

Input: 
// 10 sqls in a workload
["SELECT name.name_pcode_nf, cast_info.person_role_id FROM cast_info JOIN name ON name.id = cast_info.person_id WHERE name.name_pcode_cf >= 'S5246' AND name.id <> 1826335 AND cast_info.person_role_id <> 693 AND cast_info.id <= 25682130 ORDER BY name.name_pcode_nf DESC, cast_info.person_role_id ASC",

"SELECT aka_name.name_pcode_cf, name.imdb_index, title.season_nr, cast_info.note FROM aka_name JOIN name ON name.id = aka_name.person_id JOIN cast_info ON cast_info.person_id = name.id JOIN title ON title.id = cast_info.movie_id WHERE name.name_pcode_nf > 'J524' AND aka_name.name_pcode_nf = 'K6451' AND aka_name.surname_pcode >= 'L2' ORDER BY aka_name.name_pcode_cf DESC",

"SELECT title.phonetic_code, role_type.id, complete_cast.movie_id, cast_info.role_id FROM role_type JOIN cast_info ON cast_info.role_id = role_type.id JOIN title ON title.id = cast_info.movie_id JOIN complete_cast ON complete_cast.movie_id = title.id WHERE title.production_year < 1977 AND role_type.id >= 9 AND complete_cast.id <> 15925 AND role_type.role >= 'cinematographer' ORDER BY complete_cast.movie_id ASC, title.phonetic_code ASC", 
...]
```

LLM "text-davinci-003" Output: 
```
// recommending 9 indexes, where only 1 index can be built within 500M storage space
CREATE INDEX info_type_movie_info_idx ON movie_info (info_type_id, id, movie_id); 
CREATE INDEX movie_info_idx_info_type_info ON movie_info_idx (info_type_id, info); 
CREATE INDEX person_info_name_gender_imdb_idx ON person_info (info_type_id, person_id); 
CREATE INDEX title_movie_info_idx_movie_id_idx ON movie_info_idx (movie_id); 
CREATE INDEX info_type_movie_info_idx ON movie_info (info_type_id); 
CREATE INDEX person_info_name_id_surname_pcode_idx ON person_info (name_id, surname_pcode); 
CREATE INDEX company_name_movie_companies_idx ON movie_companies (company_id); 
CREATE INDEX role_type_cast_info_movie_id_person_role_id_idx ON cast_info (role_id, movie_id, pe,rson_role_id);
CREATE INDEX name_gender_cast_info_nr_order_role_id_idx ON cast_info (nr_order, role_id); 
```

## Run
An example of the script for this task is shown in `run.sh`.

The result is like:

| Accuracy | Ape Index Latency  | Ape Improvement  | Optimal Index Latency  | Optimal Improvement  | Prompt |
| -------- | ------------------ | ---------------- | ---------------------- | -------------------- | -------------------- |
| 1.0 | 380204.04 | 5.1 | 373903.95 | 6.7 | Create index statements for the input SQL queries based on the given database schema.|