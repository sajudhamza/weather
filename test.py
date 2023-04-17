import unittest
import json
from app import app, db, create, WeatherRecord


class TestWeatherAPI(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://root:password@localhost:5432/postgres_test'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.app = app.test_client()
        with app.app_context():
            db.drop_all()
            db.create_all()

    def test_weather_home(self):
        record1 = WeatherRecord(max_temp=10, min_temp=5, ppt=20, station_id='station1', date='20220101')
        record2 = WeatherRecord(max_temp=15, min_temp=8, ppt=10, station_id='station1', date='20220102')
        record3 = WeatherRecord(max_temp=20, min_temp=10, ppt=5, station_id='station2', date='20220101')
        with app.app_context():
            db.session.add(record1)
            db.session.add(record2)
            db.session.add(record3)
            db.session.commit()

        response = self.app.get('/api/weather/?page=1&station_id=station1&date=20220101')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['maximum_temperature'], 10)
        self.assertEqual(data[0]['minimum_temperature'], 5)
        self.assertEqual(data[0]['precipitation'], 20)
        self.assertEqual(data[0]['station'], 'station1')
        self.assertEqual(data[0]['date'], '20220101')

        response = self.app.get('/api/weather/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 3)

    def test_weather_stats(self):
        # create some test data
        record1 = WeatherRecord(max_temp=10, min_temp=5, ppt=20, station_id='station1', date='20220101')
        record2 = WeatherRecord(max_temp=15, min_temp=8, ppt=10, station_id='station1', date='20220102')
        record3 = WeatherRecord(max_temp=20, min_temp=10, ppt=5, station_id='station2', date='20220101')
        with app.app_context():
            db.session.add(record1)
            db.session.add(record2)
            db.session.add(record3)
            db.session.commit()

        # test the stats endpoint with station_id filter
        response = self.app.get('/api/weather/stats/?station_id=station1')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['station'], 'station1')
        self.assertEqual(data[0]['date'], '20220101')
        self.assertEqual(data[0]['final_maximum_temperature'], 10)
        self.assertEqual(data[0]['final_minimum_temperature'], 5)
        self.assertEqual(data[0]['final_precipitation'], 20)

        self.assertEqual(data[1]['station'], 'station1')
        self.assertEqual(data[1]['date'], '20220102')
        self.assertEqual(data[1]['final_maximum_temperature'], 15)
        self.assertEqual(data[1]['final_minimum_temperature'], 8)
        self.assertEqual(data[1]['final_precipitation'], 10)

        # test the stats endpoint with date filter
       
