


import sys
import json 
import time 
import fnmatch
import urlparse


#autovivication feature for nested dictionaries
class autoviv(dict):
    """Implementation of perl's autovivification feature."""
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value


#Import the data file into a nested dictonary 
#Data format:  Event 	Action	Visit	Sequence	URL
def create_nested_dict(open_file):
  footprint = autoviv()
  for line in open_file:
    splitline = line.split('\t')
    #print splitline[1]
    footprint[int(splitline[2])][int(splitline[3])][int(splitline[0])] = [splitline[1], splitline[4]]
  return footprint


#get the suggested or not tag out from the url query string  
'''
def get_flow_type(urlparam):
  try:
    suggested = urlparse.parse_qs(urlparam)['IsSuggested'][0]
    #print suggested
    if suggested.encode('ascii', 'ignore') == '1':
      return 'Suggested'
    else:
      return ''
  except(KeyError):
    return ''
'''

#standard get query string function

def get_qs(urlparam, qs_param):
  try:
    #remove case 
    base_dict = urlparse.parse_qs(urlparam)
    qs_dict = {}
    for key in base_dict.keys():
      qs_dict[key.lower()] = base_dict[key]
    #pull the requested parameter(first element)
    value = qs_dict[qs_param.lower()][0]
    #print urlparse.parse_qs(urlparam).keys()
    return str(value.replace('"','')).strip()
  except(KeyError):
    return ''


#use sequencing to get discoveries and the flow used for each

def get_discoveries(footprint, flowactionlist):
  for visit in sorted(footprint.keys()):
    search_action = 'Unknown'
    recordid = 'NULL'
    for sequence in sorted(footprint[visit].keys()):
      for event in sorted(footprint[visit][sequence].keys()):
        #parse out url param and the action 
        urlparam = footprint[visit][sequence][event][1]
        action = footprint[visit][sequence][event][0]
        
        #add the alerts flow 
        if action == 'ViewAncestorAlerts' and get_qs(urlparam, 'MatchesPrimaryKey') <> '0':
          search_action = 'AncestorAlert'
        #loop through other flows
        for flow in flowactionlist:    
          if action.lower().endswith(flow.lower()):
            if get_qs(urlparam, 'IsSuggested') == '1': 
              suggested = 'Suggested ' 
            else: 
              suggested = ''
            search_action = suggested + flow
            search_action = search_action.strip()
        #Get record and image views and extract the recordid 
        for view_action in ['ImageView', 'RecordView', 'RecordImageView']: 
          if action.endswith(view_action) or action.startswith(view_action):
            recordid = get_qs(urlparam, 'UniqueId')
        #print "Record ID: ", sequence, action, recordid
        #print out the action with the last used flow
        #print "key, action", str(sequence), action, get_download(urlparam)
        # Saved Record
        if action == 'SaveRecordTag':
          print '\t'.join([str(visit), str(sequence),  "Saved Record " + get_qs(urlparam, 'tag'), search_action, recordid, get_qs(urlparam, 'UniqueID')]) 
        # Tree Attach
        if action == 'PersonsMerge':
          print '\t'.join([str(visit), str(sequence), "Tree Attach", search_action, recordid, get_qs(urlparam, 'UniqueID')]) 
        # Download 
        if action.startswith('RecordImageView') and get_qs(urlparam, 'download') == '1':
          print '\t'.join([str(visit), str(sequence), "Record Download", search_action, recordid, get_qs(urlparam, 'UniqueID')])
        # Print a record
        if action == 'RecordPrint':
          print '\t'.join([str(visit), str(sequence), "Record Print", search_action, recordid, get_qs(urlparam, 'UniqueID')])     


def main(): 
  timestart = time.time()
  
  #import the data
  open_file = open(sys.argv[1])
  footprint = create_nested_dict(open_file)

  resultactionlist = []
  for line in open('action_list.txt', 'rU'):
    line = line.strip()
    #print line
    resultactionlist.append(str(line))
  #print resultactionlist

  #get any discoveries and their source
  print '\t'.join(["Visit", "Sequence", "DiscoveryType", "DiscoverySource", "RecordId", "RecordIdAction"])
  get_discoveries(footprint, resultactionlist)
  print footprint

  timeend = time.time()
  print "total time: ", timeend - timestart
if __name__ == '__main__':
  main()











