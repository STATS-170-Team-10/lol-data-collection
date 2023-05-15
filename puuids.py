"""Collect puuids of summoners.
"""

import pickle
from riotwatcher import LolWatcher, ApiError
from config import RIOT_API_KEY


lol_watcher = LolWatcher(RIOT_API_KEY)
league = lol_watcher.league
region = 'NA1'
queue = 'RANKED_SOLO_5x5'

puuids = []
summoners = []

summoners.extend( league.challenger_by_queue(region, queue).get('entries') )
summoners.extend( league.grandmaster_by_queue(region, queue).get('entries') )
summoners.extend( league.masters_by_queue(region, queue).get('entries') )

for summoner in summoners:
    try:
        summoner = lol_watcher.summoner.by_name(region, summoner['summonerName'])
        puuids.append(summoner['puuid'])
    except ApiError as err:
        if err.response.status_code == 404:
            print('404: Summoner not found. Skipping')
        else:
            raise


with open('data/puuids.pickle', 'wb') as f:
    # serialize list and write to file
    pickle.dump(puuids, f)

print('List saved to file.')