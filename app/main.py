from app.config import VALID_API_KEY
from flask import Flask, jsonify
from flask_restful import Resource, Api, abort, reqparse
from datetime import datetime
from app.data.database_utils import VdcaDatabase
from app.data.database_utils import models_to_json
from app.data.models import FieldingStats, BowlingStats, BattingStats, VdcaBase
from sqlalchemy.engine import create_engine
import json

from app.config import LOG_LEVEL, LOGFILE_PATH, DATABASE_URL

app = Flask(__name__)
api = Api(app)

engine = create_engine(DATABASE_URL)
db = VdcaDatabase(engine)

# TODO: logging - will require a separate logfile path in config/env vars

parser = reqparse.RequestParser()
parser.add_argument('api_key', type=str, default=False, required=True)
parser.add_argument('season', type=int, default=False, required=True)
parser.add_argument('finals_flag', type=int, default=False, required=True)
parser.add_argument('grade_id', type=int, default=False, required=True)


def validate_args(args):
    if args["api_key"] is None or VALID_API_KEY != args["api_key"]:
        abort(404, message="Invalid api key:  {}".format(args["api_key"]))
    if args["season"] is None or args["season"] < 2007 or args["season"] > datetime.utcnow().year:
        abort(404, message="Invalid season argument:  {}".format(args["season"]))
    if args["finals_flag"] is None or args["finals_flag"] not in [0,1,2]:
        abort(404, message="Invalid finals_flag argument")
    if args["grade_id"] is None:
        abort(404, message="Must provide a grade_id argument")

    return args


def validate_season(args):
    if args["season"] is None or args["season"] < 2007 or args["season"] > datetime.utcnow().year:
        abort(404, message="Invalid season:  {}".format(args["season"]))
    return args["season"]


def get_stats_by_type(table_type: VdcaBase):
    args = parser.parse_args()
    args = validate_args(args)

    results = db.query_stats_by_season_finals_grade(table_type,
                                                    season=args["season"],
                                                    finals_flag=args["finals_flag"],
                                                    grade_id=args["grade_id"])
    # TODO: figure out how to properly serialize this response - this way is a hack
    results = models_to_json(results)
    return results


class GetFieldingStats(Resource):

    def get(self):
        results = get_stats_by_type(FieldingStats)
        return results


class GetBowlingStats(Resource):

    def get(self):
        results = get_stats_by_type(BowlingStats)
        return results


class GetBattingStats(Resource):

    def get(self):
        results = get_stats_by_type(BattingStats)
        return results


api.add_resource(GetFieldingStats, '/fieldingStats')
api.add_resource(GetBattingStats, '/battingStats')
api.add_resource(GetBowlingStats, '/bowlingStats')

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5000)
