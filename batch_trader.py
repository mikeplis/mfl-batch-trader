import sys
import urllib
import urllib2
import xml.etree.ElementTree as ET

test_league_id = '67486'
franchise_id = '0001'
password = sys.argv[1]

params = urllib.urlencode({'L': test_league_id, 'FRANCHISE_ID': franchise_id, 'PASSWORD': password, 'XML': 1})
url = "http://football19.myfantasyleague.com/2014/login?%s" % params

f = urllib2.urlopen(url)
data = ET.fromstring(f.read())

user_id = data.attrib['session_id']
print(user_id)

opener = urllib2.build_opener()
opener.addheaders.append(('Cookie', 'USER_ID=%s' % user_id))
params = urllib.urlencode({'OFFEREDTO': '0002', 'WILL_GIVE_UP': 9823, 'WILL_RECEIVE': 10261, 'TYPE': 'tradeProposal', 'L': test_league_id})

url = 'http://football19.myfantasyleague.com/2014/import?%s' % params
req = opener.open(url)





