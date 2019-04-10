'''
OVERANKEDPY V. 0.1.0

FEATURES :
- Retrieve player stats
- Store player stats in a JSON File
- Plot SR Progression

TODO : 
'''


from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
import datetime
import os
import json

json_directory = 'Players stats'

def getrank(region, platform, username):
    #Get Time
    now = datetime.datetime.now()
    now_var = ('%s_%s_%s_%s_%s_%s' % (now.year, now.month, now.day, now.hour, now.minute, now.second))

    #Get Data
    try:
        url = "https://playoverwatch.com/{}/career/{}/{}".format(region, platform, username)
        player_stats = {}
        page = urlopen(url)
        soup = BeautifulSoup(page, 'html.parser')
    except:
        print("Wrong region, platform or username, try again :)")

    try:
        sr = int(soup.find('div', attrs={'class': "u-align-center h5"}).text.strip())

        games_played = soup.find('tr', attrs={'data-stat-id' : "0x0860000000000385"}).text.strip()
        games_played = int(re.search(r'\d+',games_played).group())

        games_won = soup.findAll('tr', attrs={'data-stat-id' : "0x08600000000003F5"})[1].text.strip() #[1] because there is the quickplay wins at [0]
        games_won = int(re.search(r'\d+',games_won).group())

        games_lost = soup.find('tr', attrs={'data-stat-id' : "0x086000000000042E"}).text.strip()
        games_lost = int(re.search(r'\d+',games_lost).group())

        games_tied = games_played - games_won - games_lost
        win_rate = round(games_won/games_played*100, 1)

        '''print('Player : ', username)
        print('Time of update : ', now_var)
        print('SR : ', sr)
        print('Win/Draw/Lose : %i/%i/%i' % (games_won,games_tied,games_lost))
        print('Win Rate : ' + str(win_rate) + '%')'''

        player_stats = {'username' : username, 'stats' : [{'games_played' : games_played, 'time_of_data' : now_var, 'sr' : sr, 'win_rate' : win_rate,
                            'games_won' : games_won, 'games_lost' : games_lost, 'games_tied' : games_tied}]}
                            
        return(player_stats)

    except:
        print("I couldn't find anything... Is your profile public ?")
        return({})

    


def stats2xml(player_stats, username):
    if os.path.exists(json_directory) and player_stats != {}:
        json_name = json_directory + (r"\player_stats_" + username + ".json")

        #Check if XML file exists or not. If yes, it will update it.
        if os.path.isfile(json_name):
            #print("JSON File of %s already exists, updating it..." % username)
            json1_file = open(json_name, 'r')
            json1_str = json1_file.read()
            old_dict = json.loads(json1_str)
            json1_file.close()
            new_dict = {}

            current_stats = len(old_dict['stats'])-1

            games_played_old = int(old_dict['stats'][current_stats]['games_played'])
            games_played = player_stats['stats'][0]['games_played']

            #Check if the player has played 1 ranked game or more since the last time. If yes, add the new data. If not, update the time of update.
            if games_played == games_played_old:
                #print("Updating the time of update...")
                now = datetime.datetime.now()
                now_var = ('%s_%s_%s_%s_%s_%s' % (now.year, now.month, now.day, now.hour, now.minute, now.second))
                old_dict['stats'][current_stats]['time_of_data'] = now_var
                new_dict = old_dict
                with open(json_name, 'w') as jsonfile:
                    json.dump(new_dict, jsonfile, indent=4)
                #print("JSON File '" + json_name + "' updated")

            else:
                #print("Adding the new data....")
                new_stat = player_stats['stats'][0]
                #print(new_stat)
                with open(json_name, 'r') as fp:
                    information = json.load(fp)
                information['stats'].append(new_stat)
                with open(json_name, 'w') as fp:
                    json.dump(information, fp, indent=4)

        else: #Create the JSON File
            print("First time getting %s stats, creating JSON File..." % username)
            with open(json_name, 'w') as jsonfile:
                    json.dump(player_stats, jsonfile, indent=4)
            print("JSON File '" + json_name + "' created")
    else:
        print("Directory of JSON Files does not exist or the profile is private")

