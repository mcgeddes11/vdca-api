import os
# API key to check requests against
VALID_API_KEY = os.getenv("API_KEY")

# Local path for our database
DATABASE_PATH = os.getenv("DATABASE_PATH")
LOGFILE_PATH = os.getenv("LOGFILE_PATH")
DATABASE_URL = "sqlite:///{}".format(DATABASE_PATH)

# Club ID as defined in CricketStatz for VDCA
CRICKETSTATZ_CLUB_ID = 23365

# Base API URL for calling into CricketStatz database
CRICKETSTATZ_API_URL = "https://www2.cricketstatz.com/ss/"

# These values come from the CriketStatz report pages and correspond to the type of report we are running
BATTING_STATS_REPORT_MODE = 4
BOWLING_STATS_REPORT_MODE = 5
CATCHING_STATS_REPORT_MODE = 18
RUNOUT_STATS_REPORT_MODE = 46
