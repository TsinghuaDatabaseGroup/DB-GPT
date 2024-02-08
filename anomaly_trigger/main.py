import argparse
import anomaly
import createdatabase
import dropdatabase



parser = argparse.ArgumentParser(description='Anomaly simulation tool')
parser.add_argument('--anomaly', type=str, required=True, choices=['INSERT_LARGE_DATA', 'MISSING_INDEXES','LOCK_CONTENTION','VACUUM','REDUNDANT_INDEX','INSERT_LARGE_DATA,IO_CONTENTION',
                                                                   'FETCH_LARGE_DATA,CORRELATED_SUBQUERY','POOR_JOIN_PERFORMANCE,CPU_CONTENTION'],
                        help='Specify the type of anomaly to simulate')
parser.add_argument('--threads',type=int,default=0,help='threads')
parser.add_argument('--duration', type=int, default=60, help='duration')
parser.add_argument('--ncolumn', type=int, default=10,help="number of columns")
parser.add_argument('--nrow', type=int, default=100,help="number of rows")
parser.add_argument('--colsize', type=int, default=200,help="column length")
parser.add_argument('--table_size', type=int, default=10,help="table size")
parser.add_argument('--table_name', type=str,default='table1', help="name of table to be excuted")
parser.add_argument('--nindex',type=int,default=5,help='index in the REDUNDANT_INDEX')

args = parser.parse_args()
#anomaly=parser.anomaly
threads= args.threads
duration = args.duration
ncolumns = args.ncolumn
nrows = args.nrow
colsize = args.colsize
nindex=args.nindex
table_name = args.table_name


if args.anomaly == 'INSERT_LARGE_DATA':
        dropdatabase.dropdatabase("tmp")
        createdatabase.createdatabase("tmp")
        anomaly.insert_large_data(threads,duration,ncolumns,nrows,colsize,table_name)
        dropdatabase.dropdatabase("tmp")

elif args.anomaly == 'MISSING_INDEXES':
        dropdatabase.dropdatabase("tmp")
        createdatabase.createdatabase("tmp")
        anomaly.missing_index(threads,duration,ncolumns, nrows, colsize,table_name)
        dropdatabase.dropdatabase("tmp")

elif args.anomaly == 'LOCK_CONTENTION':
        dropdatabase.dropdatabase("tmp")
        createdatabase.createdatabase("tmp")
        anomaly.lock_contention(threads,duration,ncolumns, nrows, colsize,table_name)
        dropdatabase.dropdatabase("tmp")

elif args.anomaly == 'VACUUM':
        dropdatabase.dropdatabase("tmp")
        createdatabase.createdatabase("tmp")
        anomaly.vacuum(threads,duration,ncolumns, nrows, colsize,table_name)
        dropdatabase.dropdatabase("tmp")
        
elif args.anomaly == 'REDUNDANT_INDEX':
        dropdatabase.dropdatabase("tmp")
        createdatabase.createdatabase("tmp")
        anomaly.redundent_index(threads,duration,ncolumns,nrows,colsize,nindex,table_name)
        dropdatabase.dropdatabase("tmp") 
             
elif args.anomaly == 'INSERT_LARGE_DATA,IO_CONTENTION':
        anomaly.io_contention()
            
elif args.anomaly == 'FETCH_LARGE_DATA,CORRELATED_SUBQUERY':
        anomaly.fetch_large_data()  
          
elif args.anomaly == 'POOR_JOIN_PERFORMANCE,CPU_CONTENTION':
        anomaly.cpu_contention() 
                       
else:
        print("Invalid --anomaly option.")


