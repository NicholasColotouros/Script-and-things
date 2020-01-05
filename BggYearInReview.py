# This script will get your ratings and number of plays for any games played or game entries modified on bgg in 2019 for the provided username

# For this to work you need to install https://lcosmin.github.io/boardgamegeek/index.html
# You can do so with pip install boardgamegeek2
# I used version 1.0.0
import csv
import datetime
from boardgamegeek import BGGClient

bgg = BGGClient()

# search parameters. Ideally these come from the command line
user_name = "USB Connector"
start_date = datetime.date(2019, 1, 1)
end_date = datetime.date(2019, 12, 31)
output_file_name = "topkek.csv"

# Used to organize the data in a dict
class GameInfo:
    name = None
    num_plays = 0
    num_plays_in_search = 0
    rating = None

    def __init__(self, name, rating = None, num_plays = 0, num_plays_in_search = 0):
        self.name = name
        self.rating = rating
        self.num_plays = num_plays
        self.num_plays_in_search = num_plays_in_search

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
        game_info.rating = item.rating
        game_info.num_plays = item.numplays
    elif start_date <= last_modified <= end_date:
        collection_in_search[item.id] = GameInfo(item.name, rating = item.rating, num_plays = item.numplays, num_plays_in_search = 0)

# Now that we have all of our information, write it to a csv
with open(output_file_name, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Name", "Rating", "Plays this year", "Total plays"])
    for gameInfo in collection_in_search.values():
        writer.writerow([gameInfo.name, gameInfo.rating, gameInfo.num_plays_in_search, gameInfo.num_plays])
