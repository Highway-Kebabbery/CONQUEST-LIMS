from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime, timezone
import copy, re
from typing import List

"""
# Notes to a hiring manager if somehow I apply to a job before I finish:

This project is in-progress. If I have to apply for a job before it's
finished, then understand that many of the comments throughout are "notes
to self" and will be removed when the build is finished.

I include rough docstring-like notes on functions as I write, but formalising
those will come last (i.e. No edits left, all testing passed
(but will test again after), ready to push to staging environment).

***I use informal speech in my notes-to-self. I'd never leave informal speech
anywhere in published code, documentation, etc.***







# General lists of things to include in documentation
Chemical/lot request validation: RRRRRRRRRRRREEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE Check this section again after testing is complete
* All fields are present
* No extra fields are present
* All fields have the correct type
* All fields that must be selected from a validated list contain a value from that list
* Requests to update existing chemical templates contain the ID of a valid chemical template
in the database (expired chemicals are still allowed to be added as components).
* Requests to create lots of prepared reagents use valid chemical IDs of chemicals that
both exist as chemical templates and also have at least one lot logged and ready for use.
* All non-empty date fields are received as strings in the ISO 8601 format with timezone offsets.
* Prepared reagents contain at least one chemical component.
* Requests to update lots are made for valid lot IDs of lots currently existing in the database.
* When adding a purchased chemical, the system checks to see if the requested combination of
manufacturer, manufacturer part number, amount, unit, and container type already exists in the
database to prevent duplicate logging of the same chemical part in multiple templates under
different names.
* When adding a prepared chemical, the system checks to see if a chemical template already exists
in the database for the requested Method/Step Referenceto prevent duplicate logging of the same
chemical part in multiple templates under different names.
* The system checks to ensure any ID key is a valid object of the type ObjectId().
* All required fields have values
* A real LIMS would specify in the chemicals template for prepared materials the number of components and the
chemical_id for each, as well as specifying amounts to add and including a space to record the
actual added amount. Creation of a prepared material would pull the chemical template, fill in
the required information, and store it as a lot document. This is outside the scope of my
demonstration portfolio project.
* Include somewhere in README that I implemented my own primary key for lists collection rather than
relying on MongoDB's "_id" primary key.

General schema:
* Chemical templates store general information on a given part number from a given manufacturer.
* Lots store information on a specific instance of a chemical (a bottle of purchased material being logged into the lab)
* The addition of chemical templates is highly validated to prevent system bloat and disorganization from duplicate templates for the same manufacturer part number.
* Chemical templates must be added before a lot of that chemical can be logged into the system.
* Purchased materials must be first logged into the system before prepared materials can be logged (edge case).
* Lists collection stores documents containing validated lists to constrain end-user entry.
    * Each document contains one list of the form {"Name": <List_Name>}, {"List_entries": [list, of, validated, values]}
* ListSchema.Name in a given list links to various fields in ChemicalSchema. Lists are named after the fields they constrain.

# Define request structure and data type for prepared and purchased chemicals and prepared and purchased lots
* Purchased chemicals:
                                   # Only one chemical may be added per unique combination of: Manufacturer, manufacturer part number, amount, unit, container type.
    request = {
        "_id": str,                # Required for PUT, discarded for POST. String must be convertable to a valid ObjectId(). chemicals collection primary key.
        "Name": str,               # Required.
        "CAS_Number": str,         # Required.
        "Classification": str,     # Required. This value must come from the lists.{"Name": "Classifications"} list in the database depending on whether the lists collection is in service yet.
        "Storage_Condition": str,  # Required. This value must come from the lists.{"Name": "Storage_Conditions"} list in the database depending on whether the lists collection is in service yet.
        "Source": str,             # Required. This value must come from the lists.{"Name": "Sources"} list in the database depending on whether the lists collection is in service yet.
        "Purchased_Fields": {      # Required.
            "Manufacturer": str,              # Required for purchased materials. This value must come from the lists.{"Name": "Manufacturers"} list in the database depending on whether the lists collection is in service yet.
            "Manufacturer_Part_Number": str,  # Required for purchased materials.
            "Amount": [int, float],           # Required for purchased materials. Either type is acceptable.
            "Units": str,                     # Required for purchased materials. This value must come from the lists.{"Name": "Units"} list in the database depending on whether the lists collection is in service yet.
            "Container_Type": str             # Required for purchased materials. This value must come from the lists.{"Name": "Container_Types"} list in the database depending on whether the lists collection is in service yet.
        }
    }
* Prepared chemicals:
    request = {
        "_id": str,                # Required for PUT, discarded for POST. String must be convertable to a valid ObjectId(). chemicals collection primary key.
        "Name": str,               # Required.
        "CAS_Number": str,         # Required.
        "Classification": str,     # Required. This value must come from the lists.{"Name": "Classifications"} list in the database depending on whether the lists collection is in service yet.
        "Storage_Condition": str,  # Required. This value must come from the lists.{"Name": "Storage_Conditions"} list in the database depending on whether the lists collection is in service yet.
        "Source": str,             # Required. This value must come from the lists.{"Name": "Sources"} list in the database depending on whether the lists collection is in service yet.
        "Prepared_Fields": {      # Required.
            "Method_Step_Reference": str  # Required for prepared materials. End users must be as explicit as possible when referring to laboratory SOP method/step number as only one chemical template is allowed per method/step number.
        }
    }
* Purchased lots:
    request = {
        "_id": str,                            # Required for PUT, discarded for POST. String must be convertable to a valid ObjectId(). lots collection primary key.
        "chemical_id": str,                    # Required. String must be convertable to a valid ObjectId(). Links to chemicals._id. Must be the "_id" of an existing chemicals collection template.
        "Manufacturer_Lot_Batch_Number": str,  # Required.
        "Open_Date": str,                      # Optional (use of field would be proceduralized by lab SOP). Must be a string in ISO 8601 format.
        "Expiry_Date": str,                    # Required. Must be a string in ISO 8601 format.
        "Empty_Date": str,                     # Optional (use of field would be proceduralized by lab SOP). Must be a string in ISO 8601 format.
    }
* Prepared lots:
    request = {
        "_id": str,               # Required for PUT, discarded for POST. String must be convertable to a valid ObjectId(). lots collection primary key.
        "chemical_id": str,       # Required. String must be convertable to a valid ObjectId(). Links to chemicals._id. Must be the "_id" of an existing chemicals collection template.
        "Amount": [int, float],   # Required. Either type is acceptable.
        "Units": str,             # Required. This value must come from the lists.{"Name": "Units"} list in the database depending on whether the lists collection is in service yet.
        "Container_Type": str,    # Required. This value must come from the lists.{"Name": "Container_Types"} list in the database depending on whether the lists collection is in service yet.
        "Preparation_Date": str,  # Required. Must be a string in ISO 8601 format.
        "Expiry_Date": str,       # Required. Must be a string in ISO 8601 format.
        "Empty_Date": str,        # Optional (use of field would be proceduralized by lab SOP). Must be a string in ISO 8601 format.
        "Components": [           # Required. Prepared lots require >= 1 components.
            # Purchased chemical/lot components        # Purchased and prepared lots currently have redundant requests, but they are left separate in the event that they ever digress.
            {
                "lot_id": str,                         # Required. String must be convertable to a valid ObjectId(). Links to lots._id. Must be the "_id" of an existing lots collection lot.
                "Amount": [int, float],                # Required. Either type is acceptable.
                "Units": str                           # Required. This value must come from the lists.{"Name": "Units"} list in the database depending on whether the lists collection is in service yet.
            },
            # Prepared chemical/lot components
            {
                "lot_id": str,           # Required. String must be convertable to a valid ObjectId(). Links to lots._id. Must be the "_id" of an existing lots collection lot.
                "Amount": [int, float],  # Required. Either type is acceptable.
                "Units": str             # Required. This value must come from the lists.{"Name": "Units"} list in the database depending on whether the lists collection is in service yet.
            }
        ]
    }

# Define response structure and data type for prepared and purchased chemicals and prepared and purchased lots
* Purchased chemicals:
    response = {
        "_id": str,
        "Name": str,
        "CAS_Number": str,
        "Classification": str,
        "Storage_Condition": str,
        "Source": str,
        "Purchased_Fields": {
            "Manufacturer": str,
            "Manufacturer_Part_Number": str,
            "Amount": [int, float],
            "Units": str,
            "Container_Type": str
        }
    }
* Prepared chemicals:
    response = {
        "_id": str,
        "Name": str,
        "CAS_Number": str,
        "Classification": str,
        "Storage_Condition": str,
        "Source": str,
        "Prepared_Fields": {
            "Method_Step_Reference": str
        }
    }
* Purchased lots:
    response = {
        "_id": str,
        "chemical_id": str,
        "Name": str,
        "CAS_Number": str,
        "Classification": str,
        "Storage_Condition": str,
        "Source": str,
        "Purchased_Fields": {
            "Manufacturer": str,
            "Manufacturer_Part_Number": str,
            "Manufacturer_Lot_Batch_Number": str,
            "Amount": [int, float],
            "Units": str,
            "Container_Type": str
        }
        "Open_Date": str,
        "Expiry_Date": str,
        "Empty_Date": str
    }
* Prepared lots:
    response = {
        "_id": str,
        "chemical_id": str,
        "Name": str,
        "CAS_Number": str,
        "Amount": [int, float],
        "Units": str,
        "Container_Type": str,
        "Classification": str,
        "Storage_Condition": str,
        "Source": str,
        "Prepared_Fields": {
            "Method_Step_Reference": str,
        }
        "Preparation_Date": str,
        "Expiry_Date": str,
        "Empty_Date": str,
        "Components": [                                # List of dicts, one component per dict
            # Purchased chemical/lot component
            {
                "lot_id": ObjectId,
                "Name": str,
                "Manufacturer": str,
                "Manufacturer_Part_Number": str,
                "Manufacturer_Lot_Batch_Number": str,
                "Amount": [int, float],                # Either is allowed. Enforced via validation methods in each schema class.
                "Units": str,
                "Expiry_Date": datetime
            },
            # Prepared chemical/lot component
            {
                "lot_id": ObjectId,
                "Name": str,
                "Method_Step_Reference": str,
                "Amount": [int, float],
                "Units": str,
                "Expiry_Date": datetime
            }
        ]
    }

# Define database schema for prepared and purchased chemicals and prepared and purchased lots
* Purchased chemicals:
    record = {
        "_id": ObjectId,
        "Name": str,
        "CAS_Number": str,
        "Classification": str,
        "Storage_Condition": str,
        "Source": str,
        "Purchased_Fields": {
            "Manufacturer": str,
            "Manufacturer_Part_Number": str,
            "Amount": [int, float],           # Either is allowed. Enforced via validation methods in each schema class.
            "Units": str,
            "Container_Type": str
        }
        "Available_Total": int,               # Optional or removed and ignored in requests. Recalculated when lots are added/updated or when chemicals are updated.
        "Available_Open": int                 # Optional or removed and ignored in requests. Recalculated when lots are added/updated or when chemicals are updated.
    }
* Prepared chemicals:
    record = {
        "_id": ObjectId,
        "Name": str,
        "CAS_Number": str,
        "Classification": str,
        "Storage_Condition": str,
        "Source": str,
        "Prepared_Fields": {
            "Method_Step_Reference": str
        }
        "Available_Total": int,           # Optional or removed and ignored in requests. Recalculated when lots are added/updated or when chemicals are updated.
        "Available_Open": int             # Optional or removed and ignored in requests. Recalculated when lots are added/updated or when chemicals are updated.
    }
* Purchased lots:
    record = {
        "_id": ObjectId,
        "chemical_id": ObjectId,
        "Name": str,
        "CAS_Number": str,
        "Classification": str,
        "Storage_Condition": str,
        "Source": str,
        "Purchased_Fields": {
            "Manufacturer": str,
            "Manufacturer_Part_Number": str,
            "Manufacturer_Lot_Batch_Number": str,
            "Amount": [int, float],                # Either is allowed. Enforced via validation methods in each schema class.
            "Units": str,
            "Container_Type": str
        }
        "Open_Date": datetime,
        "Expiry_Date": datetime,
        "Empty_Date": datetime
    }
* Prepared lots:
    record = {
        "_id": ObjectId,
        "chemical_id": ObjectId,
        "Name": str,
        "CAS_Number": str,
        "Amount": [int, float],                        # Either is allowed. Enforced via validation methods in each schema class.
        "Units": str,
        "Container_Type": str,
        "Classification": str,
        "Storage_Condition": str,
        "Source": str,
        "Prepared_Fields": {
            "Method_Step_Reference": str
        }
        "Preparation_Date": datetime,
        "Expiry_Date": datetime,
        "Empty_Date": datetime,
        "Components": [                                # List of dicts, one component per dict
            # Purchased chemical/lot component
            {
                "lot_id": ObjectId,
                "Name": str,
                "Manufacturer": str,
                "Manufacturer_Part_Number": str,
                "Manufacturer_Lot_Batch_Number": str,
                "Amount": [int, float],                # Either is allowed. Enforced via validation methods in each schema class.
                "Units": str,
                "Expiry_Date": datetime
            },
            # Prepared chemical/lot component
            {
                "lot_id": ObjectId,
                "Name": str,
                "Method_Step_Reference": str,
                "Amount": [int, float],
                "Units": str,
                "Expiry_Date": datetime
            }
        ]
    }

# Define request schema for validated lists
    request = {
        "Name": str,
        "List_entries: [
            str
        ]
    }

# Define response schema for validated lists
    response = {
        "Name": str,
        "List_entries: [
            str
        ]
    }

# Define database schema for validated lists
    record = {
        "_id": ObjectId,
        "Name": str,
        "List_entries: [
            str
        ]
    }


# Notes for documentation:
* All dates must be received by the back end as strings in ISO 8601 format (including timezone offset) and are converted to UTC for storage.
* All dates are served to front-end as UTC date strings in ISO 8601 format.
* All database keys (currently chemicals._id, lots._id, lots.chemical_id, and Lots.Components.lot_id) must be received by the back end as strings that can be converted to valid ObjectIds.
* All database keys of type ObjectId are served to the front end as strings.
* lots.chemical_id links to chemicals._id
* lots.Components.lot_id links to lots._id
* PUT requests for chemicals or lots is expected to come in with a primary key field "_id"
* POST requests for chemicals or lots will be stripped of their primary key field "_id" if they have one.
* Optional fields are required to be sent with an empty value of None type or the type specified in the 
schema. The key cannot be missing.
* Do not attempt a PUT request to update a chemical template with the template of another chemical
whose lots would need to use the first chemical, the replaced one, as a component. This cannot be enforced
until and unless the system is changed to operate in a more rigorous fashion where chemical templates
also prescribe prepared lot components and amounts.


* Don't skip over this because it's the most fleshed out record of this idea: Note that this chemical inventory system isn't as robust as it could be. Ideally 
prepared reagent chemical templates would constrain which purchased chemicals are allowed
to be used for each component, they would constrain the number of components added, and
they would also constrain the amounts added of each chemical component. Prepared *lots*
would then query not only that the added lot_id exists, but also that it's an instance of
(one of) the chemical template(s) mandated for use in that lot component by the prepared lots
parent chemical template. Prepared lot compnoents would also have fields to enter the actual
amount used of each chemical, and this would potentially be validated against the prescribed
amount, though deviations may be acceptable with user audit trail comments (e.g. some SOPs allow
for preparation in equal parts at different volumes, like half, double, etc.)
* When writing documentation, note that redundancy of chemical fields in lots documents was chosen because they're needed when getting all lots, and that happens far more often than adding a chemical (the other time they're needed together with lot fields), so slightly larger documents and fewer server requests will be faster on average than having a sctricter separation of concerns in the database. That's also a good point for showing that I'm thinking about the right thing with the document-based database (Add to "Things I learned" section of README.)
* If I really wanted to make this more realistic then I'd change ChemicalSchema to
StandardReagentTemplate and change LotSchema to StandardReagent. I'd then use
StandardReagentTemplate to also control both how many components are added to 
a given prepared reagent (with a forced _id that matches the method reference)
as well as controlling (really looking ahead) the addition of a test sample with a test
analysis (e.g. FTIR testing required to release purchased lot of a reagent for
manufacturing use.) All of that is way out of scope for demonstrating that I can use
these technologies, though. If I'm going to make a build that ready-to-ship then it'll
be for something I actually use and/or sell.
* A bunch of crap I can probably read later, like when I write documentation:
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
    * So then: `chemicals` documents contain all static data for one type of 
    chemical, and `lots` documents contain those static data from `chemicals` 
    corresponding to the type of chemical being built (pulled from /chemical/<id> 
    and added automatically) as well as dynamic data related to that lot. This 
    allows for fewer operation when requesting to GET /lots, which would be the 
    most frequent operation.


    





# Where to pick up:
* Write tests
    * Write script to load lists into lists collection.
    * Write script to load database within a test
    * I'll need to create chemicals then query them to get their _ids and do the same with lots. Flesh out tests later.
    * Test all chemical and lot methods/end points for now and call it tested
* Depending on whether I could quikcly get script to load database, write code to load it with lists collection
    * No, you're not writing end points to edit the lists collection. That can be a future upgrade.
    * You're not writing validation for the lists collection given there are no end points to interface with the lists collection.
        * Note these things in the ListsSchema() docstring
* Write docstrings and clean up comments for entire program in its current state
    * For each class, note which error codes it can return for ease of use in api end points below
    * Note which fields are stripped from the request and stored in instance variables to allow reuse of validation for both POST anf PUT methods
* Check for bugs again
* Write README as it pertains to the app and database
* Containerize with Docker
* Orchestrate with Minikube
* Update README and documentation to include containerization/Minikube
* Add ElasticSearch integration
* Update README to include ElasticSearch integration





# Future Upgrades
There are several opportunities to improve this code that weren't implemented while building
the minimum viable product:
* Note that system does not currently reject requests to update (replace) a chemical with 
a request for a prepared chemical that uses the replaced chemical in one of its components
(This operation would remove the reference required for the new chemical, but it would pass
the initial checks because it's an edge case).
* Create class ApiErrorCodes to store error messages similar to ValidationErrorCodes
    * Tests not asserting data["error"].startswith could then be made more robust
* Add an optional "Comments" field to all logged lots and chemicals. Must be a string. Max length... 256 chars?
    * This would allow yo uto log a lot of the water dispenser and note the expiry date is the "PM Due Date."
* I want to enter int(0) for "Amount" for the water system lots, but it fails (as it should) for being empty.
    * Implement a workaround in the case of instruments? This is a super small edge case.
    * This would be easier once I flatten incoming requests and handle by field rather than with a for-loop
    dictated by the class schema components
* Add "Removed" fields to lots, chemicals, and lists.
    * Update DELETE end points to set Removed=True rather than actually deleting anything
* At some point an audit trail for changes to records would be required. A separate class? Out of scope for a portfolio project.
* Consider locking the 'Name" field for edits after record creation. This would effectively make it impossible
to completely replace one record (say, a methanol chemical) with another (replacing said methanol record with information for an acetone product).
This and the addition of a "Removed" flag to replace true deletion would prevent the complete disappearance of records because the names would always be available.
Although a record could be replaced in every field but the "Name," it would be unusable as a replacement because of the locked name field.
* Prevent "Open Dates" from being future dates/times.
* Prevent empty dates from being earlier than open or prepared dates
* Prevent unopened lots from being used as compnents
* Prevent expired lots from being opened
"""

