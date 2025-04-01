from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson import ObjectId
from bson.errors import InvalidId
from decimal import *

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

# In the future I'll come back here to add logic to pull the aggregate data
                        # and add the actual data to the record. Pulling open and total available
                        # quantities will be their own endpoints that I call when updating a chemical.

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
    app.chemicals = app.db.chemicals
    app.lots = app.db.lots

class Lists():
    # Ideally I'd store these in the database and pull them for use when needed,
    # but I need to get *something* running for now. I know how this *should* be
    # set up and how it *is* set up in real LIMS systems.
    def __init__(self):
        self.__storage_conditions = [
            "-80 °C",
            "-20 °C",
            "2-8 °C",
            "Ambient",
            "Ambient, dark",
            "Room temperature"
        ]
        self.__units = [
            "g",
            "kg",
            "L",
            "mL",
            "µL"
        ]
        self.__containers = [
            "Ampoule",
            "Autosampler vial",
            "Bottle",
            "Vial"
        ]
        self.__sources = [
            "Purchased",
            "Prepared"
        ]
        self.__classifications = [
            "Flammable solvent",
            "Strong acid",
            "Weak acid",
            "Strong base",
            "Weak base",
            "Mobile phase",
            "Reagent",
            "Standard",
            "Solid",
            "Dewer",
            "Gas cylinder"
        ]

    @property
    def storage_conditions(self):
        return self.__storage_conditions
    
    @property
    def units(self):
        return self.__units
    
    @property
    def containers(self):
        return self.__containers
    
    @property
    def sources(self):
        return self.__sources
    
    @property
    def classifications(self):
        return self.__classifications

class ChemicalDocument():
    # Explain what a chemical class is as opposed to a lot. Explain why the addition of chemicals
    # and lots harmonizes data despite creating some redundancy, and why the addition of lots and
    # chemicals are isolated actions.
    def __init__(self, data):
        # __fields dictates both the required fields and their data type
        self.__fields = {
            "Name": str,
            "CAS Number": str,
            "Classification": str,
            "Storage Condition": str,
            "Source": str,
            
            "Purchased Fields": {
                "Manufacturer": str,
                "Manufacturer Part Number": str,
                "Amount": float,
                "Units": str,
                "Container Type": str,
            },
            
            "Prepared Fields": {
                "Method Reference": str
            },
            
            "Available Total": int,
            "Available Open": int
        }
        self.__request_data = data
    
    @property
    def fields(self):
        return self.__fields

    def validate_chemical_form(self):
        """
        Don't forget to include what each error_type means in final docstring
        """
        error_info = [None, 0]  # bad_key, error_type
        field_lists = Lists()

        def value_in_set(value, value_set):
            return value in value_set
        
        def data_type_match(test_value, target_type):
            # Expects piece of data and a data type as input.
            return type(test_value) == target_type
            
        def set_error_parameters(bad_key, error_type):
            bad_key = str(bad_key)
            error_type = error_type

        for key in self.__fields:            
            # Check "Purchased Fields" and "Prepared Fields" first because they'll fail
            # value_in_set(key, self.__request_data). They `continue` the outer loop if
            # data is acceptable to avoid this pitfall.
            
            continue_flag = False

            if key == "Purchased Fields":
                for inner_key in self.__fields[key]:
                    if not value_in_set(inner_key, self.__request_data):
                        error_info = [inner_key, 1]
                        break
                    elif not data_type_match(self.__request_data[inner_key], self.__fields[key][inner_key]):
                        error_info = [inner_key, 2]
                        break
                    elif inner_key == "Units":
                        if not value_in_set(self.__request_data[inner_key], field_lists.units):
                            error_info = [inner_key, 3]
                            break
                    elif inner_key == "Container Type":
                        if not value_in_set(self.__request_data[inner_key], field_lists.containers):
                            error_info = [inner_key, 3]
                            break
                    else:
                        continue_flag = True

                # See comment for outer loop
                if continue_flag:
                    continue
                else:
                    break

            elif key == "Prepared Fields":
                for inner_key in self.__fields[key]:
                    if not value_in_set(inner_key, self.__request_data):
                        error_info = [inner_key, 1]
                        break
                    elif not data_type_match(self.__request_data[inner_key], self.__fields[key][inner_key]):
                        error_info = [inner_key, 2]
                        break
                    else:
                        continue_flag = True
                
                # See comment for outer loop
                if continue_flag:
                    continue
                else:
                    break

            elif not value_in_set(key, self.__request_data):
                error_info = [key, 1]
                break

            elif not data_type_match(self.__request_data[key], self.__fields[key]):
                error_info = [key, 2]
                break

            elif key == "Classification":
                if not value_in_set(self.__request_data[key], field_lists.classifications):
                    error_info = [key, 3]
                    break

            elif key == "Storage Condition":
                if not value_in_set(self.__request_data[key], field_lists.storage_conditions):
                    error_info = [key, 3]
                    break

            elif key == "Source":
                if not value_in_set(self.__request_data[key], field_lists.sources):
                    error_info = [key, 3]
                    break
                
        return error_info

