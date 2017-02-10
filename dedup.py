
# coding: utf-8

# In[2]:

from bs4 import BeautifulSoup
import urllib
import requests
import re
import unicodedata
import csv
import csv
import sys
import time
import json
import random
import hashlib
import atexit
import urllib2


def LoadUserAgents(uafile):
    """
    uafile : string
        path to text file of user agents, one per line
    """
    uas = []
    with open(uafile, 'rb') as uaf:
        for ua in uaf.readlines():
            if ua:
                uas.append(ua.strip()[1:-1-1])
    random.shuffle(uas)
    return uas


def clean_name(str):
    str = strip_accents(re.sub("[–]"," ",str))
    str = strip_accents(re.sub("ÃƒÂ¤","",str))
    str = strip_accents(re.sub("[Łł]","L",str))
    return str


def strip_accents(str):
    return ''.join(c for c in unicodedata.normalize('NFD', str)
                  if unicodedata.category(c) != 'Mn')


def cleanhtml(raw_html):
    cleantext = re.sub(re.compile('<.*?>'),'', raw_html)
    return cleantext



def get_Html(query):
    # load user agents and set headers
    user_agents = LoadUserAgents("user_agents.txt")
    ua = random.choice(user_agents)  # select a random user agent
    headers = {
        "Connection" : "close",  # another way to cover tracks
        "User-Agent" : ua}
    # load the user agents, in random order
    
    proxy = {"https":"https://jsharm:BW9RThYD@23.81.249.78:29842", "https":"https://jsharm:BW9RThYD@23.106.239.231:29842", "https":"https://jsharm:BW9RThYD@ 23.81.249.191:29842"}
    address = "http://www.google.com/search?q=%s" % (urllib.quote(query))
    session = requests.Session()
    request = session.get(address, headers=headers)
#     print request
#     urlfile = urllib2.urlopen(request)
#     page = urlfile.read()
    soup = BeautifulSoup(request.text, "lxml")
#     print soup
    return soup


# convert Unicode to ASCII
def to_ascii(string):
    return string.encode('ascii', 'ignore')

def get_google_name(soup):
    
    if(len(soup.find_all("div", class_="kno-ecr-pt kno-fb-ctx _hdf"))>0):
        for college in soup.find_all("div", class_="kno-ecr-pt kno-fb-ctx _hdf"):
#             print "College Name from Google - " + college.contents[0]
            return clean_name(college.contents[0])
            break
    elif(len(soup.find_all("div", class_="_B5d"))>0):
        for college in soup.find_all("div", class_="_B5d"):
#             print("College Name from Google - "+ college.contents[0])
            return clean_name(college.contents[0])
            break
    else:
#         print(soup)
        return "Check regex"

def get_right_result_link(soup):
    # link_els = soup.select( [ "div._eFb div._mr.kno-fb-ctx span._Xbe.kno-fv a.fl", "div._mdf._ykh.kno-fb-ctx3 div._ldf a.ab_button" ] )
    # link = link_els[0] if link_els else None
    link = 'https://www.google.com' + soup.select('div._IGf a.fl')[1]['href']
    print link
    req = urllib2.Request(link)
    res = urllib2.urlopen(req)
    finalurl = res.geturl()
    return finalurl.split('/')[2]

def get_details_from_first_result(soup):
	name = soup.select('div.g h3.r a')[0].getText()
	link = soup.select('div.kv cite')[0].getText()
	if 'shiksha' in link or 'collegedunia' in link or 'careers360' in link or 'getmyuni' in link:
		link = soup.select('div.kv cite')[1].getText()
		if 'shiksha' in link or 'collegedunia' in link or 'careers360' in link or 'getmyuni' in link:
			link = soup.select('div.kv cite')[2].getText()
	return (name, link.split('/')[2])
    