app = Flask(__name__)

# Allow dependency injection from tests, otherwise create chemicals collection
if not hasattr(app, "mongo_client"):
    # app.mongo_client = MongoClient("mongodb-service", 27017)    # Use this client for production
    app.mongo_client = MongoClient("localhost", 27017)  # Use this client for testing directly in WSL with MongoDB
    app.db = app.mongo_client.conquest_lims
    app.chemicals = app.db.chemicals
    app.lots = app.db.lots
    app.lists = app.db.lists

class HelperFunctions():
    ISO_8601_WITH_OFFSET_REGEX = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?([+-]\d{2}:\d{2}|Z)$"
    
    @staticmethod
    def get_schema_keys(dictionary):
        # Accepts a schema dictionary
        # Returns all keys in a two-level dictionary or a dict-list-dict object as a list()
        # as well as the number of elements in the list if one value was a list
        # Expects that only one value in the dict will be a list. Need to know how many elements
        # exist because I need to know how many duplicates to expect to catch missing/extra
        # fields in lot validation of component fields.
        keys = []
        num_list_dict_elements = 0

        for key, value in dictionary.items():
            if isinstance(value, dict):
                # Adds "Purchased_Fields"/"Prepared_Fields" key and their subkeys
                keys.append(key)
                for subkey in value:
                    keys.append(f"{key}.{subkey}")
            elif isinstance(value, list):
                keys.append(key)
                for element in value:
                    if not isinstance(element, dict):
                        # Do nothing else if it's an "Amount" schema key
                        break
                    else:
                        # Adds "Components" as a key then extracts each key from each component
                        num_list_dict_elements += 1
                        for subkey in element:
                            keys.append(f"{key}.{subkey}")
            else:
                keys.append(key)
        
        return [keys, num_list_dict_elements]
    
    @staticmethod
    def to_datetime_utc(alleged_iso_8601_string):
        # This function accepts a string in valid ISO 8601 format and converts it
        # to a datetime object in the UTC time zone.
        if isinstance(alleged_iso_8601_string, datetime):
            # The function is run again when building records
            utc_dt = alleged_iso_8601_string
        elif isinstance(alleged_iso_8601_string, str):
            if not re.match(
                HelperFunctions.ISO_8601_WITH_OFFSET_REGEX,
                alleged_iso_8601_string
            ):
                raise ValueError("Date string must be ISO 8601 with time offset.")
            else:
                dt = datetime.fromisoformat(alleged_iso_8601_string)
                utc_dt = dt.astimezone(timezone.utc)

        return utc_dt
    
    @staticmethod
    def miss_req_field(key, keys):
        missing_field = not key in keys
        return missing_field
    
    @staticmethod
    def miss_req_value(value):
        missing_value = not value
        return missing_value
    
    @staticmethod
    def wrong_type(value, target_type):
        # Accepts a value and either a type, a value of
        # the target type, or a list of types for comparison.
        
        if isinstance(target_type, type):
            # Normal conditions: Receive value and type
            wrong_type = not isinstance(value, target_type)
        elif isinstance(target_type, list):
            # If receiving a list of types, as in "Amount"
            if not type(target_type[0]) == type:
                # If receiving a request list to check type of list itself.
                # Accounts for empty lists.
                wrong_type = not type(value) == type(target_type)
            else:
                # If receiving a list of acceptable types from a schema
                wrong_type = not type(value) in target_type
        else:
            # If receiving two values
            wrong_type = not isinstance(value, type(target_type))

        return wrong_type
    
    @staticmethod
    def inval_list_entry(val, validated_list):
        not_in_list = not val in validated_list
        return not_in_list
        

