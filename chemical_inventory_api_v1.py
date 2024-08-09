from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId


app = Flask(__name__)
client = MongoClient('mongodb-service', 27017)
db = client.chemical_inventory
chemicals = db.chemicals


@app.route('/chemicals', methods=['GET', 'POST'])
def manage_general_chemicals():
    if request.method == 'GET':
        #: List all chemicals
        all_chemicals = list(chemicals.find())
        for chemical in all_chemicals:
            chemical['_id'] = str(chemical['_id'])
        return jsonify(all_chemicals), 200
        
    elif request.method == 'POST':
        #: Add a new chemical
        pass


@app.route('/chemicals/{id}', methods=['GET', 'PUT', 'DELETE'])
def manage_specific_chemical():
    if request.method == 'GET':
        #: Fetch a specific chemical.
        pass
    elif request.method == 'PUT':
        #: Update an existing chemical.
        pass
    elif request.method == 'DELETE':
        #: Delete a chemical.
        pass


if __name__ == "__main__":
    # Turn off debug=True when finished. Security concern.
    app.run(debug=True, host='0.0.0.0')