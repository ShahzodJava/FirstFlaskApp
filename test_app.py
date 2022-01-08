import unittest
import json

from werkzeug.test import Client
from flaskr import create_app
from models import setup_db, Plant

class PlantTestCase(unittest.TestCase):

  def setUp(self):
    self.app = create_app()
    self.client = self.app.test_client
    self.database_name = "plant_test"
    self.database_path = "postgresql://{}:{}@{}/{}".format('postgres','7907','localhost:5432',self.database_name)
    setup_db(self.app, self.database_path)

    self.new_plant = {
      'name':'Margarite',
      'scientific_name': 'Salvia margaritae Botsch',
      'is_poisonous':False,
      'primary_color':'purple'
    }
  def tearDown(self):
    pass
  def test_get_plants(self):
    res = self.client().get('/plants')
    data = json.loads(res.data)

    self.assertEqual(res.status_code, 200)
    self.assertEqual(data['success'],True)
    self.assertTrue(data['total_plants'])
    self.assertTrue(len(data['plants']))

  def test_404_send_requesting_beyond_valid_page(self):
    res = self.client().get('/plants?page=10000')
    data = json.loads(res.data)

    self.assertEqual(res.status_code, 404)
    self.assertEqual(data['success'], False)
    self.assertEqual(data['message'],'resource not found')

  def test_get_plant(self):
    res = self.client().get('/plants/17', json={'primary_color':'blue'})
    data = json.loads(res.data)

    self.assertEqual(res.status_code, 200)
    self.assertEqual(data['success'], True)
    self.assertTrue(len(data['plant']))

  def test_404_send_requesting_beyond_valid_plant_id(self):
    res = self.client().get('/plants/100')
    data = json.loads(res.data)

    self.assertEqual(res.status_code, 404)
    self.assertEqual(data['success'], False)
    self.assertEqual(data['message'], 'resource not found')

  def test_update_plant(self):
    res = self.client().patch('/plants/20', json={'is_poisonous':True})
    data = json.loads(res.data)

    plant = Plant.query.filter(Plant.id==20).one_or_none()

    self.assertEqual(res.status_code, 200)
    self.assertEqual(data['success'], True)
    self.assertEqual(plant.format()['is_poisonous'], True)

  def test_400_for_failed_update(self):
    res = self.client().patch('/plants/2')
    data = json.loads(res.data)

    self.assertEqual(res.status_code, 400)
    self.assertEqual(data['success'], False)
    self.assertEqual(data['message'],'bad request')

  def test_delete_plant(self):
    res = self.client().delete('/plants/11')
    data = json.loads(res.data)

    plant = Plant.query.filter(Plant.id==11).one_or_none()

    self.assertEqual(res.status_code, 200)
    self.assertEqual(data['success'], True)
    self.assertTrue(data['id'])
    self.assertEqual(plant, None)

  def test_422_if_plant_does_not_exists(self):
    res = self.client().delete('/plants/100')
    data = json.loads(res.data)

    self.assertEqual(res.status_code, 422)
    self.assertEqual(data['success'],False)
    self.assertEqual(data['message'], 'unprocessable')

  def test_create_plant(self):
    res = self.client().post('/plants', json =self.new_plant)
    data = json.loads(res.data)

    self.assertEqual(res.status_code, 200)
    self.assertEqual(data['success'], True)
    self.assertTrue(data['created'])

  def test_405_if_plant_creation_not_allowed(self):
    res = self.client().post('/plants/45', json = self.new_plant)
    data = json.loads(res.data)

    self.assertEqual(res.status_code, 405)
    self.assertEqual(data['success'], False)
    self.assertEqual(data['message'], 'method not allowed')





if __name__=="__main__":
  unittest.main()