class ValidationErrorCodes():
    # Request validation error codes
    MISS_REQ_FIELD = 1  # Required key not present
    WRONG_TYPE = 2  # Value is wrong type
    INVAL_LIST_ENTRY = 3    # Value does not exist in validated list
    UNEXP_FIELD = 4    # Unexpected field in request form
    CHEM_NOT_FOUND = 5    # Chemical not found in database
    WRONG_DATE_FORMAT = 6    # Date not in ISO 8601 format
    MISSING_COMP = 7    # All prepared chemicals require at least one component
    LOT_NOT_FOUND = 8    # Lot not found in database
    CHEM_DUPLICATE = 9    # Chemical already exists in database
    INVALID_ID = 10    # ID field is not a valid ObjectId()
    MISS_REQ_VALUE = 11    # Required field left blank in request
    LIST_DUPLICATE = 12    # List already exists in database
    LIST_NOT_FOUND = 13    # List not fond in database

    # Static portion of error messages
    # Character counts given for testing
    MISS_REQ_FIELD_MSG = "Missing required field:"  # 23 chars
    WRONG_TYPE_MSG = "Incorrect data type for field:"  # 30 chars
    INVAL_LIST_ENTRY_MSG = "Invalid entry of correct data type for field:"  # 45 chars
    UNEXP_FIELD_MSG = "Unexpected fields:"  # 18 chars
    CHEM_NOT_FOUND_MSG = "Chemical _id not found in database:"  # 35 chars
    WRONG_DATE_FORMAT_MSG = "Date string must be in ISO 8601 format:"  # 39 chars
    MISSING_COMP_MSG = "Prepared lots require at least one component:"  # 45 chars
    LOT_NOT_FOUND_MSG = "Lot _id not found in database:"  # 30 chars
    CHEM_DUPLICATE_MSG = "Chemical already exists in database with primary key:"  # 36 chars
    INVALID_ID_MSG = "_id cannot be converted to valid ObjectId:"  # 42 chars
    MISS_REQ_VALUE_MSG = "Field missing required value:"  # 29 chars
    LIST_DUPLICATE_MSG = "List already exists with name:"  # 30 chars
    LIST_NOT_FOUND_MSG = "List not found in database with name:"  # 37 chars

    @staticmethod
    def gen_val_err_msg(error_info):
        # Receives a list ["affected fields", error_code=int]
        # error_code corresponds to class error code parameters
        
        match error_info[1]:
            case ValidationErrorCodes.MISS_REQ_FIELD:
                msg = f"{ValidationErrorCodes.MISS_REQ_FIELD_MSG} {error_info[0]}"
            case ValidationErrorCodes.WRONG_TYPE:
                msg = f"{ValidationErrorCodes.WRONG_TYPE_MSG} {error_info[0]}"
            case ValidationErrorCodes.INVAL_LIST_ENTRY:
                msg = f"{ValidationErrorCodes.INVAL_LIST_ENTRY_MSG} {error_info[0]}"
            case ValidationErrorCodes.UNEXP_FIELD:
                msg = f"{ValidationErrorCodes.UNEXP_FIELD_MSG} {error_info[0]}"
            case ValidationErrorCodes.CHEM_NOT_FOUND:
                msg = f"{ValidationErrorCodes.CHEM_NOT_FOUND_MSG} {error_info[0]}"
            case ValidationErrorCodes.WRONG_DATE_FORMAT:
                msg = f"{ValidationErrorCodes.WRONG_DATE_FORMAT_MSG} {error_info[0]}"
            case ValidationErrorCodes.MISSING_COMP:
                msg = f"{ValidationErrorCodes.MISSING_COMP_MSG} {error_info[0]}"
            case ValidationErrorCodes.LOT_NOT_FOUND:
                msg = f"{ValidationErrorCodes.LOT_NOT_FOUND_MSG} {error_info[0]}"
            case ValidationErrorCodes.CHEM_DUPLICATE:
                msg = f"{ValidationErrorCodes.CHEM_DUPLICATE_MSG} {error_info[0]}"
            case ValidationErrorCodes.INVALID_ID:
                msg = f"{ValidationErrorCodes.INVALID_ID_MSG} {error_info[0]}"
            case ValidationErrorCodes.MISS_REQ_VALUE:
                msg = f"{ValidationErrorCodes.MISS_REQ_VALUE_MSG} {error_info[0]}"
            case ValidationErrorCodes.LIST_DUPLICATE:
                msg = f"{ValidationErrorCodes.LIST_DUPLICATE_MSG} {error_info[0]}"
            case ValidationErrorCodes.LIST_NOT_FOUND:
                msg = f"{ValidationErrorCodes.LIST_NOT_FOUND_MSG} {error_info[0]}"
        return msg

class ListsSchema():
    """
    This class controls the lists collection, which stores lists of validated
    values for various fields that end-users interact with. This helps to harmonize
    data entry across all users and prevent entry error.

    Each list is queried and returned at the time the getter is called to ensure
    up-to-date information is provided.

    ListsSchema.LIST_NAME_KEY is used as the functional primary key to prevent
    duplication, though MongoDB's "_id" is left in place.
    """
    # Schema-level class parameters
    LIST_ID_KEY = "_id"
    LIST_NAME_KEY = "Name"
    LIST_ENT_KEY = "List_entries"
    LIST_ENTRY_TYPE = str

    LIST_SCHEMA = {
        LIST_NAME_KEY: str,
        LIST_ENT_KEY: [
            "list entry",
            "list entry"
        ]
    }  
    
    def __init__(self, data={}, lists_collection=None):
        self._list_request_data = data
        self._lists_collection = lists_collection
        self._check = HelperFunctions()
        self._errs = ValidationErrorCodes()
        
        # Pop the self.LIST_ID_KEY to clean up for validation
        if self.LIST_ID_KEY in self._list_request_data:
            self.__list_req_id = self._list_request_data.pop(self.LIST_ID_KEY)
        # Currently handled above while I use MongoDB's "_id" as the primary key, but that won't always be the case.
        if "_id" in self._list_request_data:
            self.__mongo_id = self._list_request_data.pop("_id")

    # Today I learned about a drawback to Python not being a compiled language.
    # I want list "Name"s (primary keys) linked to field definitions in ChemicalSchema
    # which is defined AFTER ListSchema. This was my workaround to make that happen.
    @classmethod
    def CLASSIF_LIST_KEY(cls):
        return ChemicalSchema.CLASSIF_KEY
    
    @classmethod
    def CONT_TYPES_LIST_KEY(cls):
        return ChemicalSchema.CONT_TYPE_KEY
    
    @classmethod
    def MANU_LIST_KEY(cls):
        return ChemicalSchema.MANU_KEY
    
    @classmethod
    def SOURCES_LIST_KEY(cls):
        return ChemicalSchema.SOURCE_KEY
    
    @classmethod
    def STOR_COND_LIST_KEY(cls):
        return ChemicalSchema.STORAGE_KEY
    
    @classmethod
    def UNITS_LIST_KEY(cls):
        return ChemicalSchema.UNIT_KEY

    @property
    def storage_conditions(self):
        storage_conditions = app.lists.find_one(
            {ListsSchema.LIST_NAME_KEY: ListsSchema.STOR_COND_LIST_KEY()}
        )
        
        return storage_conditions[ListsSchema.LIST_ENT_KEY]
    
    @property
    def units(self):
        units = app.lists.find_one(
            {ListsSchema.LIST_NAME_KEY: ListsSchema.UNITS_LIST_KEY()}
        )
        
        return units[ListsSchema.LIST_ENT_KEY]
    
    @property
    def containers(self):
        containers = app.lists.find_one(
            {ListsSchema.LIST_NAME_KEY: ListsSchema.CONT_TYPES_LIST_KEY()}
        )
        
        return containers[ListsSchema.LIST_ENT_KEY]
    
    @property
    def sources(self):
        sources = app.lists.find_one(
            {ListsSchema.LIST_NAME_KEY: ListsSchema.SOURCES_LIST_KEY()}
        )

        return sources[ListsSchema.LIST_ENT_KEY]
    
    @property
    def classifications(self):
        classifications = app.lists.find_one(
            {ListsSchema.LIST_NAME_KEY: ListsSchema.CLASSIF_LIST_KEY()}
        )
        
        return classifications[ListsSchema.LIST_ENT_KEY]
    
    @property
    def manufacturers(self):
        manufacturers = app.lists.find_one(
            {ListsSchema.LIST_NAME_KEY: ListsSchema.MANU_LIST_KEY()}
        )
        
        return manufacturers[ListsSchema.LIST_ENT_KEY]
    
    @staticmethod
    def check_list_name_exist(list_name):
        # Checks to see if a list already exists with a given name.
        # Returns all matching records, though there should be either only
        # one or none that match.

        result = list(app.lists.find(
            {ListsSchema.LIST_NAME_KEY: list_name}
        ))

        return result

    def validate_list_form(self, request_method):
        # This function is designed to short-circuit at the first error detection

        error_info = [None, 0]    # [str(affected fields), int(error_code)]
        
        if error_info[0] == None:
            # Check for extra keys
            request_keys = HelperFunctions.get_schema_keys(
                self._list_request_data
            )
            schema_keys = HelperFunctions.get_schema_keys(
                self.LIST_SCHEMA
            )

            extra_keys = [key for key in request_keys[0] if not key in schema_keys[0]]

            if extra_keys:
                error_info = [extra_keys, self._errs.UNEXP_FIELD]
        
        # Validate types and existence of fields and values
        if error_info[0] == None:
            for key in self.LIST_SCHEMA:
                if key == self.LIST_NAME_KEY:
                    if self._check.miss_req_field(key, self._list_request_data):
                        error_info = [key, self._errs.MISS_REQ_FIELD]
                        break
                    elif self._check.miss_req_value(self._list_request_data[key]):
                        error_info = [key, self._errs.MISS_REQ_VALUE]
                        break
                    elif self._check.wrong_type(self._list_request_data[key], self.LIST_SCHEMA[key]):
                        error_info = [key, self._errs.WRONG_TYPE]
                        break
                elif key == self.LIST_ENT_KEY:
                    if self._check.miss_req_field(key, self._list_request_data):
                        error_info = [key, self._errs.MISS_REQ_FIELD]
                        break
                    elif self._check.miss_req_value(self._list_request_data[key]):
                        error_info = [key, self._errs.MISS_REQ_VALUE]
                        break
                    elif self._check.wrong_type(self._list_request_data[key], self.LIST_SCHEMA[key]):
                        error_info = [key, self._errs.WRONG_TYPE]
                        break
                    for entry in self._list_request_data[key]:
                        if self._check.wrong_type(entry, self.LIST_ENTRY_TYPE):
                            error_info = [f"List entry: entry = {str(entry)}", self._errs.WRONG_TYPE]
                            break
                
                if not error_info[0] == None:
                    # Break outer loop is inner loop finds error.
                    # Redundant in current schema; future-proofing.
                    break
        
        # Check for existence or non-existence of requested list name
        if error_info[0] == None:
            if request_method.upper() == "POST":
                if ListsSchema.check_list_name_exist(
                    self._list_request_data[self.LIST_NAME_KEY]
                ):
                    error_info = [
                        self._list_request_data[self.LIST_NAME_KEY],
                        self._errs.LIST_DUPLICATE
                    ]
            elif request_method.upper() == "PUT":
                if not ListsSchema.check_list_name_exist(
                    self._list_request_data[self.LIST_NAME_KEY]
                ):
                    error_info = [
                        self._list_request_data[self.LIST_NAME_KEY],
                        self._errs.LIST_NOT_FOUND
                    ]

        return error_info

    def build_list_record(self):
        # Build dictionary object to add new list record using mandatory schema
        record = {}
        entries = []

        record[self.LIST_NAME_KEY] = str(self._list_request_data[self.LIST_NAME_KEY])
        for entry in self._list_request_data[self.LIST_ENT_KEY]:
            entries.append(str(entry))
        record[self.LIST_ENT_KEY] = entries

        return record

