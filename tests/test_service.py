"""
Counter API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
"""
import os
import logging
from unittest.mock import patch
from unittest import TestCase
from redis.exceptions import ConnectionError
from service.common import status  # HTTP Status Codes
from service.common import log_handler
from service.routes import app, reset_counters


######################################################################
#  T E S T   C A S E S
######################################################################
class CounterTest(TestCase):
    """ REST API Server Tests """

    @classmethod
    def setUpClass(cls):
        """ This runs once before the entire test suite """
        app.testing = True
        log_handler.initialize_logging(logging.CRITICAL)

    @classmethod
    def tearDownClass(cls):
        """ This runs once after the entire test suite """
        pass

    def setUp(self):
        """ This runs before each test """
        reset_counters()
        self.app = app.test_client()

    def tearDown(self):
        """ This runs after each test """
        pass

######################################################################
#  T E S T   C A S E S 
######################################################################

    def test_index(self):
        """ Test index call """
        resp = self.app.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_create_counters(self):
        """ Test Create a counter """
        name = "foo"
        resp = self.app.post(f"/counters/{name}")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        data = resp.get_json()
        self.assertEqual(data["name"], name)
        self.assertEqual(data["counter"], 0)

    def test_list_counters(self):
        """ Test List counters """
        resp = self.app.get("/counters")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 0)
        # create a counter and name sure it appears in the list
        self.app.post("/counters/foo")
        self.app.post("/counters/bar")
        self.app.post("/counters/baz")
        resp = self.app.get("/counters")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 3)

    def test_read_counters(self):
        """ Test Read a counter """
        name = "foo"
        self.test_create_counters()
        resp = self.app.get(f"/counters/{name}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], name)
        self.assertEqual(data["counter"], 0)

    def test_update_counters(self):
        """ Test Update a counter """
        name = "foo"
        self.test_create_counters()
        resp = self.app.get(f"/counters/{name}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        print(data)
        self.assertEqual(data["name"], name)
        self.assertEqual(data["counter"], 0)
        # now update it
        resp = self.app.put(f"/counters/{name}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], name)
        self.assertEqual(data["counter"], 1)

    def test_delete_counters(self):
        """ Test Delete a counter """
        name = "foo"
        self.test_create_counters()
        resp = self.app.delete(f"/counters/{name}")
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        resp = self.app.get(f"/counters/{name}")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_method_not_allowed(self):
        """ Test method not allowed """
        resp = self.app.post(f"/counters")
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_counter_already_exists(self):
        """ Test counter already exists """
        name = "foo"
        self.test_create_counters()
        resp = self.app.post(f"/counters/{name}")
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)

    def test_update_not_found(self):
        """ Test update not found """
        name = "foo"
        resp = self.app.put(f"/counters/{name}")
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_bad_connection_create(self):
        """ Test a no database connection for create """
        # make a call to fire first requeest trigger
        resp = self.app.get(f"/counters")    
        with patch('service.routes.counter.get') as connection_error_mock:
            connection_error_mock.side_effect = ConnectionError()
            resp = self.app.post(f"/counters/foo")
            self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)

    def test_bad_connection_list(self):
        """ Test a no database connection for list """
        # make a call to fire first requeest trigger
        resp = self.app.put(f"/counters/foo")    
        with patch('service.routes.counter.keys') as connection_error_mock:
            connection_error_mock.side_effect = ConnectionError()
            resp = self.app.get(f"/counters")
            self.assertEqual(resp.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)            