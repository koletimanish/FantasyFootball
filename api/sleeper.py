import requests
import pandas as pd
import os
import sys
from datetime import datetime

sys.path.append("..")
from utils import get_project_root

class Sleeper:
    def __init__(self):
        self.base_url = "https://api.sleeper.app/v1"
        self.current_year = datetime.now().year

    def daily_update(self):
        response = requests.get(f"{self.base_url}/players/nfl")
        df = pd.DataFrame()
        total_players = len(response.json())
        count = 0
        for player_id in response.json():
            count += 1
            print(f"Processing player {player_id} - ({count} of {total_players})")
            player_info = response.json()[player_id]
            sport = player_info.get("sport") or ""
            status = player_info.get("status") or ""
            if(sport.lower() != "nfl" or status.lower() != "active"):
                print(f"Skipping player {player_id} ({player_info.get('first_name', '')} {player_info.get('last_name', '')}) because their sport is {sport} or status is {status}")
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
        os.makedirs("data", exist_ok=True)
        df.to_pickle("data/players.pkl")
        return df

    def get_players(self):
        df = pd.read_pickle("data/players.pkl")
        return df

    def get_user_id(self, username):
        # Check if users.pkl exists
        if(not os.path.exists(f"data/users/users.pkl")):
            user_df = pd.DataFrame()
        else:
            user_df = pd.read_pickle(f"data/users/users.pkl")
        
        user_id = None
        if(user_df.empty or user_df[user_df["username"] == username].empty):
            print(f"User {username} does not exist, creating new entry")
            response = requests.get(f"{self.base_url}/user/{username}")
            user_id = response.json().get("user_id", None)
            user_df = pd.concat([user_df, pd.DataFrame([{"id": user_id, "username": username}])], ignore_index=True)
            os.makedirs("data/users", exist_ok=True)
            user_df.to_pickle(f"data/users/users.pkl")
            print(f"Saved user {username} to data/users/users.pkl")
        else:
            print(f"User {username} already exists")
            user_id = user_df[user_df["username"] == username]["id"].iloc[0]
        
        return user_id
    
    def get_user_league_info(self, user_id):
        print(f"Getting user {user_id} league info")
        
        df = None
        if(not os.path.exists(f"data/users/user_{user_id}_leagues.pkl")):
            print(f"User {user_id} league info not found, creating new dataframe")
            df = pd.DataFrame()
        else:
            df = pd.read_pickle(f"data/users/user_{user_id}_leagues.pkl")
        
        if(df is not None and not df.empty):
            return df[df["user_id"] == user_id]

        response = requests.get(f"{self.base_url}/user/{user_id}/leagues/nfl/{self.current_year}")
        user_info = response.json()
        for info in user_info:
            info_data = {
                "user_id": user_id,
                "league_id": info.get("league_id", ""),
                "draft_id": info.get("draft_id", ""),
                "name": info.get("name", ""),
            }
            print(info_data)
            df = pd.concat([df, pd.DataFrame([info_data])], ignore_index=True)

        os.makedirs("data/users", exist_ok=True)
        df.to_pickle(f"data/users/user_{user_id}_leagues.pkl")
        print(f"Saved user {user_id} league info to data/users/user_{user_id}_leagues.pkl")
        return df[df["user_id"] == user_id]

    def get_league_roster(self, league_id):
        print(f"Getting league {league_id} roster")

        df = None
        if(not os.path.exists(f"data/leagues/league_{league_id}_roster.pkl")):
            print(f"League {league_id} roster not found, creating new dataframe")
            df = pd.DataFrame()
        else:
            df = pd.read_pickle(f"data/leagues/league_{league_id}_roster.pkl")
        
        if(df is not None and not df.empty):
            return df[df["league_id"] == league_id]
        
        response = requests.get(f"{self.base_url}/league/{league_id}/rosters")
        rosters = response.json()
        for roster in rosters:
            user_id = roster.get("owner_id", "")
            roster_data = {
                "league_id": league_id,
                "user_id": user_id,
                "roster": roster,
            }
            df = pd.concat([df, pd.DataFrame([roster_data])], ignore_index=True)
        
        os.makedirs("data/leagues", exist_ok=True)
        df.to_pickle(f"data/leagues/league_{league_id}_roster.pkl")
        print(f"Saved league {league_id} roster to data/leagues/league_{league_id}_roster.pkl")
        return df[df["league_id"] == league_id]

    def get_user_league_roster(self, user_id, league_id):
        league_rosters = self.get_league_roster(league_id)
        user_rosters = league_rosters[league_rosters["user_id"] == user_id].iloc[0]["roster"]
        user_roster_players = user_rosters["players"]
        players = self.get_players()
        player_names = []
        for player_id in user_roster_players:
            player_row = players[players["id"] == player_id]
            if not player_row.empty:
                first_name = player_row["first_name"].iloc[0]
                last_name = player_row["last_name"].iloc[0]
                player_names.append(f"{first_name} {last_name}")
            else:
                print(f"Player not found - {player_id}")
        return player_names
    
if __name__ == "__main__":
    sleeper_api = Sleeper()
    os.chdir("..")
    # sleeper_api.daily_update()
    # players = sleeper_api.get_players()
    user_id = sleeper_api.get_user_id("Moneyish27")
    leagues = sleeper_api.get_user_league_info(user_id)
    for index, league in leagues.iterrows():
        print(f"Processing league {index + 1} of {len(leagues)}")
        league_id = league["league_id"]
        player_names = sleeper_api.get_user_league_roster(user_id, league_id)
        print(player_names)
        print("--------------------------------")