class ChemicalSchema():
    # Explain what a chemical class is as opposed to a lot. Explain why the addition of chemicals
    # and lots harmonizes data despite creating some redundancy, and why the addition of lots and
    # chemicals are isolated actions.
    CHEM_ID_KEY = "_id"    # Using MongoDB's _id field as the primary key for now
    NAME_KEY = "Name"
    CAS_KEY = "CAS_Number"
    CLASSIF_KEY = "Classification"
    STORAGE_KEY = "Storage_Condition"
    SOURCE_KEY = "Source"
    
    PURCH_FIELD_KEY = "Purchased_Fields"
    MANU_KEY = "Manufacturer"
    MANU_PN_KEY = "Manufacturer_Part_Number"
    AMT_KEY = "Amount"
    UNIT_KEY = "Units"
    CONT_TYPE_KEY = "Container_Type"

    PREP_FIELD_KEY = "Prepared_Fields"
    METH_REF_KEY = "Method_Step_Reference"

    AVAIL_TOTAL_KEY = "Available_Total"    # Added only at document creation
    AVAIL_OPEN_KEY = "Available_Open"    # Added only at document creation

    CHEMICAL_SCHEMA = {
        NAME_KEY: str,
        CAS_KEY: str,
        CLASSIF_KEY: str,
        STORAGE_KEY: str,
        SOURCE_KEY: str,

        PURCH_FIELD_KEY: {
            MANU_KEY: str,
            MANU_PN_KEY: str,
            AMT_KEY: [float, int],    # Calculations with amounts must be performed with Decimal()
            UNIT_KEY: str,
            CONT_TYPE_KEY: str,
        },

        PREP_FIELD_KEY: {
            METH_REF_KEY: str
        }
    }

    def __init__(self, data, chemicals_collection, lots_collection):
        # Single underscore prevents name mangling (easier to call in child class)
        self._chem_request_data = data
        self._chemicals_collection = chemicals_collection
        self._lots_collection = lots_collection
        self._field_lists = ListsSchema()
        self._check = HelperFunctions()
        self._errs = ValidationErrorCodes()
        
        # These fields will be stored as parameters and removed from
        # self._chem_request_data to allow reuse of data validation for both POST and PUT.
        # They aren't all used but are preserved.
        if self.CHEM_ID_KEY in self._chem_request_data:
            self.__chem_req_id = self._chem_request_data.pop(self.CHEM_ID_KEY)
        if self.AVAIL_TOTAL_KEY in self._chem_request_data:
            self.__req_total = self._chem_request_data.pop(self.AVAIL_TOTAL_KEY)
        if self.AVAIL_OPEN_KEY in self._chem_request_data:
            self.__req_open = self._chem_request_data.pop(self.AVAIL_OPEN_KEY)
        # Currently handled above while I use MongoDB's "_id" as the primary key, but that won't always be the case.
        if "_id" in self._chem_request_data:
            self.__mongo_id = self._chem_request_data.pop("_id")
    
    @staticmethod
    def query_current_totals(
        chemicals_collection,
        lots_collection,
        chem_ids: List[str],
        update_records=False
    ):
        # This function sets and returns the current avail total and 
        # current avail open for a given chemical_id. It's intended to be called either
        # internally or externally. For PUT requests it's designed to take a list of
        # one chemical primary key and return the aggregate totals. For GET requests
        # it will update the records in the list, though it still returns the totals
        # from the last id edited. The GET request must re-search the database to 
        # pull updated totals
        # 
        # cham_ids is a list of one or more chemical primary keys
        # request_method is a string that should correspond to an HTTP request
        # lots_collection is type pymongo.collection.Collection
        # Update_records instructs the method to update the aggregate fields in the database.
        #    (This is used when in all cases other than POSTing a chemical)
        for id in chem_ids:
            if isinstance(id, str):
                ObjectId(id)
            now = datetime.now(timezone.utc)
            
            current_avail_total = lots_collection.count_documents({
                "$and": [
                    {LotSchema.PARENT_CHEM_ID_KEY: id},
                    {LotSchema.EMPTY_KEY: {"$eq": None}},
                    {LotSchema.EXPIRY_KEY: {"$gt": now}}
                ]
            })

            current_avail_open = lots_collection.count_documents({
                "$and": [
                    {LotSchema.PARENT_CHEM_ID_KEY: id},
                    {LotSchema.EMPTY_KEY: {"$eq": None}},
                    {LotSchema.EXPIRY_KEY: {"$gt": now}},
                    {"$or": [
                        {"$and": [
                            {ChemicalSchema.SOURCE_KEY: "Purchased",
                             LotSchema.OPEN_KEY: {"$ne": None}}
                        ]},
                        {ChemicalSchema.SOURCE_KEY: "Prepared"}]
                    }
                ]
            })

            if update_records == True:
                # Update record in database with new totals
                chemicals_collection.update_one(
                    {ChemicalSchema.CHEM_ID_KEY: id},
                    {"$set": {
                        ChemicalSchema.AVAIL_TOTAL_KEY: current_avail_total,
                        ChemicalSchema.AVAIL_OPEN_KEY: current_avail_open
                    }}
                )

        return {
            ChemicalSchema.AVAIL_TOTAL_KEY: current_avail_total,
            ChemicalSchema.AVAIL_OPEN_KEY: current_avail_open
        }

    def find_chemical_form(self, query, chemicals_collection=None):
        # Returns document from chemicals collection with specified _id
        if chemicals_collection == None:
            chem_data = self._chemicals_collection.find_one(
                query
            )
        else:
            # This method is called in LotSchema.__init__() before self._chemicals_collection
            # is set by LotSchema.__init__().super().__init__(). I don't want to store same
            # collection reference twice.
            chem_data = chemicals_collection.find_one(
                query
            )
        
        return chem_data

    def find_lot_form(self, query, lots_collection):
        lot_data = lots_collection.find_one(
            query
        )

        return lot_data

    def validate_chemical_form(self, request_method):
        """
        Don't forget to include what each error_type means in final docstring

        Future update: Maybe I flatten the request body upon receipt so that 
        I can add each field to a list for validation (req_fields, req-values, req_types, etc.)
        and then I can easily check for one error at a time. Records would then be reconstructed
        in the nested database schema before storage. If I were more experienced then I would've 
        buit it that way from the start. When doing this, store the validated lists query results
        so that each query isn't repeated once per field
        """
        error_info = [None, 0]  # bad_key, error_type
        
        # Validate "Source" field in request first to simplify paths
        if error_info[0] == None:
            if self._check.miss_req_field(self.SOURCE_KEY, self._chem_request_data):
                error_info = [self.SOURCE_KEY, self._errs.MISS_REQ_FIELD]
            elif self._check.miss_req_value(self._chem_request_data[self.SOURCE_KEY]):
                error_info = [self.SOURCE_KEY, self._errs.MISS_REQ_VALUE]
            elif self._check.wrong_type(
                self._chem_request_data[self.SOURCE_KEY],
                self.CHEMICAL_SCHEMA[self.SOURCE_KEY]
                ):
                error_info = [self.SOURCE_KEY, self._errs.WRONG_TYPE]
            elif self._check.inval_list_entry(
                self._chem_request_data[self.SOURCE_KEY],
                self._field_lists.sources
                ):
                error_info = [self.SOURCE_KEY, self._errs.INVAL_LIST_ENTRY]

        # Check for extra fields in request
        if error_info[0] == None: 
            request_keys = HelperFunctions.get_schema_keys(
                self._chem_request_data
                )
            schema_keys = HelperFunctions.get_schema_keys(
                self.CHEMICAL_SCHEMA
                )
            
            if self._chem_request_data[self.SOURCE_KEY] == "Purchased":
                irrelevant_keys = HelperFunctions.get_schema_keys(
                    self.CHEMICAL_SCHEMA[self.PREP_FIELD_KEY]
                    )
                irrelevant_keys[0].append(self.PREP_FIELD_KEY)
            elif self._chem_request_data[self.SOURCE_KEY] == "Prepared":
                irrelevant_keys = HelperFunctions.get_schema_keys(
                    self.CHEMICAL_SCHEMA[self.PURCH_FIELD_KEY]
                    )
                irrelevant_keys[0].append(self.PURCH_FIELD_KEY)
            
            # Remove irrelevant keys (and discard unused return value)
            schema_keys = [key for key in schema_keys[0] if not key in irrelevant_keys[0]]

            extra_keys = [key for key in request_keys[0] if not key in schema_keys]
            
            if extra_keys:
                error_info = [extra_keys, self._errs.UNEXP_FIELD]
        
        # Validate remaining request fields. Assumes "Source" is last shared field.
        if error_info[0] == None:
            for key in self.CHEMICAL_SCHEMA:
                if not key in [self.SOURCE_KEY, self.PURCH_FIELD_KEY, self.PREP_FIELD_KEY]:
                    if self._check.miss_req_field(key, self._chem_request_data):
                        error_info = [key, self._errs.MISS_REQ_FIELD]
                        break
                    elif self._check.miss_req_value(self._chem_request_data[key]):
                        error_info = [key, self._errs.MISS_REQ_VALUE]
                        break
                    elif self._check.wrong_type(self._chem_request_data[key], self.CHEMICAL_SCHEMA[key]):
                        error_info = [key, self._errs.WRONG_TYPE]
                        break
                    elif key == self.CLASSIF_KEY:
                        if self._check.inval_list_entry(
                            self._chem_request_data[key],
                            self._field_lists.classifications
                            ):
                            error_info = [key, self._errs.INVAL_LIST_ENTRY]
                            break
                    elif key == self.STORAGE_KEY:
                        if self._check.inval_list_entry(
                            self._chem_request_data[key],
                            self._field_lists.storage_conditions
                            ):
                            error_info = [key, self._errs.INVAL_LIST_ENTRY]
                            break

                elif key == self.PURCH_FIELD_KEY and \
                    self._chem_request_data[self.SOURCE_KEY] == "Purchased":
                    # Validate "Purchased Fields" itself
                    if self._check.miss_req_field(key, self._chem_request_data):
                        error_info = [key, self._errs.MISS_REQ_FIELD]
                        break
                    elif self._check.miss_req_value(self._chem_request_data[key]):
                        error_info = [key, self._errs.MISS_REQ_VALUE]
                        break
                    elif self._check.wrong_type(
                        self._chem_request_data[key],
                        self.CHEMICAL_SCHEMA[key]
                        ):
                        error_info = [key, self._errs.WRONG_TYPE]
                        break

                    # Validate contents of "Purchased Fields"
                    purch_inner_dict = self.CHEMICAL_SCHEMA[key]
                    req_inner_dict = self._chem_request_data[key]

                    for inner_key in purch_inner_dict:
                        if self._check.miss_req_field(inner_key, req_inner_dict):
                            error_info = [inner_key, self._errs.MISS_REQ_FIELD]
                            break
                        elif self._check.miss_req_value(req_inner_dict[inner_key]):
                            error_info = [inner_key, self._errs.MISS_REQ_VALUE]
                            break
                        elif isinstance(purch_inner_dict[inner_key], list):
                            if self._check.wrong_type(req_inner_dict[inner_key], purch_inner_dict[inner_key]):
                                error_info = [inner_key, self._errs.WRONG_TYPE]
                                break
                        elif self._check.wrong_type(req_inner_dict[inner_key], purch_inner_dict[inner_key]):
                            error_info = [inner_key, self._errs.WRONG_TYPE]
                            break
                        elif inner_key == self.MANU_KEY:
                            if self._check.inval_list_entry(
                                req_inner_dict[inner_key],
                                self._field_lists.manufacturers
                                ):
                                error_info = [inner_key, self._errs.INVAL_LIST_ENTRY]
                                break
                        elif inner_key == self.UNIT_KEY:
                            if self._check.inval_list_entry(
                                req_inner_dict[inner_key],
                                self._field_lists.units
                                ):
                                error_info = [inner_key, self._errs.INVAL_LIST_ENTRY]
                                break
                        elif inner_key == self.CONT_TYPE_KEY:
                            if self._check.inval_list_entry(
                                req_inner_dict[inner_key],
                                self._field_lists.containers
                                ):
                                error_info = [inner_key, self._errs.INVAL_LIST_ENTRY]
                                break
                
                elif key == self.PREP_FIELD_KEY and \
                    self._chem_request_data[self.SOURCE_KEY] == "Prepared":
                    # Validate "Prepared Fields" itself
                    if self._check.miss_req_field(key, self._chem_request_data):
                        error_info = [key, self._errs.MISS_REQ_FIELD]
                        break
                    elif self._check.miss_req_value(self._chem_request_data[key]):
                        error_info = [key, self._errs.MISS_REQ_VALUE]
                        break
                    elif self._check.wrong_type(
                        self._chem_request_data[key],
                        self.CHEMICAL_SCHEMA[key]
                        ):
                        error_info = [key, self._errs.WRONG_TYPE]
                        break

                    # Validate contents of "Prepared Fields"
                    prep_inner_dict = self.CHEMICAL_SCHEMA[key]
                    req_inner_dict = self._chem_request_data[key]

                    for inner_key in prep_inner_dict:
                        if self._check.miss_req_field(inner_key, req_inner_dict):
                            error_info = [inner_key, self._errs.MISS_REQ_FIELD]
                            break
                        elif self._check.miss_req_value(req_inner_dict[inner_key]):
                            error_info = [inner_key, self._errs.MISS_REQ_VALUE]
                            break
                        elif self._check.wrong_type(req_inner_dict[inner_key], prep_inner_dict[inner_key]):
                            error_info = [inner_key, self._errs.WRONG_TYPE]
                            break

                if not error_info[0] == None:
                    # This is in the event that inner loops found invalid data
                    break

        if error_info[0] == None:
            # Chemical record existence validation
            # This comes after form validation because the form values are used in the queries.
            if request_method.upper() == "POST":
                # Check to ensure the requested chemical doesn't already have a template
                if self.PURCH_FIELD_KEY in self._chem_request_data:
                    req_purch_fields = self._chem_request_data[self.PURCH_FIELD_KEY]

                    chemical_exist_query = {
                        "$and": [
                            # Same purchased material of any name
                            {f"{self.PURCH_FIELD_KEY}.{self.MANU_KEY}": req_purch_fields[self.MANU_KEY]},
                            {f"{self.PURCH_FIELD_KEY}.{self.MANU_PN_KEY}": req_purch_fields[self.MANU_PN_KEY]},
                            {f"{self.PURCH_FIELD_KEY}.{self.AMT_KEY}": req_purch_fields[self.AMT_KEY]},
                            {f"{self.PURCH_FIELD_KEY}.{self.UNIT_KEY}": req_purch_fields[self.UNIT_KEY]},
                            {f"{self.PURCH_FIELD_KEY}.{self.CONT_TYPE_KEY}": req_purch_fields[self.CONT_TYPE_KEY]}
                            ]
                        }
                    
                else:
                    req_prep_fields = self._chem_request_data[self.PREP_FIELD_KEY]

                    chemical_exist_query = {
                        # Same prepared material of any name
                        f"{self.PREP_FIELD_KEY}.{self.METH_REF_KEY}": req_prep_fields[self.METH_REF_KEY]
                        }

                chem_data = self.find_chemical_form(
                    chemical_exist_query, self._chemicals_collection
                    )

                if chem_data:
                    error_info = [
                        chem_data[ChemicalSchema.CHEM_ID_KEY],
                        self._errs.CHEM_DUPLICATE
                    ]

            elif request_method.upper() == "PUT":
                # Check to ensure the requested chemical exists to be updated
                try:
                    chemical_exist_query = {
                        self.CHEM_ID_KEY: ObjectId(self.__chem_req_id)
                    }

                    chem_data = self.find_chemical_form(
                        chemical_exist_query, self._chemicals_collection
                        )
                    
                    if chem_data == None:
                        # Don't overwrite error code if _id key was not valid ObjectId
                        error_info = [str(self.__chem_req_id), self._errs.CHEM_NOT_FOUND]
        
                except InvalidId:
                    error_info = [str(self.__chem_req_id), self._errs.INVALID_ID]
                    
        return error_info

    def build_chem_record(self, req_method, chemical_id=ObjectId()):
        # Build dictionary object to add new record using mandatory schema.
        # req_method = "N/A" if calling from within LotSchema because aggregate fields
        # do not apply in that situation.
        record = {}

        for key in self.CHEMICAL_SCHEMA:
            if self._chem_request_data[self.SOURCE_KEY] == "Purchased":
                if key == self.PURCH_FIELD_KEY:
                    record[key] = {
                        inner_key: self._chem_request_data[key][inner_key] for inner_key in self.CHEMICAL_SCHEMA[key]
                        }
                elif key == self.PREP_FIELD_KEY:
                    continue
                else:
                    record[key] = self._chem_request_data[key]
            elif self._chem_request_data[self.SOURCE_KEY] == "Prepared":
                if key == self.PURCH_FIELD_KEY:
                    continue
                elif key == self.PREP_FIELD_KEY:
                    record[key] = {
                        inner_key: self._chem_request_data[key][inner_key] for inner_key in self.CHEMICAL_SCHEMA[key]
                        }
                else:
                    record[key] = self._chem_request_data[key]

        if req_method.upper() == "POST":
            # Aggregate fields initialized here for POST requests.
            record[self.AVAIL_TOTAL_KEY] = 0
            record[self.AVAIL_OPEN_KEY] = 0
        elif req_method.upper() == "PUT":
            totals = ChemicalSchema.query_current_totals(
                self._chemicals_collection,
                self._lots_collection,
                [chemical_id],
                req_method
            )
            
            record[self.AVAIL_TOTAL_KEY] = totals[self.AVAIL_TOTAL_KEY]
            record[self.AVAIL_OPEN_KEY] = totals[self.AVAIL_OPEN_KEY]

        return record

    def insert_chem_record(
        self,
        chemicals_collection,
        record,
        req_method,
        chemical_id: str = ""
    ):
        if req_method.upper() == "POST":
            result = chemicals_collection.insert_one(record)
        elif req_method.upper() == "PUT":
            result = chemicals_collection.update_one(
                {ChemicalSchema.CHEM_ID_KEY: ObjectId(chemical_id)},
                {"$set": record}
            )
        
        return result

