import requests
import pandas as pd
import os
import sys

sys.path.append("..")
from utils import get_project_root

class Sleeper:
    def __init__(self):
        self.base_url = "https://api.sleeper.app/v1"

    def update_players(self):
        response = requests.get(f"{self.base_url}/players/nfl")
        df = pd.DataFrame()
        for player_id in response.json():
            player_info = response.json()[player_id]
            if(player_info["sport"] == "nfl"):
                player_data = {
                    "id": player_id,
                    "first_name": player_info["first_name"],
                    "last_name": player_info["last_name"],
                    "position": player_info["position"],
                    "status": player_info["status"],
                    "fantasy_data_id": player_info["fantasy_data_id"],
                    "espn_id": player_info["espn_id"],
                    "yahoo_id": player_info["yahoo_id"],
                }
                df = df.append(player_data, ignore_index=True)
                break
            
        # Change to project root directory and save pickle file in data folder
        os.chdir(get_project_root())
        os.makedirs("data", exist_ok=True)
        df.to_pickle("data/players.pkl")
        return df

    def get_players(self):
        print(get_project_root())
        print(os.getcwd())
        os.chdir(get_project_root())
        print(os.getcwd())
        # df = pd.read_pickle("data/players.pkl")
        # return df

if __name__ == "__main__":
    sleeper = Sleeper()
    # sleeper.update_players()
    print(sleeper.get_players())