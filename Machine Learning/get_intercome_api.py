

import requests
import json

#need and App ID and API Key as username and password for API basic authentication

# My User Id:  5486121D1968F16BB60037F3

app_id = 's7iv7tz0'
api_key = '94d1ff4cd663f17bb0be4e5093d14802f0894bdf'

headers_dict = {}


headers_dict['accept'] = 'application/json'
headers_dict['content-type'] = 'application/json'
headers_dict['auth'] = 'basic'


page = 1

while page <= 200:
  
  urlstring = 'https://api.intercom.io/conversations?per_page=30&page=' + str(page)
  #print urlstring
  
  response = requests.get(urlstring, headers = headers_dict, auth=(app_id, api_key))
  
  #print response.headers
  
  #print response.url
  #print response.text
  
  conversations = json.loads(response.text)
  
  #outfile = open('test_conversations.txt', 'w')
  
  #print conversations

  # output the 
  for conversation in conversations['conversations']:
    textbody = conversation['conversation_message']['body'].encode('ascii', 'ignore')
    textbody2 = textbody.strip().replace('\n', '').replace('<\p>', ' ').replace('</p>', ' ').replace('<p>', '')
    user = conversation['conversation_message']['author']['id'].upper()
    usertype = conversation['conversation_message']['author']['type']
    created_at = str(conversation['created_at'])
    #print conversation
    #print page
    print '\t'.join([user, usertype, created_at, textbody2])
    #outfile.write('\t'.join([user, usertype, textbody2]))
    #outfile.write('\n')
    
  page += 1


'''
import requests

# Make a GET request here and assign the result to kittens:
kittens = requests.get('http://placekitten.com/')

print kittens.text[559:1000]
'''