class LotSchema(ChemicalSchema):
    LOT_ID_KEY = "_id" 
    PARENT_CHEM_ID_KEY = "chemical_id"   # Linked to chemicals._id
    COMP_LOT_KEY = "lot_id"    # Links to lots._id. Specifies the lot used in this component.
    MANU_LOT_KEY = "Manufacturer_Lot_Batch_Number"
    OPEN_KEY = "Open_Date"
    EXPIRY_KEY = "Expiry_Date"
    EMPTY_KEY = "Empty_Date"
    PREP_DATE_KEY = "Preparation_Date"
    COMPONENTS_KEY = "Components"

    # Per component added to prepared material.
    # Prepared and purchased component schema are currently redundant, but are left
    # split out to aid potential future updates where they diverge.
    PURCH_COMP_SCHEMA = {
        COMP_LOT_KEY: str,
        # ChemicalSchema.NAME_KEY added at time of lot record construction
        # ChemicalSchema.MANU_KEY added at time of lot record construction
        # ChemicalSchema.MANU_PN_KEY added at time of lot record construction
        # ChemicalSchema.MANU_LOT_KEY added at time of lot record construction
        ChemicalSchema.AMT_KEY: ChemicalSchema.CHEMICAL_SCHEMA[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.AMT_KEY],    # Calculations with amounts must be performed with Decimal()
        ChemicalSchema.UNIT_KEY: ChemicalSchema.CHEMICAL_SCHEMA[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.UNIT_KEY]
        # EXPIRY_KEY added at time of lot record construction
        }
    
    PREP_COMP_SCHEMA = {
        COMP_LOT_KEY: str,
        # ChemicalSchema.NAME_KEY added at time of lot record construction
        # ChemicalSchema.METH_REF_KEY added at time of lot record creation
        ChemicalSchema.AMT_KEY: ChemicalSchema.CHEMICAL_SCHEMA[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.AMT_KEY],
        ChemicalSchema.UNIT_KEY: ChemicalSchema.CHEMICAL_SCHEMA[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.UNIT_KEY]
        # EXPIRY_KEY added at time of lot record construction
    }
    
    LOT_SCHEMA = {
        ChemicalSchema.PURCH_FIELD_KEY: {
            PARENT_CHEM_ID_KEY: str,
            MANU_LOT_KEY: str,
            OPEN_KEY: str,
            EXPIRY_KEY: str,
            EMPTY_KEY: str
        },
        ChemicalSchema.PREP_FIELD_KEY: {
            PARENT_CHEM_ID_KEY: str,
            ChemicalSchema.AMT_KEY: ChemicalSchema.CHEMICAL_SCHEMA[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.AMT_KEY],    # Calculations with amounts must be performed with Decimal()
            ChemicalSchema.UNIT_KEY: ChemicalSchema.CHEMICAL_SCHEMA[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.UNIT_KEY],
            ChemicalSchema.CONT_TYPE_KEY: ChemicalSchema.CHEMICAL_SCHEMA[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.CONT_TYPE_KEY],
            PREP_DATE_KEY: str,
            EXPIRY_KEY: str,
            EMPTY_KEY: str,
            COMPONENTS_KEY: [
                PURCH_COMP_SCHEMA
                ]
        }
    }

    def __init__(self, data, chemicals_collection, lots_collection):
        self._lot_request_data = data
        self._check = HelperFunctions()
        self._errs = ValidationErrorCodes()

        # Used to short-circuit validation if chemical not found
        self._chem_id_error = [None, 0]    # Field name, ValidationErrorCodes error code

        # Pop _id to strip _lot_request_data for validation and build.
        if self.LOT_ID_KEY in self._lot_request_data:
            self.__lot_req_id = self._lot_request_data.pop(self.LOT_ID_KEY)
        # Currently handled above while I use MongoDB's "_id" as the primary key, but that won't always be the case.
        if "_id" in self._lot_request_data:
            self.__mongo_id = self._lot_request_data.pop("_id")
        
        try:
            # Check for and return the related chemical form's data. This is cleaned in ChemicalSchema.__init__().
            # The chemicals and lots collections are stored in the ChemicalSchema class, so they have to be passed
            # using the parameter names in LotSchema.__init__() before they can be referenced using "self."
            if self._check.miss_req_field(self.PARENT_CHEM_ID_KEY, self._lot_request_data):
                self._chem_id_error = [
                    self.PARENT_CHEM_ID_KEY,
                    self._errs.MISS_REQ_FIELD
                ]
                raise KeyError
            
            elif self._check.miss_req_value(self._lot_request_data[self.PARENT_CHEM_ID_KEY]):
                self._chem_id_error = [
                    self.PARENT_CHEM_ID_KEY,
                    self._errs.MISS_REQ_VALUE
                ]
                raise ValueError
            
            elif self._check.wrong_type(
                self._lot_request_data[self.PARENT_CHEM_ID_KEY],
                # This checks the type using one schema, but both s chema should always have same type.
                self.LOT_SCHEMA[self.PURCH_FIELD_KEY][self.PARENT_CHEM_ID_KEY]
            ):
                self._chem_id_error = [
                    self.PARENT_CHEM_ID_KEY,
                    self._errs.WRONG_TYPE
                ]
                raise TypeError
            
            id_exist_query = {
            self.CHEM_ID_KEY: ObjectId(self._lot_request_data[self.PARENT_CHEM_ID_KEY])
            }

            chem_data = self.find_chemical_form(id_exist_query, chemicals_collection)

            if not chem_data:
                self._chem_id_error = [
                    str(self._lot_request_data[self.PARENT_CHEM_ID_KEY]),
                    self._errs.CHEM_NOT_FOUND
                ]
                raise FileNotFoundError
            
            super().__init__(
                chem_data,
                chemicals_collection,
                lots_collection
            )
            
            # In a LotSchema instance, super().__init__() conveniently cleans up a chemical
            # query result, but the ChemicalSchema name self._chem_data may be confusing.
            # Rename to self._chem_data, which makes more sense in the context of
            # LotSchema's use case.
            self._chem_data = self._chem_request_data
        
        except InvalidId:
            self._chem_id_error = [
                str(self._lot_request_data[self.PARENT_CHEM_ID_KEY,]),
                self._errs.INVALID_ID
            ]
        
        # For the following exceptions: error has been stored. validate_lot_form method
        #  will catch it immediately.
        except KeyError:
            pass
        except ValueError:
            pass
        except TypeError:
            pass
        except FileNotFoundError:
            pass
        
    def validate_lot_form(self, request_method):
        """
        Internal lot number validation would be added when there's a reliable system to generate internal lot numbers
        
        See note in validate_chemical_form for future upgrade idea.
        """
        # Now is the time to validate error encountered in LotSchema.__init__()
        error_info = self._chem_id_error

        # Check for extra keys in request
        if error_info[0] == None:
            request_keys = HelperFunctions.get_schema_keys(
                self._lot_request_data
            )
            
            if self._chem_data[self.SOURCE_KEY] == "Purchased":
                schema_keys = HelperFunctions.get_schema_keys(
                    self.LOT_SCHEMA[self.PURCH_FIELD_KEY]
                )
            elif self._chem_data[self.SOURCE_KEY] == "Prepared":
                schema_keys = HelperFunctions.get_schema_keys(
                    self.LOT_SCHEMA[self.PREP_FIELD_KEY]
                )
                if request_keys[1] == 0:
                    error_info = ["", self._errs.MISSING_COMP]
                elif not request_keys[1] == 1:
                    # Add the correct number of duplicates for component keys from schema
                    # NOTE: This does not currently acconut for whether the requested components
                    # are purchased or prepared components. It does not matter with the current 
                    # schema, but they will need to be de-coupled if the requests for purchased 
                    # and prepared components diverge.
                    for i in range(2, (request_keys[1] + 1)):
                        schema_keys[0].append(LotSchema.COMPONENTS_KEY)
                        for key in self.PREP_COMP_SCHEMA:
                            schema_keys[0].append(f"{self.COMPONENTS_KEY}.{key}")

            extra_keys = [key for key in request_keys[0] if not key in schema_keys[0]]
            
            if extra_keys:
                if error_info[0] == None:
                    # Don't override error if components are missing.
                    error_info = [extra_keys, self._errs.UNEXP_FIELD]
        
        # Validate fields in request
        #
        ## PARENT_CHEM_ID validated in __init__() for type and existence in database.
        ##
        ## Note that a lot itself can have a prepared or purchased parent chemical template,
        ## but so also can the components of a prepared lot have a purchased or prepared parent
        ## chemical template.
        if error_info[0] == None:
            if self._chem_data[ChemicalSchema.SOURCE_KEY] == "Purchased":
                purch_schema = self.LOT_SCHEMA[ChemicalSchema.PURCH_FIELD_KEY]
                for key in purch_schema:
                    if key in [self.OPEN_KEY, self.EXPIRY_KEY, self.EMPTY_KEY]:
                        if self._check.miss_req_field(
                            key,
                            self._lot_request_data
                        ):
                            error_info = [key, self._errs.MISS_REQ_FIELD]
                            break
                        elif (key in [self.OPEN_KEY, self.EMPTY_KEY]) and \
                            self._lot_request_data[key] == None:
                            # These VALUES are optional. Skip remaining checks.
                            continue
                        elif self._check.miss_req_value(
                            self._lot_request_data[key]
                        ):
                            # Check expiry date for value presence. Redundant for other two date fields.
                            error_info = [key, self._errs.MISS_REQ_VALUE]
                            break
                        elif self._check.wrong_type(
                            self._lot_request_data[key],
                            purch_schema[key]
                        ):
                            error_info = [key, self._errs.WRONG_TYPE]
                            break
                        else:
                            try:
                                self._check.to_datetime_utc(
                                    self._lot_request_data[key]
                                )
                            except ValueError:
                                error_info = [key, self._errs.WRONG_DATE_FORMAT]
                                break

                    elif self._check.miss_req_field(
                        key,
                        self._lot_request_data
                    ):
                        error_info = [key, self._errs.MISS_REQ_FIELD]
                        break
                    elif self._check.miss_req_value(self._lot_request_data[key]) and \
                        (not key in [self.OPEN_KEY, self.EMPTY_KEY]):
                            error_info = [key, self._errs.MISS_REQ_VALUE]
                            break
                    elif self._check.wrong_type(self._lot_request_data[key], purch_schema[key]):
                        error_info = [key, self._errs.WRONG_TYPE]
                        break
            elif self._chem_data[ChemicalSchema.SOURCE_KEY] == "Prepared":
                prep_schema = self.LOT_SCHEMA[ChemicalSchema.PREP_FIELD_KEY]
                for key in prep_schema:
                    if key in [self.PREP_DATE_KEY, self.EXPIRY_KEY, self.EMPTY_KEY]:
                        if self._check.miss_req_field(
                            key,
                            self._lot_request_data
                        ):
                            error_info = [key, self._errs.MISS_REQ_FIELD]
                            break
                        elif (key == self.EMPTY_KEY) and \
                            self._lot_request_data[key] == None:
                            # This VALUE is optional. Skip remaining checks.
                            continue
                        elif self._check.miss_req_value(
                            self._lot_request_data[key]
                        ):
                            # Check expiry date. Redundant for other two date fields.
                            error_info = [key, self._errs.MISS_REQ_VALUE]
                            break
                        elif self._check.wrong_type(
                            self._lot_request_data[key],
                            prep_schema[key]
                        ):
                            error_info = [key, self._errs.WRONG_TYPE]
                            break
                        else:
                            try:
                                self._check.to_datetime_utc(
                                    self._lot_request_data[key]
                                )
                            except ValueError:
                                error_info = [key, self._errs.WRONG_DATE_FORMAT]
                                break

                    elif isinstance(prep_schema[key], list):
                        # "Components" and "Amount" both have embedded lists as values
                        if key == self.COMPONENTS_KEY:
                            # Validate "Components" itself
                            if self._check.miss_req_field(
                                key,
                                self._lot_request_data
                            ):
                                error_info = [key, self._errs.MISS_REQ_FIELD]
                                break
                            elif self._check.miss_req_value(
                                self._lot_request_data[key]
                            ):
                                error_info = [key, self._errs.MISS_REQ_VALUE]
                                break
                            elif self._check.wrong_type(
                                self._lot_request_data[key],
                                prep_schema[key]
                            ):
                                error_info = [key, self._errs.WRONG_TYPE]
                                break
                            
                            # Loop through components and validate each
                            for component in self._lot_request_data[key]:
                                comp_index = self._lot_request_data[key].index(component)
                                req_comp_dict = self._lot_request_data[key][comp_index]
                                
                                # Validate LotSchema.COMP_LOT_KEY first to then determine whether component gets
                                # prepared lot fields or purchased lot fields from the parent chemical template.
                                if self._check.miss_req_field(
                                    LotSchema.COMP_LOT_KEY,
                                    req_comp_dict
                                ):
                                    error_info = [LotSchema.COMP_LOT_KEY, self._errs.MISS_REQ_FIELD]
                                    break
                                elif self._check.miss_req_value(
                                    req_comp_dict[LotSchema.COMP_LOT_KEY]
                                ):
                                        error_info = [LotSchema.COMP_LOT_KEY, self._errs.MISS_REQ_VALUE]
                                        break
                                elif self._check.wrong_type(
                                    req_comp_dict[LotSchema.COMP_LOT_KEY],
                                    prep_schema[LotSchema.COMPONENTS_KEY][0][LotSchema.COMP_LOT_KEY]
                                ):
                                    error_info = [LotSchema.COMP_LOT_KEY, self._errs.WRONG_TYPE]
                                    break
                                
                                # Validate that requested component chemical has an existing lot record
                                # available for use.
                                try:
                                    lot_exist_query = {
                                        self.LOT_ID_KEY: ObjectId(
                                            req_comp_dict[self.COMP_LOT_KEY]
                                        )
                                    }
                                    
                                    # Validate component's parent_chemical_id is a valid ObjectId() type
                                    lot_data = self.find_lot_form(lot_exist_query, self._lots_collection)

                                    if error_info[0] == None:
                                        if not lot_data:
                                            # Trigger error if no lot exists for requested component
                                            error_info = [
                                                f"{key}.Component #{comp_index + 1}.{LotSchema.COMP_LOT_KEY}",
                                                self._errs.LOT_NOT_FOUND
                                            ]
                                            break
                                
                                except InvalidId:
                                    error_info = [
                                        f"{key}.Component #{comp_index + 1}.{LotSchema.COMP_LOT_KEY}",
                                        self._errs.INVALID_ID
                                    ]

                                # Expect different request fields for purchased and prepared components
                                ## This isn't currently the case but will make it easier to implement in the future
                                if lot_data[LotSchema.SOURCE_KEY] == "Purchased":
                                    schema_comp_dict = self.PURCH_COMP_SCHEMA
                                elif lot_data[LotSchema.SOURCE_KEY] == "Prepared":
                                    schema_comp_dict = self.PREP_COMP_SCHEMA

                                for subkey in schema_comp_dict:
                                    # Refer to component by # in case "Name" field missing. "Name" should be validated
                                    # upstream, but this keeps it robust.
                                    if subkey == self.COMP_LOT_KEY:
                                        continue
                                    if isinstance(schema_comp_dict[subkey], list):   # "Amount" field
                                        if self._check.miss_req_field(
                                            subkey,
                                            req_comp_dict
                                        ):
                                            error_info = [
                                                f"{key}.Component #{comp_index + 1}.{subkey}",
                                                self._errs.MISS_REQ_FIELD
                                            ]
                                            break
                                        elif self._check.miss_req_value(
                                            req_comp_dict[subkey]
                                        ):
                                            error_info = [
                                                f"{key}.Component #{comp_index + 1}.{subkey}",
                                                self._errs.MISS_REQ_VALUE
                                            ]
                                            break
                                        elif self._check.wrong_type(
                                            req_comp_dict[subkey],
                                            schema_comp_dict[subkey]
                                        ):
                                            error_info = [
                                                f"{key}.Component #{comp_index + 1}.{subkey}",
                                                self._errs.WRONG_TYPE
                                            ]
                                            break
                                    else:
                                        if self._check.miss_req_field(
                                            subkey, 
                                            req_comp_dict
                                        ):
                                            error_info = [
                                                f"{key}.Component #{comp_index + 1}.{subkey}",
                                                self._errs.MISS_REQ_FIELD
                                            ]
                                            break
                                        elif self._check.miss_req_value(
                                            req_comp_dict[subkey]
                                        ):
                                            error_info = [
                                                f"{key}.Component #{comp_index + 1}.{subkey}",
                                                self._errs.MISS_REQ_VALUE
                                            ]
                                            break
                                        elif self._check.wrong_type(
                                            req_comp_dict[subkey],
                                            schema_comp_dict[subkey]
                                        ):
                                            error_info = [
                                                f"{key}.Component #{comp_index + 1}.{subkey}",
                                                self._errs.WRONG_TYPE
                                            ]
                                            break
                                        elif subkey == self.UNIT_KEY:
                                            if self._check.inval_list_entry(
                                                req_comp_dict[subkey],
                                                self._field_lists.units
                                                ):
                                                error_info = [
                                                    f"{key}.Component #{comp_index + 1}.{subkey}",
                                                    self._errs.INVAL_LIST_ENTRY
                                                ]
                                                break
                                

                                if not error_info[0] == None:
                                    # This is in the event that inner loops found invalid data
                                    break

                        else:
                            # Valiate "Amount" field
                            if self._check.miss_req_field(
                                key,
                                self._lot_request_data
                            ):
                                error_info = [key, self._errs.MISS_REQ_FIELD]
                                break
                            elif self._check.miss_req_value(
                                self._lot_request_data[key]
                            ):
                                error_info = [key, self._errs.MISS_REQ_VALUE]
                                break
                            elif self._check.wrong_type(
                                self._lot_request_data[key],
                                prep_schema[key]
                            ):
                               error_info = [key, self._errs.WRONG_TYPE]
                               break
                    elif self._check.miss_req_field(
                        key, self._lot_request_data
                    ):
                        error_info = [key, self._errs.MISS_REQ_FIELD]
                        break
                    elif self._check.miss_req_value(
                        self._lot_request_data[key]
                    ):
                        error_info = [key, self._errs.MISS_REQ_VALUE]
                        break
                    elif self._check.wrong_type(
                        self._lot_request_data[key],
                        prep_schema[key]
                    ):
                        error_info = [key, self._errs.WRONG_TYPE]
                        break
                    elif key == self.UNIT_KEY:
                        if self._check.inval_list_entry(
                            self._lot_request_data[key],
                            self._field_lists.units
                        ):
                            error_info = [key, self._errs.INVAL_LIST_ENTRY]
                            break
                    elif key == self.CONT_TYPE_KEY:
                        if self._check.inval_list_entry(
                            self._lot_request_data[key],
                            self._field_lists.containers
                        ):
                            error_info = [key, self._errs.INVAL_LIST_ENTRY]
                            break
                    
                    if not error_info[0] == None:
                        # This is in the event that inner loops found invalid data
                        break
        
        if error_info[0] == None:        
            if request_method.upper() == "PUT":
                # Check to ensure the requested lot exists to be updated
                try:
                    lot_exist_query = {
                        self.LOT_ID_KEY: ObjectId(self.__lot_req_id)
                    }

                    lot_data = self.find_lot_form(
                    lot_exist_query, self._lots_collection
                    )
                        
                    
                    if lot_data == None:
                        error_info = [
                            str(self.__lot_req_id),
                            self._errs.LOT_NOT_FOUND
                            ]
                        
                except InvalidId:
                    error_info = [self.__lot_req_id, self._errs.INVALID_ID]
        
        return error_info
    
    def build_lot_record(self):
        # Build dictionary object to insert new lot document using mandatory schema
        
        record = {}
        # Fetch shared fields from chemical schema
        request = self._lot_request_data
        chem_fields = self.build_chem_record("N/A", self._chem_data)

        # Build fields with same order in purchased or prepared records
        record[self.PARENT_CHEM_ID_KEY] = ObjectId(request[self.PARENT_CHEM_ID_KEY])
        record[self.NAME_KEY] = chem_fields[self.NAME_KEY]
        record[self.CAS_KEY] = chem_fields[self.CAS_KEY]

        # Build fields after structures diverge
        if self._chem_data[ChemicalSchema.SOURCE_KEY] == "Purchased":
            chem_purch_obj = chem_fields[self.PURCH_FIELD_KEY]

            record[self.CLASSIF_KEY] = chem_fields[self.CLASSIF_KEY]
            record[self.STORAGE_KEY] = chem_fields[self.STORAGE_KEY]
            record[self.SOURCE_KEY] = chem_fields[self.SOURCE_KEY]

            record[self.PURCH_FIELD_KEY] = {}
            rec_purch_flds = record[self.PURCH_FIELD_KEY]
            rec_purch_flds[self.MANU_KEY] = chem_purch_obj[self.MANU_KEY]
            rec_purch_flds[self.MANU_PN_KEY] = chem_purch_obj[self.MANU_PN_KEY]
            rec_purch_flds[self.MANU_LOT_KEY] = request[self.MANU_LOT_KEY]
            rec_purch_flds[self.AMT_KEY] = chem_purch_obj[self.AMT_KEY]
            rec_purch_flds[self.UNIT_KEY] = chem_purch_obj[self.UNIT_KEY]
            rec_purch_flds[self.CONT_TYPE_KEY] = chem_purch_obj[self.CONT_TYPE_KEY]

            if request[self.OPEN_KEY]:
                record[self.OPEN_KEY] = self._check.to_datetime_utc(request[self.OPEN_KEY])
            else:
                record[self.OPEN_KEY] = None
            record[self.EXPIRY_KEY] = self._check.to_datetime_utc(request[self.EXPIRY_KEY])
            if request[self.EMPTY_KEY]:
                record[self.EMPTY_KEY] = self._check.to_datetime_utc(request[self.EMPTY_KEY])
            else:
                record[self.EMPTY_KEY] = None
            
        elif self._chem_data[ChemicalSchema.SOURCE_KEY] == "Prepared":
            chem_purch_flds = chem_fields[self.PREP_FIELD_KEY]

            record[self.AMT_KEY] = request[self.AMT_KEY]
            record[self.UNIT_KEY] = request[self.UNIT_KEY]
            record[self.CONT_TYPE_KEY] = request[self.CONT_TYPE_KEY]
            record[self.CLASSIF_KEY] = chem_fields[self.CLASSIF_KEY]
            record[self.STORAGE_KEY] = chem_fields[self.STORAGE_KEY]
            record[self.SOURCE_KEY] = chem_fields[self.SOURCE_KEY]

            record[self.PREP_FIELD_KEY] = {}
            rec_prep_flds = record[self.PREP_FIELD_KEY]
            rec_prep_flds[self.METH_REF_KEY] = chem_purch_flds[self.METH_REF_KEY]

            record[self.PREP_DATE_KEY] = self._check.to_datetime_utc(request[self.PREP_DATE_KEY])
            record[self.EXPIRY_KEY] = self._check.to_datetime_utc(request[self.EXPIRY_KEY])
            if request[self.EMPTY_KEY]:
                record[self.EMPTY_KEY] = self._check.to_datetime_utc(request[self.EMPTY_KEY])
            else:
                record[self.EMPTY_KEY] = None

            record[self.COMPONENTS_KEY] = []

            # Insert each component from the lot record request
            # Lot record info shared with parent chemical is pulled from chemical database
            # where applicable to prevent entry errors
            for component in request[self.COMPONENTS_KEY]:
                component_attrs = {}

                # primary key already evaluated to be valid.
                component_lot_query = {
                    self.LOT_ID_KEY: ObjectId(component[self.COMP_LOT_KEY])
                }

                comp_lot_rec = self.find_lot_form(component_lot_query, self._lots_collection)

                # Determine whether to build component as purchased or prepared material
                if comp_lot_rec[LotSchema.SOURCE_KEY] == "Purchased":
                    comp_lot_rec_purch = comp_lot_rec[self.PURCH_FIELD_KEY]

                    component_attrs[self.COMP_LOT_KEY] = ObjectId(
                        component[self.COMP_LOT_KEY]
                        )
                    component_attrs[self.NAME_KEY] = comp_lot_rec[self.NAME_KEY]
                    component_attrs[self.MANU_KEY] = comp_lot_rec_purch[self.MANU_KEY]
                    component_attrs[self.MANU_PN_KEY] = comp_lot_rec_purch[self.MANU_PN_KEY]
                    component_attrs[self.MANU_LOT_KEY] = comp_lot_rec_purch[self.MANU_LOT_KEY]
                    component_attrs[self.AMT_KEY] = component[self.AMT_KEY]
                    component_attrs[self.UNIT_KEY] = component[self.UNIT_KEY]
                    component_attrs[self.EXPIRY_KEY] = \
                        self._check.to_datetime_utc(comp_lot_rec[self.EXPIRY_KEY])

                elif comp_lot_rec[LotSchema.SOURCE_KEY] == "Prepared":
                    comp_lot_rec_prep = comp_lot_rec[self.PREP_FIELD_KEY]

                    component_attrs[self.COMP_LOT_KEY] = ObjectId(
                        component[self.COMP_LOT_KEY]
                        )
                    component_attrs[self.NAME_KEY] = comp_lot_rec[self.NAME_KEY]
                    component_attrs[self.METH_REF_KEY] = comp_lot_rec_prep[self.METH_REF_KEY]
                    component_attrs[self.AMT_KEY] = component[self.AMT_KEY]
                    component_attrs[self.UNIT_KEY] = component[self.UNIT_KEY]
                    component_attrs[self.EXPIRY_KEY] = \
                        self._check.to_datetime_utc(comp_lot_rec[self.EXPIRY_KEY])
                    
                record[self.COMPONENTS_KEY].append(component_attrs)

        return record
    
    def insert_lot_record(
        self,
        chemicals_collection,
        lots_collection,
        record,
        req_method,
        lot_id: str = ""

    ):
        # Update lot record and then update parent chemical aggregate fields
        if req_method.upper() == "POST":
            result = app.lots.insert_one(record)
        
        elif req_method.upper() == "PUT":
            result = app.lots.update_one(
                    {LotSchema.LOT_ID_KEY: ObjectId(lot_id)},
                    {"$set": record}
                )

        ChemicalSchema.query_current_totals(
            chemicals_collection,
            lots_collection,
            [record[LotSchema.PARENT_CHEM_ID_KEY]],
            True
        )
    
        return result









