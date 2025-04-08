"""
# List Choice
Lists are simple objects with two fields that must contain a unique string and
a list of strings. The lists needed for chemical and lot validation are sufficient.

# HTTP code 200
* The tests verify that list objects of all valid configurations are
successfully modified in or retrieved from the database.

HTTP code 201
* List objects of all valid configurations are successfully inserted in 
the database.

HTTP code 204
* The tests verify that list objects of all valid configurations are
successfully deleted from the database.

# HTTP code 400
* Missing request bodies return error code 400.
* GET requests with malformed primary keys return error code 400

# HTTP code 404
* Lists not found in the database returr error code 404.

# HTTP code 422:
All fields in the list request body, the primary key, and the nature of the 
request itself are tested individually to verify that the system properly 
validates all applicable error codes:

* No required fields are missing from the request body
* No required values are missing from the request body
* All fields in a list request are the correct type.
* List request bodies contain bo unexpected fields.
* POST: Ensure that the list does not already exist.
* PUT: Ensure that the list does exist.
* Malformed primary keys return error code 422.
* Primary keys match in the request body and address.
* Note that control flow when multiple errors exist cannot truly be tested for
lists because of the nature of their schema. This test must currently invalidate
the name field, and doing so results in the end point catching an error related to
the "Name" primary key.
* PUT: All invalid list configurations are tested for failure to update against 
a valid list record.
"""

import sys
import os

# Had to explicitly add root to sys.path for pytest to find the Flask app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest, copy, mongomock
from flask import Flask
from pymongo import MongoClient
from chemical_inventory_api_v1 import ChemicalSchema, ListsSchema, ValidationErrorCodes
from chemical_inventory_api_v1 import app as flask_app

@pytest.fixture()
def app():
    flask_app.config.update({
        "TESTING": True
    })

    flask_app.mongo_client = mongomock.MongoClient()
    flask_app.db = flask_app.mongo_client.conquest_lims
    flask_app.lists = flask_app.db.lists
    
    with flask_app.mongo_client as client:
        # Not technically necessary since mongomock is in-memory, but left as reminder
        # when I check back that it's important to use something like `with` to clean
        # up connections after testing. This is a learning project for me.
        yield flask_app

@pytest.fixture()
def client(app):
    return app.test_client()