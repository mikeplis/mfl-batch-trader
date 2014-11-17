import sys
import urllib
import urllib2
import xml.etree.ElementTree as ET
import json

test_league_id = '67486'
franchise_id = '0001'
will_give_up_id = '9823'
password = sys.argv[1]

params = urllib.urlencode({'L': test_league_id, 'FRANCHISE_ID': franchise_id, 'PASSWORD': password, 'XML': 1})
url = "http://football19.myfantasyleague.com/2014/login?%s" % params

f = urllib2.urlopen(url)
data = ET.fromstring(f.read())

user_id = data.attrib['session_id']

opener = urllib2.build_opener()
opener.addheaders.append(('Cookie', 'USER_ID=%s' % user_id))

pick_year = '2015'
pick_round = '1'

draft_picks_req = 'http://football21.myfantasyleague.com/2014/export?TYPE=futureDraftPicks&L=%s&W=&JSON=1' % test_league_id
draft_picks_resp = urllib2.urlopen(draft_picks_req)
dp = json.loads(draft_picks_resp.read())
draft_picks = dp['futureDraftPicks']['franchise']

for draft_pick in draft_picks:
    fid = draft_pick['id']
    if fid != franchise_id:
        will_receive_id = 'FP_{0}_{1}_{2}'.format(fid, pick_year, pick_round)
        params = urllib.urlencode({'OFFEREDTO': fid, 'WILL_GIVE_UP': will_give_up_id, 'WILL_RECEIVE': will_receive_id, 'TYPE': 'tradeProposal', 'L': test_league_id})
        url = 'http://football19.myfantasyleague.com/2014/import?%s' % params
        print(url)
        opener.open(url)

# WILL_GIVE_UP = player that user will give up; player that other owner will receive
# WILL_RECEIVE = player that user will receive; player that other owner will give up

"""
TODO
* Offer player to every other owner
** Retrieve list of other owners from MFL
** Extract all owners that aren't user
** Retrieve list of players for each owner and pick one at random
** Create trade offer
* Offer player to every other owner in exchange for a draft pick
** Retrieve list of draft picks for each owner and pick one at random
** Create trade offer
* Offer player to every other owner in exchange for specific draft pick 
** Take year and round as input
** If owner has draft pick in that year/round, create trade offer. Else, skip
"""