# Fetch all chemical documents
@app.route("/chemicals", methods=["GET"])
def get_all_chemicals():
    # Update aggregate fields to refresh data
    all_chem_ids = [
        chem[ChemicalSchema.CHEM_ID_KEY] for chem in app.chemicals.find(
            {},
            {ChemicalSchema.CHEM_ID_KEY: 1}
        )
    ]

    ChemicalSchema.query_current_totals(
        app.chemicals,
        app.lots,
        all_chem_ids,
        True
    )

    # Find and return refreshed records
    all_chemicals = list(app.chemicals.find())

    for chemical in all_chemicals:
        # Type ObjectId not JSON serializable
        chemical[ChemicalSchema.CHEM_ID_KEY] = str(
            chemical[ChemicalSchema.CHEM_ID_KEY]
        )

    response = jsonify(all_chemicals), 200

    return response

# Add a new chemical according to the database schema
@app.route("/chemicals", methods=["POST"])
def add_chemical():
    data = request.get_json()

    if not data:
        response = jsonify({"error": "Missing request body"}), 400
    else:
        # Validate data in request
        new_chemical = ChemicalSchema(
            copy.deepcopy(data),
            app.chemicals,
            app.lots
        )

        form_val = new_chemical.validate_chemical_form(request.method)

        if form_val[1] == 0:
            record = new_chemical.build_chem_record(request.method)
            result = new_chemical.insert_chem_record(
                app.chemicals,
                record,
                request.method
            )

            response = jsonify({"inserted_id": str(result.inserted_id)}), 201
        else:
            msg = ValidationErrorCodes.gen_val_err_msg(form_val)
            response = jsonify({"error": msg}), 422

    return response

