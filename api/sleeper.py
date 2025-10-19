import requests
import pandas as pd
import os
import sys

sys.path.append("..")
from utils import get_project_root

class Sleeper:
    def __init__(self):
        self.base_url = "https://api.sleeper.app/v1"

    def daily_update(self):
        response = requests.get(f"{self.base_url}/players/nfl")
        df = pd.DataFrame()
        for player_id in response.json():
            player_info = response.json()[player_id]
            if(player_info.get("sport", "") != "nfl" or player_info.get("status", "") != "active"):
                continue
            
            player_data = {
                "id": player_id,
                "first_name": player_info.get("first_name", ""),
                "last_name": player_info.get("last_name", ""),
                "position": player_info.get("position", ""),
                "status": player_info.get("status", ""),
                "fantasy_data_id": player_info.get("fantasy_data_id", ""),
                "espn_id": player_info.get("espn_id", ""),
                "yahoo_id": player_info.get("yahoo_id", ""),
            }
            
            df = pd.concat([df, pd.DataFrame([player_data])], ignore_index=True)
            print(f"Dataframe now has {len(df)} elements after adding {player_data['first_name']} {player_data['last_name']}")
        # Change to project root directory and save pickle file in data folder
        os.chdir("..")
        os.makedirs("data", exist_ok=True)
        df.to_pickle("data/players.pkl")
        return df

    def get_players(self):
        os.chdir("..")
        df = pd.read_pickle("data/players.pkl")
        return df

if __name__ == "__main__":
    sleeper_api = Sleeper()
    sleeper_api.daily_update()
    # print(sleeper_api.get_players())