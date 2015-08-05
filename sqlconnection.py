#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      szhang
#
# Created:     21/04/2014
# Copyright:   (c) szhang 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------


import pyodbc

# connection parameters

driver = 'SQL Server Native Client 10.0'
server = 'vdb_dwadhoc'
database = 'ProdDB_EDW'

# connection string with parameters

connStr = 'DRIVER={%s};SERVER=%s;DATABASE=%s;trusted_connection=yes' %(driver,server,database)


# create connection object

conn = pyodbc.connect(connStr)
cursor = conn.cursor()
cursor.execute("select top 10 UCDMID from fact_registrant")
rows = cursor.fetchall()
for row in rows:
    print row

