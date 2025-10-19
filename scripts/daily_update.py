import sys
sys.path.append("..")

from api import sleeper

sleeper_api = sleeper.Sleeper()
sleeper_api.daily_update()