# Fetch a specific chemical by _id
@app.route("/chemicals/<chemical_id>", methods=["GET"])
def get_chemical(chemical_id):
    try:
        chem_doc = app.chemicals.find_one(
            {ChemicalSchema.CHEM_ID_KEY: ObjectId(chemical_id)}
        )

        if not chem_doc:
            response = jsonify({"error": "Not found"}), 404
        else:
            # Update aggregate fields to reflect current state of lot database
            ChemicalSchema.query_current_totals(
                app.chemicals,
                app.lots,
                [chem_doc[ChemicalSchema.CHEM_ID_KEY]],
                True
            )

            # Find and return refreshed record
            chem_doc = app.chemicals.find_one(
                {ChemicalSchema.CHEM_ID_KEY: ObjectId(chemical_id)}
            )
            
            chem_doc[ChemicalSchema.CHEM_ID_KEY] = str(
                chem_doc[ChemicalSchema.CHEM_ID_KEY]
            )
            
            response = jsonify(chem_doc), 200
    except InvalidId:
        response = jsonify({"error": "Invalid ID format"}), 400

    return response

# Update an existing chemical according to the database schema
@app.route("/chemicals/<chemical_id>", methods=["PUT"])
def update_chemical(chemical_id):
    data = request.get_json()
    
    if not ChemicalSchema.CHEM_ID_KEY in data:
        response = jsonify({
            "error": f"Request body missing primary key: {ChemicalSchema.CHEM_ID_KEY}"
        }), 422
    elif not data[ChemicalSchema.CHEM_ID_KEY] == chemical_id:
        response = jsonify({"error": "Request body primary key does not match address " \
            f"<chemical_id>: {data[ChemicalSchema.CHEM_ID_KEY]}, {chemical_id}"}), 422
            
    else:
        # Validate data in request
        updated_chemical = ChemicalSchema(
            copy.deepcopy(data),
            app.chemicals,
            app.lots
        )
        form_val = updated_chemical.validate_chemical_form(request.method)

        if form_val[1] == 0:
            try:
                record = updated_chemical.build_chem_record(
                    request.method,
                    chemical_id
                )

                result = updated_chemical.insert_chem_record(
                    app.chemicals,
                    record,
                    request.method,
                    chemical_id
                )
                
                response = jsonify({"modified_count": str(result.modified_count)}), 200

            except InvalidId:
                # This is a failsafe. validate_chemical_forms() handles this case.
                response = jsonify({"error": "Invalid ID format"}), 400
        elif form_val[1] == 5:
            msg = ValidationErrorCodes.gen_val_err_msg(form_val)
            response = jsonify({"error": msg}), 404
        else:
            msg = ValidationErrorCodes.gen_val_err_msg(form_val)
            response = jsonify({"error": msg}), 422

    return response

