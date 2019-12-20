from app.config import VALID_API_KEY
from flask import Flask
from flask_restful import Resource, Api, abort, reqparse
from datetime import datetime

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('api_key', type=str, default=False, required=True)
parser.add_argument('season', type=int, default=False)


def validate_api_key(args):
    if args["api_key"] is None or VALID_API_KEY != args["api_key"]:
        abort(404, message="Invalid api key:  {}".format(args["api_key"]))
    return args["api_key"]


def validate_season(args):
    if args["season"] is None or args["season"] < 2007 or args["season"] > datetime.utcnow().year:
        abort(404, message="Invalid season:  {}".format(args["season"]))
    return args["season"]


class FieldingStats(Resource):

    def get(self):
        args = parser.parse_args()
        api_key = validate_api_key(args)
        season = validate_season(args)

        # TODO: actual work here

        return {'season': season,
                'api_key': "uh... no"}


api.add_resource(FieldingStats, '/fieldingStats')

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5000)
