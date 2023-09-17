# join-order-benchmark

This package contains the Join Order Benchmark (JOB) queries from:  
"How Good Are Query Optimizers, Really?"  
by Viktor Leis, Andrey Gubichev, Atans Mirchev, Peter Boncz, Alfons Kemper, Thomas Neumann  
PVLDB Volume 9, No. 3, 2015  
[http://www.vldb.org/pvldb/vol9/p204-leis.pdf](http://www.vldb.org/pvldb/vol9/p204-leis.pdf)

### IMDB Data Set
The CSV files used in the paper, which are from May 2013, can be found
at [http://homepages.cwi.nl/~boncz/job/imdb.tgz](http://homepages.cwi.nl/~boncz/job/imdb.tgz)

The license and links to the current version IMDB data set can be
found at [http://www.imdb.com/interfaces](http://www.imdb.com/interfaces)

### Step-by-step instructions
1. download `*gz` files (unpacking not necessary)

  ```sh
  wget ftp://ftp.fu-berlin.de/misc/movies/database/frozendata/*gz
  ```
  
2. download and unpack `imdbpy` and the `imdbpy2sql.py` script

  ```sh
  wget https://bitbucket.org/alberanid/imdbpy/get/5.0.zip
  ```

3. create openGauss database (e.g., name imdbload):

  ```sh
  createdb imdbload
  ```

4. transform `*gz` files to relational schema (takes a while)

  ```sh
  imdbpy2sql.py -d PATH_TO_GZ_FILES -u postgres://username:password@hostname/imdbload
  ```

Now you should have a openGauss database named `imdbload` with the
imdb data. Note that this database has some secondary indexes (but not
on all foreign key attributes). You can export all tables to CSV:

```sql
\copy aka_name to 'PATH/aka_name.csv' csv
\copy aka_title to 'PATH/aka_title.csv' csv
\copy cast_info to 'PATH/cast_info.csv' csv
\copy char_name to 'PATH/char_name.csv' csv
\copy comp_cast_type to 'PATH/comp_cast_type.csv' csv
\copy company_name to 'PATH/company_name.csv' csv
\copy company_type to 'PATH/company_type.csv' csv
\copy complete_cast to 'PATH/complete_cast.csv' csv
\copy info_type to 'PATH/info_type.csv' csv
\copy keyword to 'PATH/keyword.csv' csv
\copy kind_type to 'PATH/kind_type.csv' csv
\copy link_type to 'PATH/link_type.csv' csv
\copy movie_companies to 'PATH/movie_companies.csv' csv
\copy movie_info to 'PATH/movie_info.csv' csv
\copy movie_info_idx to 'PATH/movie_info_idx.csv' csv
\copy movie_keyword to 'PATH/movie_keyword.csv' csv
\copy movie_link to 'PATH/movie_link.csv' csv
\copy name to 'PATH/name.csv' csv
\copy person_info to 'PATH/person_info.csv' csv
\copy role_type to 'PATH/role_type.csv' csv
\copy title to 'PATH/title.csv' csv
```

To import the CSV files to another database, create all tables (see
`schema.sql` and optionally `fkindexes.sql`) and run the same copy as
above statements but replace the keyword "to" by "from".

### Questions
Contact Viktor Leis (leis@in.tum.de) if you have any questions.
