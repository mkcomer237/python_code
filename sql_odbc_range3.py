


def sql_tree_range(server, database, starttree, endtree, daylimit):
  import pyodbc
  # connection parameters
  driver = 'SQL Server Native Client 11.0'
  # connection string with parameters
  connStr = 'DRIVER={%s};SERVER=%s;DATABASE=%s;trusted_connection=yes' %(driver,server,database)

  # create connection object
  conn = pyodbc.connect(connStr)
  cursor = conn.cursor()
  
  sqlFile = """   
  select
    tid,
    cast(pid as varchar(25)),
    coalesce(father, 'n') as father,
    coalesce(mother, 'n') as mother,
    case when max_child is null then 0 else 1 end as has_child
  from (
    select 
      r.tid, 
      r.pid, 
      max(cast(case when role = 1 then rid else null end as varchar(30))) as Father,
      max(cast(case when role = 2 then rid else null end as varchar(30))) as Mother,
      max(cast(case when role = 16 then rid else null end as varchar(30))) as max_child
    from (
      select 
      *,
      min(datestamp) over (partition by tid) as tree_create_date
      from """ + database +""".dbo.XRelationships r with(nolock) 
      where
        tid between """ + str(starttree) + ' and ' + str(endtree) + """ 
        --tid = 55683073
      ) as r
    where
      role in (1,2,16)
      and datediff(day, tree_create_date, datestamp) <= """ + str(daylimit) + """
    group by
      r.tid,
      r.pid
    ) as qq
  where 
    coalesce(father, mother) is not null
  order by
    tid,
    pid
  """

  
  
  
  
  sql_query = str(sqlFile)
  #print sql_query
  #execute the sql code 
  cursor.execute(sql_query)
  rows = cursor.fetchall()
  return rows