# Delete a specific chemical by _id
@app.route("/chemicals/<chemical_id>", methods=["DELETE"])
def delete_chemical(chemical_id):
    try:
        result = app.chemicals.delete_one(
            {ChemicalSchema.CHEM_ID_KEY: ObjectId(chemical_id)}
        )

        if result.deleted_count == 0:
            response = jsonify({"error": "Not found"}), 404
        else:
            response = jsonify({"deleted_count": result.deleted_count}), 204

    except InvalidId:
        response = jsonify({"error": "Invalid ID format"}), 400   
    
    return response

# Fetch all lot documents
@app.route("/lots", methods=["GET"])
def get_all_lots():
    all_lots = list(app.lots.find())
    inval_json_types = (ObjectId, datetime)
    
    # Re-type JSON-incompatible data types to strings
    for lot in all_lots:
        for key in lot:
            if isinstance(lot[key], inval_json_types):
                lot[key] = str(lot[key])
            elif isinstance(lot[key], list) and isinstance(lot[key][0], dict):
                # Iterate through all values of all components
                for component in lot[key]:
                    comp_index = lot[key].index(component)
                    component_dict = lot[key][comp_index]
                    for subkey in component_dict:
                        if isinstance(component_dict[subkey], inval_json_types):
                            component_dict[subkey] = str(component_dict[subkey])

    response = jsonify(all_lots), 200

    return response

# Add a new lot according to the database schema
@app.route("/lots", methods=["POST"])
def add_lot():
    data = request.get_json()

    if not data:
        response = jsonify({"error": "Missing request body"}), 400
    else:
        # Validate data in request
        new_lot = LotSchema(
            copy.deepcopy(data),
            app.chemicals,
            app.lots
        )
        form_val = new_lot.validate_lot_form(request.method)
        
        if form_val[1] == 0:
            record = new_lot.build_lot_record()
            result = new_lot.insert_lot_record(
                app.chemicals,
                app.lots,
                record,
                request.method
            )

            response = jsonify({"inserted_id": str(result.inserted_id)}), 201

        elif form_val[1] == 5 or form_val[1] == 8:
            msg = ValidationErrorCodes.gen_val_err_msg(form_val)
            response = jsonify({"error": msg}), 404

        else:
            msg = ValidationErrorCodes.gen_val_err_msg(form_val)
            response = jsonify({"error": msg}), 422
    
    return response

# Fetch a specific lot by _id
@app.route("/lots/<lot_id>", methods=["GET"])
def get_lot(lot_id):
    try:
        result = app.lots.find_one({LotSchema.LOT_ID_KEY: ObjectId(lot_id)})
        
        if not result:
            response = jsonify({"error": "Not found"}), 404
        else:
            inval_json_types = (ObjectId, datetime)

            # Re-type JSON-incompatible data types to strings
            for key in result:
                if isinstance(result[key], inval_json_types):
                    result[key] = str(result[key])
                elif isinstance(result[key], list) and isinstance(result[key][0], dict):
                    # Iterate through all values of all components
                    for component in result[key]:
                        comp_index = result[key].index(component)
                        component_dict = result[key][comp_index]
                        for subkey in component_dict:
                            if isinstance(component_dict[subkey], inval_json_types):
                                component_dict[subkey] = str(component_dict[subkey])

            response = jsonify(result), 200
    
    except InvalidId:
        response = jsonify({"error": "Invalid ID format"}), 400
    
    return response

# Update a specific lot by _id according to the database schema
@app.route("/lots/<lot_id>", methods=["PUT"])
def update_lot(lot_id):
    data = request.get_json()

    if not LotSchema.LOT_ID_KEY in data:
        response = jsonify({
            "error": f"Request body missing primary key: {LotSchema.LOT_ID_KEY}"
        }), 422
    elif not data[LotSchema.LOT_ID_KEY] == lot_id:
        response = jsonify({"error": "Request body primary key does not match address " \
            f"<lot_id>: {data[LotSchema.LOT_ID_KEY]}, {lot_id}"}), 422
    else:
        # Validate data in request
        updated_lot = LotSchema(
            copy.deepcopy(data),
            app.chemicals,
            app.lots
        )
        form_val = updated_lot.validate_lot_form(request.method)

        if form_val[1] == 0:
            try:
                record = updated_lot.build_lot_record()
                result = updated_lot.insert_lot_record(
                    app.chemicals,
                    app.lots,
                    record,
                    request.method,
                    lot_id
                )

                response = jsonify({"modified_count": str(result.modified_count)}), 200
            
            except InvalidId:
                # This is a failsafe. validate_lot_forms() handles this case.
                response = jsonify({"error": "Invalid ID format"}), 400
        elif form_val[1] == 5 or form_val[1] == 8:
            msg = ValidationErrorCodes.gen_val_err_msg(form_val)
            response = jsonify({"error": msg}), 404
        else:
            msg = ValidationErrorCodes.gen_val_err_msg(form_val)
            response = jsonify({"error": msg}), 422
    
    return response

# Delete a specific lot by _id
@app.route("/lots/<lot_id>", methods=["DELETE"])
def delete_lot(lot_id):
    try:
        result = app.lots.delete_one({LotSchema.LOT_ID_KEY: ObjectId(lot_id)})
       
        if result.deleted_count == 0:
            response = jsonify({"error": "Not found"}), 404
        else:
            response = "", 204

    except InvalidId:
        response = jsonify({"error": "Invalid ID format"}), 400

    return response

# Fetch all list documents
@app.route("/lists", methods=["GET"])
def get_all_lists():
    all_lists = list(app.lists.find(
        {},
        {"_id": 0}
    ))
    
    response = jsonify(all_lists), 200

    return response

# Add a new list document according to the database schema
@app.route("/lists", methods=["POST"])
def add_list():
    data = request.get_json()

    if not data:
        response = jsonify({"error": "Missing request body"}), 400
    else:
        # Validate data in request
        new_list = ListsSchema(
            copy.deepcopy(data),
            app.lists
        )
        form_val = new_list.validate_list_form(request.method)
        
        if form_val[1] == 0:
            record = new_list.build_list_record()
            result = app.lists.insert_one(record)

            response = jsonify({"inserted_id": str(result.inserted_id)}), 201
        else:
            msg = ValidationErrorCodes.gen_val_err_msg(form_val)
            response = jsonify({"error": msg}), 422
    
    return response

# Fetch a specific list by name
@app.route("/lists/<list_name>", methods=["GET"])
def get_list(list_name):
    result = app.lists.find_one(
        {ListsSchema.LIST_NAME_KEY: list_name},
        {ListsSchema.LIST_ID_KEY: 0}
    )
    
    if not result:
        response = jsonify({"error": "List not found"}), 404
    else:
        response = jsonify(result), 200
    
    return response

# Update an existing list according to the database schema
@app.route("/lists/<list_name>", methods=["PUT"])
def update_list(list_name):
    data = request.get_json()

    if not ListsSchema.LIST_NAME_KEY in data:
        response = jsonify({
            "error": f"Request body missing primary key: {ListsSchema.LIST_NAME_KEY}"
        }), 422
    elif not data[ListsSchema.LIST_NAME_KEY] == list_name:
        response = jsonify({"error": "Request body primary key does not match address " \
            f"<list_name>: {data[ListsSchema.LIST_NAME_KEY]}, {list_name}"}), 422
    else:
        # Validate data in request
        updated_list = ListsSchema(
            copy.deepcopy(data),
            app.lists
        )
        form_val = updated_list.validate_list_form(request.method)

        if form_val[1] == 0:
            record = updated_list.build_list_record()
            result = app.lists.update_one(
                {ListsSchema.LIST_NAME_KEY: list_name},
                {"$set": record}
            )

            response = jsonify({"modified_count": str(result.modified_count)}), 200
        elif form_val[1] == 13:
            msg = ValidationErrorCodes.gen_val_err_msg(form_val)
            response = jsonify({"error": msg}), 404
        else:
            msg = ValidationErrorCodes.gen_val_err_msg(form_val)
            response = jsonify({"error": msg}), 422

    return response

# Remove a specific list from the database by list name
# This action is not recommended.
@app.route("/lists/<list_name>", methods=["DELETE"])
def delete_list(list_name):
    result = app.lists.delete_one(
        {ListsSchema.LIST_NAME_KEY: list_name}
        )
    
    if result.deleted_count == 0:
        response = jsonify({"error": "List not found"}), 404
    else:
        response = "", 204
    
    return response



if __name__ == "__main__":
    # Turn off debug=True when finished. Security concern.
    app.run(debug=True, host="0.0.0.0")