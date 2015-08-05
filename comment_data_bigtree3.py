

#Pull Persona Comments Data from all the slices 

import pyodbc
import time
import XmlDictObject


def bigtree():
  bigtree = open("ClusterSample.xml")
  # parse out the tid,pid
  bigtree_gid = 0
  counter = 1
  outdict = {}
  for line in bigtree:
    #print line
    if line == '</cluster>':
      continue
    if line.startswith("<cluster gid"):
      bigtree_gid = line.split('"')[1]
    elif line.strip().startswith("<clustermember"):  
      splitline = line.split(">")
      gid = splitline[1].split("<")[0]
      tid = gid.split(":")[2]
      pid = gid.split(":")[0]
      outdict[counter] = [bigtree_gid, tid, pid]
      counter += 1
  return outdict


#connect and run sql
def sql(server, database, sql_query):
  import pyodbc
  # connection parameters
  driver = 'SQL Server Native Client 11.0'
  # connection string with parameters
  connStr = 'DRIVER={%s};SERVER=%s;DATABASE=%s;trusted_connection=yes' %(driver,server,database)

  # create connection object
  conn = pyodbc.connect(connStr)
  cursor = conn.cursor()
  
  #print sql_query
  #execute the sql code 
  cursor.execute(sql_query)
  rows = cursor.fetchall()
  return rows


## need to script the query creation step itself to create a long in statement


def main(): 
  timestart = time.time()
  print '\t'.join(["db_source", "cluster", "tid", "pid", "subject", "comment", "datestamp"])
  db = 11
  treedict = bigtree()
  #loop through the db slices
  while db <= 44:
    print "DB: ", db
    key = 1
    endkey = 1000
    #query 1000 tid/pid pairs at a time for each database 
    while key <= 400000: 
      keysub = key
      sqlFile = "select * from treedb.dbo.XCommentPersonas where "    
      sqlFile = sqlFile + " (tid = " + treedict[key][1] + " and pid = " + treedict[key][2] + ")"
      keysub += 1
      #build the sql query with tid/pid pairs
      while keysub <= endkey:        
        sqlFile = sqlFile + " or (tid = " + treedict[key][1] + " and pid = " + treedict[key][2] + ")"      
             
        keysub += 1
      sql_query = str(sqlFile)   
      #print sql_query
      #run the concatenated sql query
      dbout = sql('vdb_treedb' + str(db) + '_repl', 'TreeDB', sql_query) 
      #print out the final info
      for el in dbout:
        tid = str(el[0])
        pid = str(el[1])
        subject = el[4].encode('ascii', 'ignore')
        comment = ''.join(el[5].replace('\n', " ").encode('ascii', 'ignore').splitlines())
        datestamp = str(el[6])
        db_source = 'vdb_treedb' + str(db) + '_repl'
        for key2 in treedict:
          if treedict[key][1] == tid and treedict[key][2] == pid:
            cluster = treedict[key][0]
        print '\t'.join([db_source, cluster, tid, pid, subject, comment, datestamp])
      key += 1000
      endkey += 1000
    db += 1   

  timeend = time.time()
  print "total time: ", timeend - timestart
if __name__ == '__main__':
  main()






