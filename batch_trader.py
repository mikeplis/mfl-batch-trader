import sys
import urllib
import urllib2
import xml.etree.ElementTree as ET
import json

class Trader:

    def __init__(self, league_id, _franchise_id, password):
        def prepend_zeros(input_):
            string = str(input_)
            length = len(string)
            if length >= 4:
                return string
            else:
                num_of_zeros = 4 - length
                return ''.join(('0' * num_of_zeros, string))
        franchise_id = prepend_zeros(_franchise_id)
        params = urllib.urlencode({
            'L': league_id,
            'FRANCHISE_ID': franchise_id,
            'PASSWORD': password,
            'XML': 1})
        url = "http://football19.myfantasyleague.com/2014/login?{}".format(params)
        resp = urllib2.urlopen(url)
        user_id = ET.fromstring(resp.read()).attrib['session_id']
        opener = urllib2.build_opener()
        opener.addheaders.append(('Cookie', 'USER_ID={}'.format(user_id)))

        self.league_id = league_id
        self.franchise_id = franchise_id
        self.opener = opener

    def batch(self, offers, dry_run=False):
        """Send offers to all other owners.

        Args:
            offers (list of dict): List of dicts containing offers to make.
                Each offer must have the following fields:
                    will_give_up (list of int): List of player ID's to trade away
                    picks (list of dict): List of picks to trade for.
                        Each pick must have the following fields:
                            year (int)
                            round (int)
            dry_run (bool): If True, won't actually send offers, will only print out offers to be made.
                Useful for double-checking that input parameters are correct.

        Example:
            >>> offers = [
                {
                    'will_give_up': [123, 456],
                    'picks': [
                        {
                            'year': 2015,
                            'round': 1
                        }
                    ]
                },
                {
                    'will_give_up': [789],
                    'picks': [
                        {
                            'year': 2015,
                            'round': 1
                        },
                        {
                            'year': 2016,
                            'round': 2
                        }
                    ]
                },
            ]
            >>> batch(offers)
            This will send two offers to every other owner. One trade offering
            players 123 and 456 in exchange for a 2015 1st, and a second trade
            offering player 789 in exchange for a 2015 1st and a 2016 2nd
        """
        req = 'http://football21.myfantasyleague.com/2014/export?TYPE=futureDraftPicks&L={}&W=&JSON=1'.format(self.league_id)
        resp = urllib2.urlopen(req)
        draft_picks = json.loads(resp.read())['futureDraftPicks']['franchise']

        for offer in offers:
            will_give_up = ','.join(map(str,offer['will_give_up']))
            # TODO: make this be able to handle multiple picks
            pick_year = str(offer['picks'][0]['year'])
            pick_round = str(offer['picks'][0]['round'])
            for draft_pick in draft_picks:
                fid = draft_pick['id']
                if fid != self.franchise_id:
                    picks = draft_pick['futureDraftPick']

                    # find first pick that satisfies predicate using 'next': http://stackoverflow.com/questions/8534256/find-first-element-in-a-sequence-that-matches-a-predicate
                    target_picks = [pick for pick in picks if pick['round'] == pick_round and pick['year'] == pick_year]
                    if target_picks:
                        target_pick = target_picks[0]
                        will_receive_id = 'FP_{0}_{1}_{2}'.format(
                            target_pick['originalPickFor'],
                            target_pick['year'],
                            target_pick['round'])
                        params = urllib.urlencode({
                            'OFFEREDTO': fid,
                            'WILL_GIVE_UP': will_give_up,
                            'WILL_RECEIVE': will_receive_id,
                            'TYPE': 'tradeProposal',
                            'L': self.league_id})
                        url = 'http://football19.myfantasyleague.com/2014/import?{}'.format(params)
                        if not dry_run:
                            self.opener.open(url)
                        else:
                            print('DRY RUN: {}'.format(url))

    def revoke_all(self, dry_run=False):
        req = 'http://football21.myfantasyleague.com/2014/export?TYPE=pendingTrades&L={}&JSON=1'.format(self.league_id)
        resp = self.opener.open(req)
        # TODO: properly handle situation where this function is called by no pending trades exist
        pending_trades = json.loads(resp.read())['pendingTrades']['pendingTrade']
        for pending_trade in pending_trades:
            params = urllib.urlencode({
                'TYPE': 'tradeResponse',
                'OFFEREDTO': pending_trade['offeredto'],
                'WILL_GIVE_UP': pending_trade['will_give_up'],
                'WILL_RECEIVE': pending_trade['will_receive'],
                'RESPONSE': 'revoke',
                'OFFERINGTEAM': self.franchise_id,
                'L': self.league_id
            })
            url = 'http://football21.myfantasyleague.com/2014/import?{}'.format(params)
            if not dry_run:
                self.opener.open(url)
            else:
                print('DRY RUN: {}'.format(url))

if __name__ == "__main__":
    t = Trader('67486', '0001', sys.argv[1])
    try:
        dry_run = sys.argv[2] == 'True'
    except IndexError:
        dry_run = True
    offer = {'will_give_up': [9823, 9448], 'picks': [{'year': 2015, 'round': 1}]}
    t.batch([offer],dry_run=dry_run)

# WILL_GIVE_UP = player that user will give up; player that other owner will receive
# WILL_RECEIVE = player that user will receive; player that other owner will give up

"""
TODO

* Allow batch function to take in list of player id's and picks
** I.e. can offer one/many players in exchange for one/many picks

* Write better algorithm for choosing which pick to create a trade for
** Sort by one or many standings parameters retrieved from MFL 'standings' endpoint
** Create ability to specify a max of X number of offers; useful in larger leagues where there's a large difference in value between early and late picks in a round

* Write tests

* Better log messages
** Should display some kind of message when actually sending request, not just on dry runs
** Log messages could display actual player/team names. E.g. "Offering Larry Fitzgerald to Dave's Team in exchange for a 2015 2nd round pick originally belonging to Steve's Team"
*** Default could be print one message (e.g. "Offering <player(s)> in exchange for <pick(s)>") and could add verbose param to print out more detailed messages

"""




