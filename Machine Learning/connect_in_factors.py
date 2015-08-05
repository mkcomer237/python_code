
import json
import string as st
import time
import string

#Parse out and count all of the items in the call and response
#dictionary with the counts of events and gender, name, etc 
#then load into pandas to deal with better 


def count_family(request_parameters):
	try:
		family = request_parameters['Family']
	except(KeyError):
		family = []
	counter = 0
	for relative in family:
		counter += 1
	return counter


def get_states():

	stateslist = []
	statesdict = {}
	stateslistabv = []
	statesdictabv = {}


	statesraw = open('us_states.txt', 'r')

	for line in statesraw:
		splitline = line.split('\t')

		state = splitline[0].lower()
		stateabv = splitline[1].lower()
		region = splitline[2].lower()
		subregion = splitline[3].lower().strip()

		stateslist.append(state)
		stateslistabv.append(stateabv)

		statesdict[state] = [region, subregion]
		statesdictabv[stateabv] = [region, subregion]

	return [stateslist, stateslistabv, statesdict, statesdictabv]


def get_birthplace(request_parameters, state_objects):

	try:
		for event in request_parameters['Events']:
			fullplace = ''
			if event['t'] == 'Birth':
				#print 'has birth:  ', event
				fullplace = event['p'].strip().lower()
				fullplace = filter(lambda x: x in string.printable, fullplace) #gets rid of unicode
	except(KeyError):
		fullplace = '' 

	stateslist = state_objects[0]
	statesdict = state_objects[2]

	birthstate = 'none'
	if fullplace != '':
		for state in stateslist:
			if state.strip() in fullplace:
				birthstate = state
				break
			else:
				birthstate = 'none'

	#lookup region and subregion 
	try: birth_regions = statesdict[birthstate]
	except(KeyError): birth_regions = ['none', 'none']

	if fullplace != '' and birthstate == 'none':
		birthstate = 'non-us'
		birth_regions = ['non-us','non-us']

	return [birthstate] + birth_regions


def get_bday(request_parameters):

	fulldate = '0'
	try:
		for event in request_parameters['Events']:
			if event['t'] == 'Birth':
				fulldate = event['d']
	except(KeyError): 
		return 0

	fulldate_nopunct = fulldate.replace('/',' ').replace('.', ' ')

	year = 0
	splitdate = fulldate_nopunct.split(' ')
	for piece in splitdate:
		#print piece, len(piece)
		if len(piece) == 4:
			try:
				year = int(piece)
			except(ValueError):
				year = 0

	#print fulldate, year		
	return year



def get_events(request_parameters):
	event_dict = {}
	eventlist = ['Birth', 'Residence', 'Death', 'Marriage', 'Burial', 'Arrival', 'Military', 'Occupation', 'Divorce']
	
	for event in eventlist:
		event_dict[event] = 0

	event_sum = 0

	try:
		for event in request_parameters['Events']:
			ename = event['t']
			event_sum += 1
			try:
				event_dict[ename] = event_dict[ename] + 1
			except(KeyError):
				pass
	except(KeyError):
		return [event_dict, 0]

	return [event_dict, event_sum]


def get_outcome(response, mscutoff):
	matchnumber  = 0
	if response == 'NA':
		return 'nothing'
	for cluster in response:
		clusterms = cluster['MatchScore']
		if clusterms < mscutoff:
			continue
		matchnumber += 1
	if matchnumber > 0:
		success = 'Yes'
	else: 
		success = 'No'
	return success


def get_gender(request_parameters):
	gender = 'f'
	try:
		for gen in request_parameters['Genders']:
			gender = gen['g']
	except(KeyError):
		gender = 'f'
	return gender


def get_names(request_parameters):
	
	try:
		name = request_parameters['Names'][0]
	except(KeyError):
		return['', '', '']

	try:
		given_name = name['g'].strip().replace('\\','').replace('\"','').decode()
	except(KeyError, UnicodeEncodeError):
		given_name = ''

	try:
		surname = name['s'].strip().replace('\\','').replace('\"','').decode()
	except(KeyError, UnicodeEncodeError):
		surname = ''

	if len(given_name) == 1 or '?' in given_name:
		given_name = ''

	if len(surname) == 1 or '?' in surname:
		surname = ''

	splitname = given_name.split(' ')

	first = splitname[0]
	try:
		middle = splitname[1]
	except(IndexError):
		middle = ''
	last = surname

	return [first, middle, last]


def clean_time(timestamp): 
	cleantime =  timestamp[:19].replace('T', ' ')

	#print cleantime
	return cleantime

