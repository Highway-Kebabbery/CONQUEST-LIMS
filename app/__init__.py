from flask import Flask
from pymongo import MongoClient
from app.api.lists import lists
from app.api.chemicals import chemicals
from app.api.lots import lots

def create_app():
    app = Flask(__name__)
    
    app.register_blueprint(lists, url_prefix="/lists")
    app.register_blueprint(chemicals, url_prefix="/chemicals")
    app.register_blueprint(lots, url_prefix="/lots")

    # Only initialize MongoDB client if it hasn't been injected (e.g., during testing)
    if not hasattr(app, "mongo_client"):
        # app.mongo_client = MongoClient("mongodb-service", 27017)    # Use this client for production
        app.mongo_client = MongoClient("localhost", 27017)  # Use this client for testing directly in WSL with MongoDB
        app.db = app.mongo_client.conquest_lims
        app.chemicals = app.db.chemicals
        app.lots = app.db.lots
        app.lists = app.db.lists

        return app