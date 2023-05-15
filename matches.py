"""Collect matches from puuids
"""

import pickle
import shelve
from cassiopeia import Patch
from riotwatcher import LolWatcher, ApiError
from config import RIOT_API_KEY


lol_watcher = LolWatcher(RIOT_API_KEY)
match = lol_watcher.match
counter = 0

# API params
region = 'NA1'
count = 100
queue = 420              # queue id of 5v5 Ranked Solo games (Summoner's Rift)
patch = Patch.from_str('13.9', 'NA')
start_time = patch.start.int_timestamp
end_time = 1684096523    # 5/14/2023


with open('data/puuids.pickle', 'rb') as f:
    ids = pickle.load(f)


db = shelve.open('data/matches.db', flag='c', writeback=True)

for puuid in ids:
    try:
        match_list = match.matchlist_by_puuid(region=region, puuid=puuid,
                                              count=count, queue=queue,
                                              start_time=start_time, end_time=end_time)

        for match_id in match_list:
            if match_id not in db:
                m = match.by_id(region=region, match_id=match_id)
                participants = m['info']['participants']
                match_details = []

                if participants:
                    for p in m['info']['participants']:
                        match_details.append(p['championName'])
                        match_details.append(p['teamPosition'])

                    match_details.append(m['info']['teams'][0]['win'])
                    db[match_id] = match_details
                    counter += 1

                    # offload every 5000 matches
                    if counter % 5000 == 0:
                        db.sync()
                        print('Number of matches saved: ', counter)

    except ApiError as err:
        if err.response.status_code == 404:
            print(err.response)
        else:
            db.close()
            raise


db.close()
print('Total number of matches saved: ', counter)