class LotDocument():
    # When writing docstring, note that redundancy of chemical fields in lots documents 
    # was chosen because they're needed when getting all lots, and that happens far
    # more often than adding a chemical (the other time they're needed together with
    # lot fields), so slightly larger documents and fewer server requests will be faster
    # on average than having a sctricter separation of concerns in the database. That's
    # also a good point for showing that I'm thinking about the right thing with the
    # document-based database (Add to "Things I learned" section of README.)

    # I'll want to pull the chemicals document for whichever chemical I'm trying to add and 
    # ensure the _id already exists. When pulling this to validate, I'll pull the entire
    # chemical form and add store that for use later when entering the redundant data onto
    # the lots form. I first need to create a chemical in test setup and in testing I'll query
    # to get the chemical _id then proceed as usual (submitting a request with that _id).
    
    
    # Note that I won't duplicate the aggregate "amount" fields
    def __init__(self):
        self.__chemical_fields = {
            "Name": str,
            "CAS Number": str,
            "Classification": str,
            "Storage Condition": str,
            "Source": str,
            
            # If source is purchased
            "Manufacturer": str,
            "Manufacturer Part Number": str,
            "Amount": float,
            "Units": str,
            "Container Type": str,
            
            # If source is prepared
            "Method Reference": str
        }
        self.__lot_fields_purchased = {
            "Manufacturer Lot/Batch Number": str,
            "Internal Lot Number": str,
            "Opened Date": str,
            "Expiry Date": str,
            "Empty Date": str
        }
        self.__lot_fields_prepared = {
            #It is absolutely imperative that `Amount`s are converted to Decimal()
            #when arithmetic is performed, but float works for the data type validation
            #this dictionary is used for.

            "Internal Lot Number": str,
            "Amount": float,
            "Units": str,
            "Container Type": str,
            "Preparation Date": str,    # Come back and figure out date validation later
            # Not sure how to validate yet. Ensure each prepared lto has at least one component
            # Ensure each component has the right keys. For loop on keys w/in `Components` when
            # key in outer loop == "Components"?
            "Expiry Date": str,
            "Empty Date": str,
            "Components": {
                "Component n": {
                    "Name": str,
                    "Internal Lot Number": str,                  
                    "Amount": float,
                    "Units": str,
                }
            }
        }

@app.route("/chemicals", methods=["GET", "POST"])
def manage_chemicals():
    if request.method == "GET":
        # List all chemicals
        all_chemicals = list(app.chemicals.find())
        for chemical in all_chemicals:
            # Type ObjectId not JSON serializable
            chemical["_id"] = str(chemical["_id"])
        response = jsonify(all_chemicals), 200
        
    elif request.method == "POST":
        # Add a new chemical with only those fields specified in the database structure.
        data = request.get_json()
        new_chemical = ChemicalDocument(data)

        def build_record(data, data_structure):
            # Build dictionary object to add new record using correct field names.
            record = {}

            for key in data_structure:
                if data["Source"] == "Purchased":
                    if key == "Purchased Fields":
                        for inner_key in data_structure[key]:
                            record[inner_key] = data[inner_key]
                    elif key == "Prepared Fields":
                        continue
                    elif key in ["Available Total", "Available Open"]:
                        record[key] = 0
                    else:
                        record[key] = data[key]
                elif data["Source"] == "Prepared":
                    if key == "Purchased Fields":
                        continue
                    elif key == "Prepared Fields":
                        for inner_key in data_structure[key]:
                            record[inner_key] = data[inner_key]
                    elif key in ["Available Total", "Available Open"]:
                        record[key] = 0
                    else:
                        record[key] = data[key]
            
            return record


        if not data:
            response = jsonify({"error": "Missing request body"}), 400
        else:
            # Validate data and check for extraneous keys in request
            form_val = new_chemical.validate_chemical_form()
            unexpected_keys = [key for key in data if key not in new_chemical.fields]

            if unexpected_keys:
                response = jsonify({"error": f"Unexpected fields: {unexpected_keys}."}), 422
            else:    
                if form_val[0]:
                    if form_val[1] == 1:
                        msg = f"Missing required field: {form_val[0]}."
                        response = jsonify({"error": msg}), 422
                    elif form_val[1] == 2:
                        msg = f"Incorrect data type for field: {form_val[0]}."
                        response = jsonify({"error": msg}), 422
                    elif form_val[1] == 3:
                        msg = f'Invalid entry of correct data type for {form_val[0]}.'
                        response = jsonify({"error": msg}), 422
                else:
                    record = build_record(data, new_chemical.fields)
                    result = app.chemicals.insert_one(record)
                    response = jsonify({"inserted_id": str(result.inserted_id)}), 201
        
    else:
        response = jsonify({"error": "Method not allowed"}), 405
    
    return response

@app.route("/chemicals/<chemical_id>", methods=["GET", "PUT", "DELETE"])
def manage_chemical(chemical_id):
    if request.method == "GET":
        # Fetch a specific chemical
        try:
            result = app.chemicals.find_one({"_id": ObjectId(chemical_id)})
            if result == None:
                response = jsonify({"error": "Not found"}), 404
            else:
                result["_id"] = str(result["_id"])
                response = jsonify(result), 200
        except InvalidId:
            response = jsonify({"error": "Invalid ID format"}), 400
    
    elif request.method == "PUT":
        # Update an existing chemical
        pass

    elif request.method == "DELETE":
        # Delete a chemical
        try:
            result = app.chemicals.delete_one({"_id": ObjectId(chemical_id)})
            if result.deleted_count == 0:
                response = jsonify({"error": "Not found"}), 404
            else:
                response = "", 204
        except InvalidId:
            response = jsonify({"error": "Invalid ID format"}), 400   

    else:
        response = jsonify({"error": "Method not allowed"}), 405
    
    return response

@app.route("/lots", methods=["GET", "POST"])
def manage_lots():
    if request.method == "GET":
        # Get all lots
        pass
    elif request.method == "POST":
        # Create new lot
        pass
    else:
        response = jsonify({"error": "Method not allowed"}), 405
    
    return response
    
@app.route("/lots/<lot_id>", methods=["GET", "PUT", "DELETE"])
def manage_lot():
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
        response = jsonify({"error": "Method not allowed"}), 405

    return response

if __name__ == "__main__":
    # Turn off debug=True when finished. Security concern.
    app.run(debug=True, host="0.0.0.0")