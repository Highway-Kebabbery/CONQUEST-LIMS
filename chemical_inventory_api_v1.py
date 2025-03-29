from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson import ObjectId
from bson.errors import InvalidId


app = Flask(__name__)

# Allow dependency injection from unit tests, otherwise create chemicals collection
if not hasattr(app, "mongo_client"):
    # app.mongo_client = MongoClient('mongodb-service', 27017)    # This is the client I'll use when I set it up in Docker
    app.mongo_client = MongoClient('localhost', 27017)  # Remove this line when I begin testing in Docker containers
    app.db = app.mongo_client.chemical_inventory
    app.chemicals = app.db.chemicals


@app.route('/chemicals', methods=['GET', 'POST'])
def manage_general_chemicals():
    if request.method == 'GET':
        # List all chemicals
        all_chemicals = list(app.chemicals.find())
        for chemical in all_chemicals:
            chemical['_id'] = str(chemical['_id'])  # Type ObjectId is not JSON serializable
        return jsonify(all_chemicals), 200
        
    elif request.method == 'POST':
        # Add a new chemical
        data = request.get_json()
        
        # Come back later to add a function, defined above the app routes, that validates the request body format
        # When the validation function is written, have it return a Bool to keep this structure essentially the same.
        if not data or "name" not in data:
            response = jsonify({'Error: Missing "Name" field.'}), 400
        else:
            result = app.chemicals.insert_one(
                {
                    "name": data["name"]
                }
            )
            response = jsonify({"inserted_id": str(result.inserted_id)}), 201
        return response

@app.route('/chemicals/<chemical_id>', methods=['GET', 'PUT', 'DELETE'])
def manage_specific_chemical(chemical_id):
    if request.method == 'GET':
        # Fetch a specific chemical
        try:
            result = app.chemicals.find_one({"_id": ObjectId(chemical_id)})
            if result == None:
                response = {"error": "Not found"}, 404
            else:
                result["_id"] = str(result["_id"])
                response = jsonify(result), 200
        except InvalidId:
            response = {"error": "Invalid ID format"}, 400
        return response
    
    elif request.method == 'PUT':
        # Update an existing chemical
        pass
    
    elif request.method == 'DELETE':
        # Delete a chemical
        try:
            result = app.chemicals.delete_one({"_id": ObjectId(chemical_id)})
            if result.deleted_count == 0:
                response = {"error": "Not found"}, 404
            else:
                response = '', 204
        except InvalidId:
            response = {"error": "Invalid ID format"}, 400
        return response    



if __name__ == "__main__":
    # Turn off debug=True when finished. Security concern.
    app.run(debug=True, host='0.0.0.0')