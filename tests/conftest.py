import sys
import os

# Had to explicitly add root to sys.path for pytest to find the Flask app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from flask import Flask
from pymongo import MongoClient
import mongomock

from chemical_inventory_api_v1 import app as flask_app

@pytest.fixture()
def app():
    flask_app.config.update({
        "TESTING": True
    })

    flask_app.mongo_client = mongomock.MongoClient()
    flask_app.db = flask_app.mongo_client.chemical_inventory
    flask_app.chemicals = flask_app.db.chemicals

    yield flask_app

@pytest.fixture()
def client(app):
    return app.test_client()
