""" This code runs the daily update to sync our database with Cricketstatz"""

from app.data.models import BattingStats, VdcaBase, BowlingStats, FieldingStats
from app.data.database_utils import VdcaDatabase
from app.config import DATABASE_URL, CRICKETSTATZ_CLUB_ID, CRICKETSTATZ_API_URL, BATTING_STATS_REPORT_MODE, \
    BOWLING_STATS_REPORT_MODE, CATCHING_STATS_REPORT_MODE, RUNOUT_STATS_REPORT_MODE, LOGFILE_PATH
from sqlalchemy.engine import create_engine
from app.data.data_utils import get_html_from_response, get_table_from_html, get_playerid_from_url, \
    get_team_season_grade_combinations, get_teams
from app.data.utils import get_logger
from datetime import datetime
import requests

logger = get_logger("vdca-update-job-log", LOGFILE_PATH)

engine = create_engine(DATABASE_URL)
db = VdcaDatabase(engine)

this_season = datetime.utcnow().year

# FOR TESTING ONLY!
DROP_AND__RECREATE = True

#  drop and recreate if necessary
if DROP_AND__RECREATE:
    logger.info("Dropping and recreating tables")
    years_to_process = range(2007, this_season+1)
    VdcaBase.metadata.drop_all(engine)
    VdcaBase.metadata.create_all(engine)
# Find current season, drop only those records
else:
    # Set to only process current season - changes will be processed as updates
    years_to_process = [this_season]


# Get a dict of teams
team_dict = get_teams(CRICKETSTATZ_API_URL, CRICKETSTATZ_CLUB_ID)

# Get a list of grades
url = CRICKETSTATZ_API_URL + "getgrades.aspx?league={}".format(CRICKETSTATZ_CLUB_ID)
response = requests.get(url)
response.raise_for_status()
grades_list = response.json()

# Get a list of fixtures
url = CRICKETSTATZ_API_URL + "getfixtures.aspx?league={}".format(CRICKETSTATZ_CLUB_ID)
response = requests.get(url)
response.raise_for_status()
fixtures_list = response.json()

# Combos to process
combos = get_team_season_grade_combinations(years_to_process, fixtures_list)


# Need to pull separate stats for finals, regular-season and combined
# 0 = both
# 1 = finals only
# 2 = exclude
finals_flags = [0,1,2]

# TODO: make this better - batting and bowling is basically the same code with one parameter different

## BATTING - note we're setting mininns=1 so we don't get records for every player
logger.info("Processing batting stats...")
base_url = CRICKETSTATZ_API_URL + "linkreport.aspx?mode={}&club={}&playerid=&mininns=1&minruns=&minovers=&team={}&grade={}&pool=&season={}&finals={}"
for ix, item in combos.iterrows():
    logger.debug("Processing batting stats... batch {} of {}".format(ix+1, len(combos)))
    for finals in finals_flags:
        team_id = item["Team"]
        team_name = team_dict[team_id]
        yr = item["Season"]
        grade_id = item["Grade"]
        # Get the URL to fetch from
        fetch_url = base_url.format(BATTING_STATS_REPORT_MODE, CRICKETSTATZ_CLUB_ID,team_id, grade_id, yr, finals)
        # Fetch response
        response = requests.get(fetch_url)
        response.raise_for_status()
        # Parse the resulting HTML
        html = get_html_from_response(response.text)
        data_table = get_table_from_html(html)
        # If we have no data, do nothing
        if len(data_table) == 0:
            continue
        # add necessary fields
        data_table["season"] = yr
        data_table["team_id"] = team_id
        data_table["finals_flag"] = finals
        data_table["player_id"] = [get_playerid_from_url(x) for x in data_table["player_url"].values]
        data_table["grade_id"] = grade_id

        # Query for each record, create if doesn't exist, update if does
        records = []
        for inner_ix, row in data_table.iterrows():
            result = db.query_unique_record(BattingStats, player_id=row["player_id"], team_id=row["team_id"], season=row["season"], finals_flag=finals, grade_id=grade_id)
            # If we get multiple results, that's a problem
            if len(result) > 1:
                raise Exception("Multiple entries detected")
            # If we get none, we need to create one
            if len(result) == 0:
                new_model = BattingStats()
                new_model.map_from_dataframe_row(row)
                records.append(new_model)
            # If we have a single record, update it with new data
            if len(result) == 1:
                result[0].map_from_dataframe_row(row)
                records.append(result[0])

        with db.yield_session() as s:
            s.add_all(records)

logger.info("Batting stats processed")


