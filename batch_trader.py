import sys
import urllib
import urllib2
import xml.etree.ElementTree as ET

test_league_id = 67486
franchise_id = sys.argv[1]
password = sys.argv[2]

params = urllib.urlencode({'L': test_league_id, 'FRANCHISE_ID': franchise_id, 'PASSWORD': password, 'XML': 1})
url = "http://football21.myfantasyleague.com/2014/login?%s" % params

f = urllib2.urlopen(url)
data = ET.fromstring(f.read())

print(data.attrib)