def get_lists(fp, mscutoff):

	rawfile = open(fp)

	counter = 0 
	outdict = {}
	eventdict = {}
	outlist = []
	state_objects = get_states()
	#print state_objects

	target = open('dataset_full_mobile.txt', 'w')
	target.write('\t'.join(['gid', 'timestamp', 'personaid', 'treeid', 'response', 'gender', 'relatives', 'birthyear', 'namecount', 'first', 'middle', 'last', 'eventsum', 'birth', 'residence', 'death', 'marriage', 'burial', 'arrival', 'military', 'occupation', 'divorce', 'birthstate', 'birthregion', 'birthsubregion' ]))
	target.write('\n')

	for line in rawfile:

		#print line
		if line.strip() == 'json':
			continue 

		connectdict = json.loads(line)

		#include only mobile 
		if connectdict['Tracking']['ClientPath'] != 'Unknown:AncestryApiTrees':
			continue 

		try:
			request_parameters = connectdict['Data']['Parameters']['request']['Value']['Container']['Persons'][0]
		except:
			#print connectdict['Data']['Parameters']['request']['Value']
			continue 
		try:
			response = connectdict['Data']['Return']['Value']['Matches']
		except(KeyError):
			response = 'NA'
		

		timestamp = connectdict['TimeStamp']
		cleantime = clean_time(timestamp)
		requestgid = request_parameters['gid']['v']
		personaid = requestgid.split(':')[0]
		treeid = requestgid.split(':')[2]
		success = get_outcome(response, mscutoff)
		gender = get_gender(request_parameters)
		events_2 = get_events(request_parameters)
		events = events_2[0]
		eventsum = events_2[1]
		fam_members = count_family(request_parameters)
		birthday = get_bday(request_parameters)
		names = get_names(request_parameters)
		birthplace = get_birthplace(request_parameters, state_objects)

		namecount = 0
		for name in names:
			if name != '': namecount += 1
		#print 'Namecount is: ', namecount
		if names[0] != '': first = 1 
		else: first = 0

		if names[1] != '': middle = 1 
		else: middle = 0

		if names[2] != '': last = 1 
		else: last = 0


		for key in events:
			try:
				eventdict[key] = eventdict[key] + events[key]
			except(KeyError):
				eventdict[key] = events[key]


		outdict[requestgid] = [success, gender, fam_members, birthday, events, namecount, first, middle, last, eventsum]


		#switch to using the list instead of the dictionary to allow duplicate gids - then dedup accross everything but fam_members

		eventlist = []
		for event in ['Birth', 'Residence', 'Death', 'Marriage', 'Burial', 'Arrival', 'Military', 'Occupation', 'Divorce']:
			eventlist.append(str(events[event]))

		row = [requestgid, cleantime, personaid, treeid, success, gender, fam_members, birthday, namecount, first, middle, last, eventsum] + eventlist + birthplace

		rowstring = []
		for el in row:
			rowstring.append(str(el))


		target.write('\t'.join(rowstring))
		target.write('\n')
		counter += 1

		if counter >= 1000:
			break


	#print "final eventdict is ", eventdict 
	#for eventkey in eventdict:
	#	print '\t'.join([eventkey, str(eventdict[eventkey])])
	#return outlist


def print_csv(printlist):

	target = open('dataset_full_mobile.txt', 'w')

	target.write('\t'.join(['gid', 'response', 'gender', 'relatives', 'birthyear', 'namecount', 'first', 'middle', 'last', 'eventsum', 'birth', 'residence', 'death', 'marriage', 'burial', 'arrival', 'military', 'occupation', 'divorce']))
	target.write('\n')

	for row in printlist:

		'''
		outlist = []
		outlist.append(key)
		outlist.append(outdict[key][0])
		outlist.append(outdict[key][1])
		outlist.append(str(outdict[key][2]))
		outlist.append(str(outdict[key][3]))
		outlist.append(str(outdict[key][5]))
		outlist.append(str(outdict[key][6]))
		outlist.append(str(outdict[key][7]))			
		outlist.append(str(outdict[key][8]))
		outlist.append(str(outdict[key][9]))
		'''

		rowstring = []
		for el in row:
			rowstring.append(str(el))


		target.write('\t'.join(rowstring))
		target.write('\n')



def main(): 

	timestart = time.time() 

	fp = 'outfull_2_20_2_26.txt'

	outlist = get_lists(fp, 100)

	#for key in outdict:
	#	print key, outdict[key]

	#print_csv(outlist)

	timeend = time.time()
	print "Time taken: ", timeend - timestart

if __name__ == '__main__':
  main()