def google_result(college_name, recurse=0):
#     college_name = clean_name(college_name)
    soup = get_Html(college_name)
    # print soup.prettify()
    
    googleName=get_google_name(soup)
    if googleName == "Check regex":
        googleName, link = get_details_from_first_result(soup)   # This function has NOT been defined yet.
    else:
        link = get_right_result_link(soup)

    if googleName==None or link==None:
    	if recurse==0:
    		print 'May have been blocked. Trying Again'
    		google_result(college_name, 1)
    	if recurse==1:
    		print 'Tried Again. Still Blocked. Saving and Quitting'
    		return 0

    """
    If we still don't have a result after all this while, then perhaps Google is blocking us.
    Therefore, this solution needs to be integrated with a proxy. I'll hand over 2-3 proxies for this purpose.
    Hence, it's possible to write code which'll essentially mean:
    `If can't get result using current proxy (transparent or other), then use next proxy in list.`
    """

    googleCollegeName = dict()
    googleCollegeName["googleName"] = googleName
    googleCollegeName["link"] = link
    return googleCollegeName


def google_custom_search(key, search_engine_id, search_term):
    response = urllib.urlopen('https://www.googleapis.com/customsearch/v1?' + urllib.urlencode( { 'key': key, 'cx': search_engine_id, 'q': search_term } )).read().decode('utf8')
    data = json.loads(response)
    # print response
    # print json.dumps(data, indent=4, sort_keys=True)
    results = data['items']
    first_result = results[0]

    return { 'description': to_ascii(first_result['title']), 'link': to_ascii(first_result['link']) }

def get_re_val(match, key):
    try:
        return match.group(key)
    except IndexError:
        return ''


def save_and_exit(results):
	print 'De-Dup Done. {} Duplicate Entries Removed. Saving in given file.'.format(duplicates)


	with open(output,'wb') as resultFile:
	    wr = csv.writer(resultFile)
	    for element in results:
	    	wr.writerow(element)

	print 'Saving Done. Good Day'


# In[6]:

# test function

import json

college_name="IIM Bangalore"
google_results=dict()
google_results = google_result(college_name)
print google_results
if google_results['googleName']!='Check regex':
	print 'Verified Connectivity.'

api = "AIzaSyC4EmkFHaktnLZu2vCetEiP9NrZpcOAzDQ"
csid =  "002545386949181512612:0z0ctuh97j8"
collegeName = "IIMA"
try:
    googleResult= google_custom_search(api,csid, collegeName)
    print googleResult
    print 'API Connectivity Verified'
except:
	print 'API Search failed. Check API Key and CSID.'


file_name = raw_input('Enter name of CSV with college names:')
import csv

try:
	reader = csv.DictReader(open(file_name))

	result = {}
	for row in reader:
		for column, value in row.iteritems():
			result.setdefault(column, []).append(value)

except Exception as e:
	print e

print 'Imported File as Dictionary with Keys:{}'.format(str(result.keys()))

key = raw_input('Enter name of key to De-Dup:')

output = raw_input('File to save De-Dupped Values in:')

"""
Removing this.
identifier = raw_input('ID Identifier for entries: ')
"""


ids = 0
unique_names = dict()
# not a set
unique_links = dict()


print 'Looking for any savefiles in current directory.'
try:
	with open('savefile.json') as infile:
		save_data = json.load(infile)
		unique_names = save_data['names']
		unique_links = save_data['links']
except:
	print 'No savefile found. Starting from Scratch'

values = result[key]
results = []
duplicates = 0
results.append(['Duplicate Name', 'Unique Name', 'Unique Link', 'Note'])
atexit.register(save_and_exit, (results))
for value in values:
    temp_result = {}
    result_1 = google_result(value)
    """
    if result_1 does NOT have name, then everything has failed. Serialize data structures unique_names and unique_links (json or otherwise), save to disk and exit gracefully.
    Correspondingly, before starting up, load data structures from file.
    """
    if result_1==0:
    	with open('savefile.json') as savefile:
    		json.dumps(savefile, {'links' : unique_links, 'names': unique_names})
    	print 'Current Data Saved in File. Initiating Exit.'
	    
    else:
	    name = result_1['googleName']
	    link = result_1['link']

	    (result_name, result_link, note) = (None, None, None)

	    if name in unique_names:
	        (result_name, result_link) = (name, link)
	    elif link in unique_links:
	        (result_name, result_link, note) = (unique_links[link], link, "Link match.")
	    else:
	        (result_name, result_link) = (name, link)
	        unique_names[name] = link
	        unique_names[link] = name

	    results.append([value, result_name, result_link, note])
save_and_exit(results)





