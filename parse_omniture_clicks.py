


import sys




def main():
  rawfile = open("Clicks 7-18.txt")
  f = open('clean_omniture_newtrackking.txt', 'w')


  #print '\t'.join(["Cell", "Nav", "Clicks", "Visits"])
  for line in rawfile:
    splitline = line.split('\t')
    clickaction = splitline[1]
    clicks = splitline[2]
    visits = splitline [3].strip()

    
    splitaction = clickaction.split(':')
    testcell = splitaction[0].replace('"','')
    
    
    nav = splitaction[1].strip()
    try:
        subnav = splitaction[2].strip()
    except: 
        subnav = " "
    
    if nav =="Family Trees":
      nav = "TREES"
    if nav == "Collaborate":
      nav = "COLL"
    if nav == "Learning Center":
      nav = "LEARN"
    if nav == "Search":
      nav = "SEARCH"
    


    if subnav.lower().endswith('family tree'):
        subnav = 'specifc family tree'
    if nav == 'TREES' and subnav not in ('Family Trees', 'Start a new tree', 'Manage All Trees', ' '):
        subnav = 'specifc family tree'   
    
    #for el in splitaction:
    #   print testcell, el
        
    grouped_out = {}
    
    navgroup = nav + ': ' + subnav    
    
    print >> f, '\t'.join([testcell, nav, subnav, clicks, visits])    
    
    '''
    try:
        grouped_out[navgroup] = [grouped_out[navgroup][0] + clicks, grouped_out[navgroup][1] + visits]
    except(KeyError):
        grouped_out[navgroup] = [clicks, visits]
    #rename the clicks 
    '''
  #print grouped_out  
    
    
if __name__ == '__main__':
  main()











