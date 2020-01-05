# This script will get your ratings and number of plays for any games played or game entries modified on bgg in 2019 for the provided username

# For this to work you need to install https://lcosmin.github.io/boardgamegeek/index.html
# You can do so with pip install boardgamegeek2
# I used version 1.0.0
import argparse
import csv
import datetime
from boardgamegeek import BGGClient

# argument parsing and variable setup
parser = argparse.ArgumentParser(description='Search parameters for Board Game Geek.')
parser.add_argument('-u', '--username', required=True, type=str, dest='user_name',
                    help='The BGG user name to use when querying collections and plays.')
parser.add_argument('-s', '--startdate', required=True, type=datetime.date.fromisoformat, dest='start_date',
                    help='The start date for searching BGG records (inclusively) in format YYYY-MM-DD.')
parser.add_argument('-e', '--enddate', required=True, type=datetime.date.fromisoformat, dest='end_date',
                    help='The end date for searching BGG records (inclusively) in format YYYY-MM-DD.')

args = parser.parse_args()
user_name = args.user_name
start_date = args.start_date
end_date = args.end_date
output_file_name = user_name + '_' + start_date.strftime('%Y%m%d') + '_' + end_date.strftime('%Y%m%d') + ".csv"

bgg = BGGClient()

# Used to organize the data in a dict
class GameInfo:
    name = None
    num_plays = 0
    num_plays_in_search = 0
    rating = None

    # Checking for None is not ideal, but it can happen from the BGG API
    def __init__(self, name, rating = None, num_plays = 0, num_plays_in_search = 0):
        self.name = name
        self.rating = rating
        self.num_plays = num_plays
        self.num_plays_in_search = num_plays_in_search

    def _compareName(self, other):
        if self.name is None:
            if other.name is None:
                return False
            else:
                return True
        elif other.name is None:
            return False
        return self.name < other.name

    def __lt__(self, other):
        if self.rating is None:
            if other.rating is not None:
                return True
            else:
                return self._compareName(other)
        elif other.rating is None:
            return False

        if self.rating == other.rating:
            return self.name < other.name
        return self.rating < other.rating
        

collection_in_search = {}

# Start by grabbing the sessions. By putting it in the dict from now, we can fill in the total number of plays from the collection later
# instead of fully filling it out and pruning the dictionary.
for play in bgg.plays(name=user_name, min_date=start_date, max_date=end_date):
    if play.game_id in collection_in_search:
        game_info = collection_in_search[play.game_id]
        game_info.num_plays_in_search = play.quantity + game_info.num_plays_in_search
    else:
        collection_in_search[play.game_id] = GameInfo(play.game_name, num_plays_in_search = play.quantity)

collection_items = bgg.collection(user_name=user_name, rated=True).items
for item in collection_items:
    last_modified = datetime.datetime.strptime(item.last_modified, '%Y-%m-%d %H:%M:%S').date()

    # We played it within the specified time frame if it's already in the set
    if item.id in collection_in_search:
        game_info = collection_in_search[item.id]
        game_info.num_plays = item.numplays
        game_info.rating = item.rating
    elif start_date <= last_modified <= end_date:
        collection_in_search[item.id] = GameInfo(item.name, rating = item.rating, num_plays = item.numplays, num_plays_in_search = 0)

# Now that we have all of our information, write it to a csv
with open(output_file_name, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Name", "Rating", "Plays this year", "Total plays"])
    for gameInfo in sorted(collection_in_search.values(), reverse = True):
        rating_string = "N/A"
        if gameInfo.rating is not None:
            rating_string = str(gameInfo.rating)
        
        name_string = "UNSET GAME NAME"
        if gameInfo.name is not None:
            name_string = gameInfo.name
        writer.writerow([name_string, rating_string, gameInfo.num_plays_in_search, gameInfo.num_plays])
