


import json
import time

treesui = open('dump22.txt')

counter = 0

timestart = time.time()

f = open('ucdm_counts.txt', 'w')

dict_trees = {}
dict_summary = {}
for line in treesui:
    
    '''
    counter += 1
    if counter >= 100000:
        break
    '''
    
    splitline = line.split('\t')
  
    dict_trees = json.loads(splitline[0])


    event = dict_trees["Event"]
    timestamp = dict_trees["TimeStamp"].replace('T', ' ').replace('Z','')
    hour = int(timestamp.split(' ')[1][:2])
    day = timestamp.split(' ')[0]   
    #print hour, day, timestamp
    
    
    if hour >= 6 and day == '2014-06-23':
        continue
    if hour < 6 and day == '2014-06-22':
        continue
    if event != 'PersonOverview':
        continue
    

    userid = dict_trees["Properties"]["UserId"]
    
    try:  
        dict_summary[userid] = dict_summary[userid] + 1
    except(KeyError):
        dict_summary[userid] = 1
    
# Summary of Data: 
for key in dict_summary.keys():
    print >> f, '\t'.join([str(key), str(dict_summary[key])])


timeend = time.time()
print "total time: ", timeend - timestart


#print dict_tweets.keys()


#print dict_tweets["text"]



#response = urllib.urlopen("http://search.twitter.com/search.json?q=microsoft")
#pyresponse = json.load(response)
##print type (pyresponse)

##print pyresponse.keys()
##print type(pyresponse["results"])

#results = pyresponse["results"] 
##print type(results[0])
##print results[0].keys()
