from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson import ObjectId
from bson.errors import InvalidId

"""
This project is in-progress. If I have to apply for a job before it's
finished, then understand that many of the comments throughout are "notes
to self" and will be removed when the build is finished.

***I use informal speech in my notes-to-self. I'd never leave informal speech
anywhere in published code, documentation, etc.***

Misc. Notes to self:
* `chemicals` and `lots` collections to avoid constantly re-writing static
data any time a new lot is added/removed.
* chemicals stores static data on the chemical, lots stores dynamic data.
* In the future I could store data on the chemicals document to force a
structure on a related lots document (e.g. # of components requried for
prepared reagents), but that's out of scope for having a complete project
before a job interview.
* Users can't just add a new chemical at will: That's a controlled process to
keep data harmonized.
    * Chemicals may be added freely, but not at the time of lot addition.
    *Lots may only be added to existing chemicals. This avoids redundancy from
    end-users who insist on creating their own sad path.
    * On a hypothetical front end, a GET request would be sent to /chemicals on
    loading, and a "name" field would have a drop-down list of the pulled names.
    These would correspond to the MongoDB "_id" (hidden) and would add the "_id"
    to the form (also hidden) when creating the lot so that validation is forced
    from the front-end (though I'll still test on the back end).
* Test set-up should include creating a chemical and pulling the _id for later
use, I think. Keeps every test from having to do that.
* When a new lot is added/removed (not updated), it should trigger an update
to the aggregate quantity of the corresponding `chemicals` document.
* Decision: When a front end sends GET request for all lots, I'm going to need
to display static data as well as the dynamic `lot` data. Either I can store
the static data on the `lots` documents as well as on `chemicals`
(redundant data, slightly larger documents) _or_ I can GET /chemicals at the
same time I GET /lots and join the data (longer loading time when user needs all
lot data, more operations, but much less redundant data). I can probably still
use `chemicals` to harmonize lot entry, and just have slightly larger documents
that load more quickly (`lots`) (fewer requests to server) because primarily I 
needthings to run quick for the analysts who absolutely hate any minor
inconvenience coming from a computer. When lot is entered (less frequent
operation than GET /lots), I can maybe make another call within this function
to pull the specific chemical I'm adding and then use that JSON object to load 
the fields in the `lots` JSON object on the back end?
    * When there's a front end, I (am not a front-end engineer in any sense of
    the word but I) think I'd be able to cache the GET /chemicals request I made
    when the page laoded and then use that to fill out the duplicated fields for
    the `lots` document? However, if I have to pull the chemical to validate 
    data entry, then I may as well just fill those fields in on the back-end,
    right? Handling that on the back-end would replace validation because I 
    can guarantee the front-end engineer can't mess it up if they're not 
    responsible for sending those data.
* So then: `chemicals` documents contain all static data for one type of 
chemical, and `lots` documents contain those static data from `chemicals` 
corresponding to the type of chemical being built (pulled from /chemical/<id> 
and added automatically) as well as dynamic data related to that lot. This 
allows for fewer operation when requesting to GET /lots, which would be the 
most frequent operation.

***Pick back up by re-organizing fields on chemicals and lots documents. Add
aggregate quantity to chemicals documents. Who cares about price? Let
procurement manage that with their own software HAHAHA.

"""

app = Flask(__name__)

# Allow dependency injection from tests, otherwise create chemicals collection
if not hasattr(app, "mongo_client"):
    # app.mongo_client = MongoClient("mongodb-service", 27017)    # This is the client I'll use when I set it up in Docker
    app.mongo_client = MongoClient("localhost", 27017)  # Remove this line when I begin testing in Docker containers
    app.db = app.mongo_client.chemical_inventory
    app.chemicals = app.db.chemicals    # chemicals collection can be thought of as a class (if you're a tech nerd).
    app.lots = app.db.lots  # lots collection represents instances of the chemicals class which stores dynamic data on each physical bottle in the lab.


@app.route("/chemicals", methods=["GET", "POST"])
def manage_general_chemicals():
    if request.method == "GET":
        # List all chemicals
        all_chemicals = list(app.chemicals.find())
        for chemical in all_chemicals:
            # Type ObjectId not JSON serializable
            chemical["_id"] = str(chemical["_id"])
        response = jsonify(all_chemicals), 200
        
    elif request.method == "POST":
        # Add a new chemical
        data = request.get_json()
        
        # Come back later to add a function, defined above the app routes, that validates the request body format
        # When the validation function is written, have it return a Bool to keep this structure essentially the same.
        if not data or "name" not in data:
            response = jsonify({"Error: Missing 'Name' field."}), 400
        else:
            result = app.chemicals.insert_one(
                {
                    "name": data["name"]    # To be fleshed out
                }
            )
            response = jsonify({"inserted_id": str(result.inserted_id)}), 201
    
    else:
        response = {"error: Method not allowed", 405}
    
    return response

@app.route("/chemicals/<chemical_id>", methods=["GET", "PUT", "DELETE"])
def manage_specific_chemical(chemical_id):
    if request.method == "GET":
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
    
    elif request.method == "PUT":
        # Update an existing chemical
        pass

    elif request.method == "DELETE":
        # Delete a chemical
        try:
            result = app.chemicals.delete_one({"_id": ObjectId(chemical_id)})
            if result.deleted_count == 0:
                response = {"error": "Not found"}, 404
            else:
                response = "", 204
        except InvalidId:
            response = {"error": "Invalid ID format"}, 400   

    else:
        response = {"error: Method not allowed", 405}
    
    return response

@app.route("/lots", methods=["GET", "POST"])
def manage_general_lots():
    if request.method == "GET":
        # Get all lots
        pass
    elif request.method == "POST":
        # Create new lot
        pass
    else:
        response = {"error: Method not allowed", 405}
    
    return response
    
@app.route("/lots/<lot_id>", method=["GET", "PUT", "DELETE"])
def manage_specific_lots():
    if request.method == "GET":
        # Get specific lot
        pass
    elif request.method == "PUT":
        # Update specific lot
        pass
    elif request.method == "DELETE":
        # Delete specific lot
        pass
    else:
        response = {"error: Method not allowed", 405}

    return response

if __name__ == "__main__":
    # Turn off debug=True when finished. Security concern.
    app.run(debug=True, host="0.0.0.0")