## BOWLING - note we're setting minovers=1 so we don't get records for every player
# NOTE: This flag doesn't seem to work for... reasons?  Filter them out below
logger.info("Processing bowling stats...")
base_url = CRICKETSTATZ_API_URL + "linkreport.aspx?mode={}&club={}&playerid=&mininns=&minruns=&minovers=1&team={}&grade={}&pool=&season={}&finals={}"
for ix, item in combos.iterrows():
    logger.debug("Processing bowling stats... batch {} of {}".format(ix+1, len(combos)))
    for finals in finals_flags:
        team_id = item["Team"]
        team_name = team_dict[team_id]
        yr = item["Season"]
        grade_id = item["Grade"]
        # Get the URL to fetch from
        fetch_url = base_url.format(BOWLING_STATS_REPORT_MODE, CRICKETSTATZ_CLUB_ID,team_id, grade_id, yr, finals)
        # Fetch response
        response = requests.get(fetch_url)
        response.raise_for_status()
        # Parse the resulting HTML
        html = get_html_from_response(response.text)
        data_table = get_table_from_html(html)
        # If we have no data, do nothing
        if len(data_table) == 0:
            continue
        # add necessary fields
        data_table["season"] = yr
        data_table["team_id"] = team_id
        data_table["finals_flag"] = finals
        data_table["player_id"] = [get_playerid_from_url(x) for x in data_table["player_url"].values]
        data_table["grade_id"] = grade_id

        # Filter out players who haven't bowled
        data_table = data_table[data_table["Overs"] != "0"]

        # Query for each record, create if doesn't exist, update if does
        records = []
        for inner_ix, row in data_table.iterrows():
            # TODO: debug this logic
            result = db.query_unique_record(BowlingStats, player_id=row["player_id"], team_id=row["team_id"], season=row["season"], finals_flag=finals, grade_id=grade_id)
            # If we get multiple results, that's a problem
            if len(result) > 1:
                raise Exception("Multiple entries detected")
            # If we get none, we need to create one
            if len(result) == 0:
                new_model = BowlingStats()
                new_model.map_from_dataframe_row(row)
                records.append(new_model)
            # If we have a single record, update it with new data
            if len(result) == 1:
                result[0].map_from_dataframe_row(row)
                records.append(result[0])

        with db.yield_session() as s:
            s.add_all(records)

logger.info("Bowling stats processed")

## FIELDING ##
# For fielding we need to grab two reports and join them, f-ing dumb, but here we are
logger.info("Processing fielding stats...")
base_url = CRICKETSTATZ_API_URL + "linkreport.aspx?mode={}&club={}&playerid=&mininns=1&minruns=&minovers=&team={}&grade={}&pool=&season={}&finals={}"
for ix, item in combos.iterrows():
    logger.debug("Processing fielding stats... batch {} of {}".format(ix+1, len(combos)))
    for finals in finals_flags:
        team_id = item["Team"]
        team_name = team_dict[team_id]
        yr = item["Season"]
        grade_id = item["Grade"]

        ## CATCHES
        # Get the catches URL
        fetch_url = base_url.format(CATCHING_STATS_REPORT_MODE, CRICKETSTATZ_CLUB_ID,team_id, grade_id, yr, finals)
        # Fetch response
        response = requests.get(fetch_url)
        response.raise_for_status()
        # Parse the resulting HTML
        html = get_html_from_response(response.text)
        catches_table = get_table_from_html(html)

        ## RUNOUTS
        # Get the catches URL
        fetch_url = base_url.format(RUNOUT_STATS_REPORT_MODE, CRICKETSTATZ_CLUB_ID,team_id, grade_id, yr, finals)
        # Fetch response
        response = requests.get(fetch_url)
        response.raise_for_status()
        # Parse the resulting HTML
        html = get_html_from_response(response.text)
        runouts_table = get_table_from_html(html)

        # JOIN tables
        data_table = catches_table.merge(runouts_table, on=["Name", "Last Team", "player_url", "Matches"], copy=True)

        # If we have no data, do nothing
        # TODO: do we need this now that we're only getting data for stuff we know exists?
        if len(data_table) == 0:
            continue
        # add necessary fields
        data_table["season"] = yr
        data_table["team_id"] = team_id
        data_table["finals_flag"] = finals
        data_table["player_id"] = [get_playerid_from_url(x) for x in data_table["player_url"].values]
        data_table["grade_id"] = grade_id

        # Filter out players who can't bowl, can't throw
        data_table = data_table[(data_table["Catches"] != "0") | (data_table["Run Outs"] != "0")]

        # Query for each record, create if doesn't exist, update if does
        records = []
        for inner_ix, row in data_table.iterrows():
            result = db.query_unique_record(FieldingStats, player_id=row["player_id"], team_id=row["team_id"], season=row["season"], finals_flag=finals, grade_id=grade_id)
            # If we get multiple results, that's a problem
            if len(result) > 1:
                raise Exception("Multiple entries detected")
            # If we get none, we need to create one
            if len(result) == 0:
                new_model = FieldingStats()
                new_model.map_from_dataframe_row(row)
                records.append(new_model)
            # If we have a single record, update it with new data
            if len(result) == 1:
                result[0].map_from_dataframe_row(row)
                records.append(result[0])

        with db.yield_session() as s:
            s.add_all(records)

logger.info("Fielding stats processed")