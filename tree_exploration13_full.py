

import sys
import time
import sql_odbc_range3 as sql
import pyodbc
import itertools as it


#autoviv implementation 

class autoviv(dict):
    """Implementation of perl's autovivification feature."""
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value



# import and format the data (created a nested dictionary): 
# (This does load the dataset into memory)

def import_file(starttree, endtree, server, days, dbname):

  treefile = sql.sql_tree_range(server, dbname, starttree, endtree, days)
  treedictnew = autoviv()
  
  for line in treefile:
    treedictnew[str(line[0])][str(line[1])] = [str(line[2]), str(line[3]), str(line[4])]
  return treedictnew


## For every node crawl through every possible path of mothers and fathers to get the depth 

def get_parents(originchild, treedict, counter):
  counter = 0
  circular = 0
  inner_count = 0
  childlist_new = [originchild]
  
  while 1==1:
    childlist = childlist_new 
    childlist_new = [] #erase new childlist to accept the parents of each child
    inner_count = 0
    for child in childlist:
      #get the mothers and fathers for the new people added only as one step with one counter increment
      #add the mother and father for every child in the list (list keeps growing)
      father = str(treedict[child][0])
      mother = str(treedict[child][1])
      #check for circular infinite trees: 
      if counter >= 1000:
        return 9999
      if inner_count >= 2000:
        return 9999
      #add mother and father to the new lists
      if len(father) >= 3:
        childlist_new.append(father)
      if len(mother) >= 3:
        childlist_new.append(mother)
      inner_count += 1
    if childlist == []:
      break
    counter += 1
  return counter 


#calculate the depth for every node with no children and take the max 

def count_relationships(treedict):
  max_depth = -1
  node_counter = 0
  max_depthnode = 0
  for key in treedict.keys():
    current_max_depth = 0
    #run get parents only for childless bottom nodes 
    #loop through each node
    if treedict[key][2] <> '0':
      continue
    current_max_depth = get_parents(key, treedict, 0)
    node_counter += 1
    if current_max_depth > max_depth:
      max_depth = current_max_depth
      max_depthnode = key
    #break out early if it's a problem tree to improve performance
    if max_depth == 9999:
      return max_depth, max_depthnode, node_counter
  return str(max_depth), str(max_depthnode), str(node_counter)



def get_tree_depth(output):
  tree_max_depth = count_relationships(output)
  return [str(tree_max_depth[0]), str(tree_max_depth[1]), str(tree_max_depth[2])]


#run the full query for a single db

def run_db(increment, last_tree, runs, server, days, dbname):
  iteration = 1
  tree = last_tree + increment
  #loop through importing sets of trees and pull incrementally from sql
  while iteration <= runs:
    #looptimestart = time.time()
    treedict=import_file(last_tree, tree, server, days, dbname)
    treedict
    #now loop through one tree at a time to calculate the max depth 
    for key in treedict.keys():
      try:
        variables = [key]
        for value in get_tree_depth(treedict[key]):
          variables.append(value)
        print '\t'.join(variables)
      except(RuntimeError):
        print '\t'.join([str(key), "null", "null", "null"])  #print treedict
    tree += increment
    last_tree += increment
    iteration += 1


def main(): 
  timestart = time.time()
  print '\t'.join(["Tree", "Depth", "Bottom_Node", "Child_Nodes"])
  db = 14
  #loop through the db slices
  while db <= 14:
    # BatchSize, StartNode, Iterations, ServerName, DaysCutoff, DBName)
    run_db(10000, 65646870, 1, 'vdb_treedb' + str(db) + '_repl', 2000, 'TreeDB')
    db += 1   
  timeend = time.time()
  print "total time: ", timeend - timestart
if __name__ == '__main__':
  main()








