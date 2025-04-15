"""
Application factory for the CONQUEST-LIMS Flask application.

This module defines the `create_app` function, which configures and returns
a Flask app instance. It registers API blueprints and sets up a connection
to the MongoDB database, attaching the relevant collections as app-level 
attributes.
"""
from flask import Flask
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure as DBConnectionFailure
from elasticsearch import Elasticsearch, ConnectionError as ESConnectionError
from app.api.lists import lists
from app.api.chemicals import chemicals
from app.api.lots import lots
import os, time

def create_app():
    """
    Create and configure the Flask application.

    Registers API blueprints for chemicals, lists, and lots. 
    Initializes a MongoDB client and attaches the database and its collections 
    (chemicals, lots, and lists) as attributes of the Flask app.

    Returns:
        Flask: A configured Flask application instance.
    """
    app = Flask(__name__)
    
    app.register_blueprint(lists, url_prefix="/lists")
    app.register_blueprint(chemicals, url_prefix="/chemicals")
    app.register_blueprint(lots, url_prefix="/lots")

    # Only initialize MongoDB client if it hasn't been injected (e.g., during testing)
    if not hasattr(app, "mongo_client"):
        mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/conquest-lims-db")
        
        for i in range(15):
            try:
                app.mongo_client = MongoClient(mongo_uri)
                app.db = app.mongo_client.get_default_database()
                print("Connected to MongoDB")
                break
            except DBConnectionFailure:
                print(f"Failed to connect to MongoDB ({i + 1}/15)")
                time.sleep(3)
        
        else:
            raise DBConnectionFailure("Failed to connect to MongoDB after multiple attempts.")

        app.chemicals = app.db.chemicals
        app.lots = app.db.lots
        app.lists = app.db.lists
    
    if not hasattr(app, "es"):
        es_uri = os.getenv("ELASTIC_URI", "http://localhost:9200")

        for i in range(10):
            try:
                # Wouldn't hardcode passwords in production environment.
                app.es = Elasticsearch(es_uri, basic_auth=("elastic", "changeme"), verify_certs=False)


                # Check if ES is responding to ping
                if app.es.ping():
                    print("Connected to Elasticsearch")
                    break
                else:
                    raise ESConnectionError("Ping to Elasticsearch failed")

            except ESConnectionError as e:
                print(f"Failed to connect to Elasticsearch ({i + 1}/10): {e}")
                time.sleep(3)
        else:
            raise ESConnectionError("Failed to connect to Elasticsearch after multiple attempts.")
        
    @app.route("/")
    def index():
        return "Prepare to VANQUISH your competition.\n"

    return app