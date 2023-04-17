from flask import Flask, request, jsonify
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, func, UniqueConstraint
from datetime import datetime
# from flasgger import Swagger, swag_from
from flask_swagger_ui import get_swaggerui_blueprint
import logging

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://root:password@localhost:5432/postgres'
api = Api(app)
db = SQLAlchemy(app)

# flask swagger configs
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Todo List API"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)


class WeatherRecord(db.Model):
    __tablename__ = 'weather_record'
    id = db.Column(db.Integer, primary_key=True)
    max_temp = db.Column(db.BigInteger, nullable=True)
    min_temp = db.Column(db.BigInteger, nullable=True)
    ppt = db.Column(db.BigInteger, nullable=True)
    station_id = db.Column(db.String, nullable=False)
    date = db.Column(db.String(8))
    __table_args__ = (UniqueConstraint('station_id', 'date', name='_station_date_uc'),
                     )

    @property
    def serialize(self):
        return {
            "station": self.station_id,
            "date": self.date,
            "maximum_temperature": self.max_temp,
            "minimum_temperature": self.min_temp,
            "precipitation": self.ppt,
        }


class AnalysisPerYyear(db.Model):
    __tablename__ = 'analysis_per_year'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String, nullable=False)
    station_id = db.Column(db.String, nullable=False)
    max_temp_mean = db.Column(db.Float, nullable=True)
    min_temp_mean = db.Column(db.Float, nullable=True)
    ppt_sum = db.Column(db.Float, nullable=True)
    __table_args__ = (UniqueConstraint('station_id', 'date', name='_station_date_uc1'),
                     )

    @property
    def serialize(self):
        return {
            "station": self.station_id,
            "date": self.date,
            "final_maximum_temperature": self.max_temp_mean,
            "final_minimum_temperature": self.min_temp_mean,
            "final_precipitation": self.ppt_sum,
        }

def create():
    with app.app_context():
        db.drop_all()
        db.create_all()


test_resource_fields = {
    'max_temp': fields.Integer,
    'min_temp': fields.Integer,
    'ppt': fields.Integer,
    'station_id': fields.String
}

analysis_per_year_resource_fields = {
    'date': fields.String,
    'station_id': fields.String,
    'max_temp_mean': fields.Float,
    'min_temp_mean': fields.Float,
    'ppt_sum': fields.Float
}

# swagger = Swagger(app)

# class Weather(Resource):
#     @swag_from('swagger/weather.yml')
#     @marshal_with(test_resource_fields)
#     def get(self):
#         parser = reqparse.RequestParser()
#         parser.add_argument('date', type=str)
#         parser.add_argument('station_id', type=str)
#         parser.add_argument('page', type=int, default=1)
#         parser.add_argument('per_page', type=int, default=10)
#         args = parser.parse_args()
#         query = Test.query
#         if args.date:
#             query = query.filter(Test.date == args.date)
#         if args.station_id:
#             query = query.filter(Test.station_id == args.station_id)
#         results = query.paginate(args.page, args.per_page, False).items
#         return results

# class WeatherStats(Resource):
#     @swag_from('swagger/weather_stats.yml')
#     @marshal_with(analysis_per_year_resource_fields)
#     def get(self):
#         parser = reqparse.RequestParser()
#         parser.add_argument('date', type=str)
#         parser.add_argument('station_id', type=str)
#         parser.add_argument('page', type=int, default=1)
#         parser.add_argument('per_page', type=int, default=10)
#         args = parser.parse_args()
#         query = AnalysisPerYear.query
#         if args.date:
#             query = query.filter(AnalysisPerYear.date == args.date)
#         if args.station_id:
#             query = query.filter(AnalysisPerYear.station_id == args.station_id)
#         results = query.paginate(args.page, args.per_page, False).items
#         return results

# api.add_resource(Weather, '/api/weather')
# api.add_resource(WeatherStats, '/api/weather/stats')

# if __name__ == '__main__':
#     create()
#     app.run(debug=True)

@app.route("/api/weather/", methods=["GET"])
def weather_home():
    page = request.args.get("page", type=int)
    date = request.args.get("date")
    station_id = request.args.get("station_id")
    result = WeatherRecord.query
    if date:
        result = result.filter(WeatherRecord.date == date)
    if station_id:
        result = result.filter(WeatherRecord.station_id == station_id)

    return jsonify([r.serialize for r in result.paginate(page=page, per_page=100)])




@app.route("/api/weather/stats/", methods=["GET"])
def stats():
    page = request.args.get("page", type=int)
    date = request.args.get("date")
    station_id = request.args.get("station_id")
    result = AnalysisPerYyear.query
    if date:
        result = result.filter(AnalysisPerYyear.date == date)
    if station_id:
        result = result.filter(AnalysisPerYyear.station_id == station_id)

    return jsonify([r.serialize for r in result.paginate(page=page, per_page=100)])


if __name__ == "__main__":
    create()
    app.run(debug=True)
