from prefect import flow, task
from prefect.artifacts import create_table_artifact
from chessdotcom import get_player_stats, get_leaderboards, Client
import time
import pprint
printer = pprint.PrettyPrinter()
      
@task
def get_player_statistics(username):
    Client.request_config["headers"]["User-Agent"] = (
        "My Chess Application "
        "Tess"
    )
    player_statistics = get_player_stats(username).json
    player_statistics_structured = {
        'Username': username,
        'Rating': player_statistics['stats']['chess_rapid']['last']['rating'],
        'Win': player_statistics['stats']['chess_rapid']['record']['win'],
        'Loss': player_statistics['stats']['chess_rapid']['record']['loss'],
        'Draw': player_statistics['stats']['chess_rapid']['record']['draw']
    }
    return player_statistics_structured

@task
def get_leaderboard(sleep: int = 15):
    time.sleep(sleep)
    all_leaderboard_data = get_leaderboards().json
    categories = all_leaderboard_data['leaderboards']
    daily_leaderboards = categories['daily']
    return [i['username'] for i in daily_leaderboards[:10]]

#@flow decorator turns function to a flow 
@flow(log_prints=True)
def chess_flow(username:str='tess245'):
    chess_table = []
    my_stats = get_player_statistics(username)
    my_stats['Score Difference'] = 0
    chess_table.append(my_stats)

    for username in get_leaderboard():
        top_player_stats = get_player_statistics(username)
        top_player_stats['Score Difference'] = top_player_stats['Rating'] - my_stats['Rating'] 
        chess_table.append(top_player_stats)
    
    create_table_artifact(
        key='chess-comparison',
        table=chess_table,
        description= "## My Chess Report"
    )

if __name__ == "__main__":
    chess_flow()
