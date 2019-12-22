from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base

VdcaBase = declarative_base()

# TODO: add unique constraints and indexes to all tables

class BattingStats(VdcaBase):

    __tablename__ = "batting_stats"

    rowid = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer)
    player_name = Column(String)
    player_url = Column(String)
    team_name = Column(String)
    team_id = Column(String)
    season = Column(Integer)
    matches = Column(Integer)
    innings = Column(Integer)
    notouts = Column(Integer)
    high_score = Column(Integer)
    hs_notout = Column(Boolean)
    average = Column(Float)
    hundreds = Column(Integer)
    fifties = Column(Integer)
    ducks = Column(Integer)
    fours = Column(Integer)
    sixes = Column(Integer)
    runs_aggregate = Column(Integer)
    finals_flag = Column(String)
    grade_id = Column(Integer)

    def __init__(self):
        pass

    def map_from_dataframe_row(self,row):
        # Assign fields
        self.player_id = row["player_id"]
        self.player_name = row["Name"]
        self.player_url = row["player_url"]
        self.team_name = row["Last Team"]
        self.team_id = row["team_id"]
        self.season = row["season"]
        self.matches = int(row["Mts"])
        self.innings = int(row["Inns"])
        self.notouts = int(row["NOs"])
        self.hs_notout = "*" in row["HS"]
        self.high_score = int(row["HS"].replace("*",""))
        self.average = None if row["Average"] == "-" else float(row["Average"])
        self.hundreds = row["100s"]
        self.fifties = row["50s"]
        self.ducks = row["0s"]
        self.fours = row["4s"]
        self.sixes = row["6s"]
        self.runs_aggregate = row["Runs"]
        self.finals_flag = row["finals_flag"]
        self.grade_id = row["grade_id"]


class BowlingStats(VdcaBase):

    __tablename__ = "bowling_stats"

    rowid = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer)
    player_name = Column(String)
    player_url = Column(String)
    team_name = Column(String)
    team_id = Column(String)
    season = Column(Integer)
    matches = Column(Integer)
    overs = Column(String)
    maidens = Column(Integer)
    runs_against = Column(Integer)
    five_wicket_innings = Column(Integer)
    best_bowling = Column(String)
    average = Column(Float)
    economy = Column(Float)
    wickets_aggregate = Column(Integer)
    finals_flag = Column(String)
    grade_id = Column(Integer)

    def __init__(self):
        pass

    def map_from_dataframe_row(self,row):
        self.player_id = row["player_id"]
        self.player_name = row["Name"]
        self.player_url = row["player_url"]
        self.team_name = row["Last Team"]
        self.team_id = row["team_id"]
        self.season = row["season"]
        self.matches = int(row["Mts"])
        self.overs = row["Overs"]
        self.maidens = int(row["Maids"])
        self.runs_against = int(row["Runs"])
        self.five_wicket_innings = int(row["5WI"])
        self.best_bowling = row["BBI"]
        self.average = None if row["Average"] == "-" else float(row["Average"])
        self.economy = None if row["Econ"] == "-" else float(row["Econ"])
        self.wickets_aggregate = int(row["Wickets"])
        self.finals_flag = row["finals_flag"]
        self.grade_id = row["grade_id"]


class FieldingStats(VdcaBase):

    __tablename__ = "fielding_stats"

    rowid = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer)
    player_name = Column(String)
    player_url = Column(String)
    team_name = Column(String)
    team_id = Column(String)
    season = Column(Integer)
    matches = Column(Integer)
    catches = Column(Integer)
    runouts = Column(Integer)
    total_dismissals = Column(Integer)
    strikerate = Column(Float)
    finals_flag = Column(String)
    grade_id = Column(Integer)

    def __init__(self):
        pass

    def map_from_dataframe_row(self, row):
        self.player_id = row["player_id"]
        self.player_name = row["Name"]
        self.player_url = row["player_url"]
        self.team_name = row["Last Team"]
        self.team_id = row["team_id"]
        self.season = row["season"]
        self.matches = int(row["Matches"])
        self.catches = int(row["Catches"])
        self.runouts = int(row["Run Outs"])
        self.total_dismissals = self.catches + self.runouts
        self.strikerate = float(self.total_dismissals) / float(self.matches)
        self.finals_flag = row["finals_flag"]
        self.grade_id = row["grade_id"]

        pass
