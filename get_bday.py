def get_bday(request_parameters):

	fulldate = 'None'
	try:
		for event in request_parameters['Events']:
			if event['t'] == 'Birth':
				fulldate = event['d']
	except(KeyError): 
		return fulldate

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