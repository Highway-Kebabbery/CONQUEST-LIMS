from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime, timezone

"""
This project is in-progress. If I have to apply for a job before it's
finished, then understand that many of the comments throughout are "notes
to self" and will be removed when the build is finished.

I include rough docstring-like notes on functions as I write, but formalising
those will come last (i.e. No edits left, all testing passed
(but will test again after), ready to push to staging environment).

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

* If I really wanted to make this more realistic then I'd change ChemicalSchema to
StandardReagentTemplate and change LotSchema to StandardReagent. I'd then use
StandardReagentTemplate to also control both how many components are added to 
a given prepared reagent (with a forced _id that matches the method reference)
as well as controlling (really looking ahead) the addition of a test sample with a test
analysis (e.g. FTIR testing required to release purchased lot of a reagent for
manufacturing use.) All of that is way out of scope for demonstrating that I can use
these technologies, though. If I'm going to make a build that ready-to-ship then it'll
be for something I actually use and/or sell.


I first need to create a chemical in test setup and in testing I'll query
to get the chemical _id then proceed as usual (submitting a request with that _id).

    # When writing docstring, note that redundancy of chemical fields in lots documents 
    # was chosen because they're needed when getting all lots, and that happens far
    # more often than adding a chemical (the other time they're needed together with
    # lot fields), so slightly larger documents and fewer server requests will be faster
    # on average than having a sctricter separation of concerns in the database. That's
    # also a good point for showing that I'm thinking about the right thing with the
    # document-based database (Add to "Things I learned" section of README.)

Note in docs that all dates received are converted to UTC, so they should be sent as local times with a timezone.
Note i ndocs that all dates are served to front-end as UTC dates.
    
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
    # but I need to get *something* running for now. I know how to use the
    # database for this purpose, but this API is taking long enough as is and I want
    # the list logic in place for now.
    #
    # When the rest of it is up and running, I'll add this as a collection to the DB
    # and replace calls to this class with database queries.
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

field_lists = Lists()

class ChemicalSchema():
    # Explain what a chemical class is as opposed to a lot. Explain why the addition of chemicals
    # and lots harmonizes data despite creating some redundancy, and why the addition of lots and
    # chemicals are isolated actions.
    ID_KEY = "_id"    # Using MongoDB's _id field as the primary key for now
    NAME_KEY = "Name"
    CAS_KEY = "CAS Number"
    CLASSIF_KEY = "Classification"
    STORAGE_KEY = "Storage Condition"
    SOURCE_KEY = "Source"
    
    PURCH_FIELD_KEY = "Purchased Fields"
    MANU_KEY = "Manufacturer"
    MANU_PN_KEY = "Manufacturer Part Number"
    AMT_KEY = "Amount"
    UNIT_KEY = "Units"
    CONT_TYPE_KEY = "Container Type"

    PREP_FIELD_KEY = "Prepared Fields"
    METH_REF_KEY = "Method Reference"

    __AVAIL_TOTAL_KEY = "Available Total"    # Added only at document creation
    __AVAIL_OPEN_KEY = "Available Open"    # Added only at document creation

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

    def __init__(self, data):
        # Single underscore prevents name mangling (easier to call in child class)
        self._chem_request_data = data
        
        # These fields will be stored as parameters and removed from
        # self._chem_request_data to allow reuse of data validation for both POST and PUT.
        # They aren't used but are preserved.
        if self.ID_KEY in self._chem_request_data:
            self.__req_id = self._chem_request_data.pop(self.ID_KEY)
        if self.__AVAIL_TOTAL_KEY in self._chem_request_data:
            self.__req_total = self._chem_request_data.pop(self.__AVAIL_TOTAL_KEY)
        if self.__AVAIL_OPEN_KEY in self._chem_request_data:
            self.__req_open = self._chem_request_data.pop(self.__AVAIL_OPEN_KEY)
        
        # These should be calculated at execution, ergo no validation of
        # front-end request. Set with self.query_current_totals()
        self.__current_avail_total = 0
        self.__current_avail_open = 0

    @staticmethod
    def get_schema_dict_keys(dictionary):
        # Returns all keys in a two-level dictionary or a dict-list-dict object as a list()
        # as well as the number of elements in the list if one value was a list
        # Expects that only one value in the dict will be a list. Need to know how many elements
        # exist because I need to know how many duplicates to expect to catch missing/extra
        # fields in lot validation of component fields.
        keys = []
        for key, value in dictionary.items():
            if isinstance(value, dict):
                for subkey in value:
                    keys.append(f"{key}.{subkey}")
            elif isinstance(value, list):
                num_elements = 0
                for element in value:
                    num_elements += 1
                    for subkey in element:
                        keys.append(f"{key}.{subkey}")
            else:
                keys.append(key)
        return [keys, num_elements]
    
    def query_current_totals(self, lots_collection, chemical_id):
        # This function sets and returns the self.__current_avail_total and 
        # self.__current_avail_open paramenters. It's intended to be called either
        # internally or externally.
        # 
        # lots_collection is type pymongo.collection.Collection
        # 
        # related_lot is ojbect of type LotSchema (to pass key names)
        
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")

        self.__current_avail_total = lots_collection.count_documents({
            "$and": [
                {self.ID_KEY: ObjectId(chemical_id)},
                {LotSchema.EMPTY_KEY: {"$eq": None}},
                {LotSchema.EXPIRY_KEY: {"$gt": now}},
            ]
        })

        self.__current_avail_open = lots_collection.count_documents({
            "$and": [
                {self.ID_KEY: ObjectId(chemical_id)},
                {LotSchema.EMPTY_KEY: {"$eq": None}},
                {LotSchema.EXPIRY_KEY: {"$gt": now}},
                {"$or": [
                    {
                        ChemicalSchema.SOURCE_KEY: "Purchased",
                        LotSchema.OPEN_KEY: {"$ne": None}
                    },
                    {
                        ChemicalSchema.SOURCE_KEY: "Prepared"
                    }
                ]}
            ]
        })

        return {
            self.__AVAIL_TOTAL_KEY: self.__current_avail_total,
            self.__AVAIL_OPEN_KEY: self.__current_avail_open
        }

    def validate_chemical_form(self):
        """
        Don't forget to include what each error_type means in final docstring
        """
        error_info = [None, 0]  # bad_key, error_type
        
        # Validate "Source" first to simplify paths
        if error_info[0] == None:
            if not self.SOURCE_KEY in self._chem_request_data:
                error_info = [self.SOURCE_KEY, 1]
            elif not type(self._chem_request_data[self.SOURCE_KEY]) == self.CHEMICAL_SCHEMA[self.SOURCE_KEY]:
                error_info = [self.SOURCE_KEY, 2]
            elif not self._chem_request_data[self.SOURCE_KEY] in field_lists.sources:
                error_info = [self.SOURCE_KEY, 3]

        # Check for extra/missing fields 
        if error_info[0] == None: 
            request_keys = ChemicalSchema.get_schema_dict_keys(
                self._chem_request_data
                )
            schema_keys = ChemicalSchema.get_schema_dict_keys(
                self.CHEMICAL_SCHEMA
                )
            
            if self._chem_request_data[self.SOURCE_KEY] == "Purchased":
                irrelevant_keys = ChemicalSchema.get_schema_dict_keys(
                    self.CHEMICAL_SCHEMA[self.PREP_FIELD_KEY]
                    )
                irrelevant_keys.append(self.PREP_FIELD_KEY)
            else:
                irrelevant_keys = ChemicalSchema.get_schema_dict_keys(
                    self.CHEMICAL_SCHEMA[self.PURCH_FIELD_KEY]
                    )
                irrelevant_keys.append(self.PURCH_FIELD_KEY)
            
            # Reassign the list of keys. Other return value not needed
            schema_keys = schema_keys[0] - irrelevant_keys
            request_keys = request_keys[0]

            extra_keys = list(request_keys - schema_keys)
            missing_keys = list(schema_keys - request_keys)

            if extra_keys:
                error_info = [extra_keys, 4]
            if missing_keys:
                error_info = [missing_keys, 1]
        
        # Validate remaining fields. Assumes "Source" is last shared field.

        #####If missing_keys check doesn't work above then add back these commented out sections
        if error_info[0] == None:
            for key in self.CHEMICAL_SCHEMA:
                if not key in [self.SOURCE_KEY, self.PURCH_FIELD_KEY, self.PREP_FIELD_KEY]:
                    #if not key in self._chem_request_data:
                    #    error_info = [key, 1]
                    #    break
                    if not type(self._chem_request_data[key]) == self.CHEMICAL_SCHEMA[key]:
                        error_info = [key, 2]
                        break
                    elif key == self.CLASSIF_KEY:
                        if not self._chem_request_data[key] in field_lists.classifications:
                            error_info = [key, 3]
                        break
                    elif key == self.STORAGE_KEY:
                        if not self._chem_request_data[key] in field_lists.storage_conditions:
                            error_info = [key, 3]
                        break
                else:
                    # "Source" is only used to enter this code block; it's evaluated above.
                    # `key` stuck == "Source" in this block so new `key`-like variables are created.
                    if self._chem_request_data[key] == "Purchased":
                        # Validate "Purchased Fields" itself
                        outer_key = self.PURCH_FIELD_KEY

                        #if not outer_key in self._chem_request_data:
                        #    error_info = [outer_key, 1]
                        #    break
                        if not type(self._chem_request_data[outer_key]) == type(self.CHEMICAL_SCHEMA[outer_key]):
                            error_info = [outer_key, 2]
                            break

                        # Validate contents of "Purchased Fields"
                        purch_inner_dict = self.CHEMICAL_SCHEMA[outer_key]
                        req_inner_dict = self._chem_request_data[outer_key]

                        for inner_key in purch_inner_dict:
                            #if not inner_key in req_inner_dict:
                            #    error_info = [inner_key, 1]
                            #    break
                            if isinstance(purch_inner_dict[inner_key], list):
                                if not type(req_inner_dict[inner_key]) in purch_inner_dict[inner_key]:
                                    error_info = [inner_key, 2]
                                    break
                            elif not type(req_inner_dict[inner_key]) == purch_inner_dict[inner_key]:
                                error_info = [inner_key, 2]
                                break
                            elif inner_key == self.UNIT_KEY:
                                if not req_inner_dict[inner_key] in field_lists.units:
                                    error_info = [inner_key, 3]
                                    break
                            elif inner_key == self.CONT_TYPE_KEY:
                                if not req_inner_dict[inner_key] in field_lists.containers:
                                    error_info = [inner_key, 3]
                                    break
                    
                    elif self._chem_request_data[key] == "Prepared":
                        # Validate "Prepared Fields" itself
                        outer_key = self.PREP_FIELD_KEY

                        #if not outer_key in self._chem_request_data:
                        #    error_info = [outer_key, 1]
                        #    break
                        if not type(self._chem_request_data[outer_key]) == type(self.CHEMICAL_SCHEMA[outer_key]):
                            error_info = [outer_key, 2]
                            break

                        # Validate contents of "Prepared Fields"
                        prep_inner_dict = self.CHEMICAL_SCHEMA[outer_key]
                        req_inner_dict = self._chem_request_data[outer_key]

                        for inner_key in prep_inner_dict:
                            #if not inner_key in req_inner_dict:
                            #    error_info = [inner_key, 1]
                            #    break
                            if not type(req_inner_dict[inner_key]) == prep_inner_dict[inner_key]:
                                error_info = [inner_key, 2]
                                break

                if not error_info[0] == None:
                    # This is in the event that inner loops found invalid data
                    break
       
        return error_info

    def build_record(self, lots_collection=None, chemical_id=ObjectId(), req_method=""):
            # Build dictionary object to add new record using correct field names.
            # lots_collection is type pymongo.collection.Collection
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
                record[self.__AVAIL_TOTAL_KEY] = 0
                record[self.__AVAIL_OPEN_KEY] = 0
            elif req_method.upper() == "PUT":
                self.query_current_totals(lots_collection, chemical_id)

                record[self.__AVAIL_TOTAL_KEY] = self.__current_avail_total
                record[self.__AVAIL_OPEN_KEY] = self.__current_avail_open

            return record

class LotSchema(ChemicalSchema):
    # Add this to documentation, but requests should be of the form of one of the two VALUES in the LOT_SCHEMA dictionary (plus chemical_id).
    CHEMICAL_ID = "chemical_id"
    MANU_LOT_KEY = "Manufacturer Lot/Batch Number"
    INTERNAL_LOT_KEY = "Internal Lot Number"
    OPEN_KEY = "Open Date"
    EXPIRY_KEY = "Expiry Date"
    EMPTY_KEY = "Empty Date"
    PREP_DATE_KEY = "Preparation Date"
    COMPONENTS_KEY = "Components"

    # Per component added to prepared material.
    COMPONENT_SCHEMA = {
        ChemicalSchema.NAME_KEY: ChemicalSchema.CHEMICAL_SCHEMA[ChemicalSchema.NAME_KEY],
        INTERNAL_LOT_KEY: str,
        ChemicalSchema.AMT_KEY: ChemicalSchema.CHEMICAL_SCHEMA[ChemicalSchema.AMT_KEY],    # Calculations with amounts must be performed with Decimal()
        ChemicalSchema.UNIT_KEY: ChemicalSchema.CHEMICAL_SCHEMA[ChemicalSchema.UNIT_KEY]
        }
    
    LOT_SCHEMA = {
        ChemicalSchema.PURCH_FIELD_KEY: {
            MANU_LOT_KEY: str,
            INTERNAL_LOT_KEY: str,
            OPEN_KEY: str,
            EXPIRY_KEY: str,
            EMPTY_KEY: str
        },
        ChemicalSchema.PREP_FIELD_KEY: {
            INTERNAL_LOT_KEY: str,
            ChemicalSchema.AMT_KEY: ChemicalSchema.CHEMICAL_SCHEMA[ChemicalSchema.AMT_KEY],    # Calculations with amounts must be performed with Decimal()
            ChemicalSchema.UNIT_KEY: ChemicalSchema.CHEMICAL_SCHEMA[ChemicalSchema.UNIT_KEY],
            ChemicalSchema.CONT_TYPE_KEY: ChemicalSchema.CHEMICAL_SCHEMA[ChemicalSchema.CONT_TYPE_KEY],
            PREP_DATE_KEY: str,
            EXPIRY_KEY: str,
            EMPTY_KEY: str,
            COMPONENTS_KEY: [
                COMPONENT_SCHEMA
                ]
        }
    }

    def __init__(self, data, chemicals_collection):
        self._chem_id_valid = bool
        self._lot_request_data = data

        # Pop chemical_id to strip _lot_request_data for validation and build.
        self._chemical_id = self._lot_request_data.pop(self.CHEMICAL_ID)

        # Check for/return related data from chemical form (already cleaned on arrival)
        super().__init__(
            self.query_chemical_form(self._chemical_id, chemicals_collection)
            )
        # Use self._chem_data because the name makes more sense in LotSchema context
        self._chem_data = self._chem_request_data
    
    def query_chemical_form(self, chemical_id, chemicals_collection):
        # Returns document from chemicals collection with specified _id
        chem_data = chemicals_collection.find_one(
            {self.ID_KEY: ObjectId(chemical_id)}
        )

        if not chem_data:
            self._chem_id_error = ["chemical_id", 5]
        
        return chem_data

    def validate_lot_form(self):
        # Check value for "Source" from pulled chemical data and validate lot fields based on that (means I only eval a 1- or 2-level dict)
        #
        # The data: * types
        #           * existence of all keys in schema
        #           * No extra keys
        #           * Date keys are either empty string or date of specified format
        #             * Convert date to utc by calling a method that does so
        #             * Can I handle daylight savings time? I would just need to store whether or not it's DST and only apply that to time difference calculations
        #           * Ensure prepared lots have >= 1 component (can check self.SOURCE_KEY to determine if purchased or prepared)
        #
        #
        ########I need to make an instance parameter that flags whether the chemical _id was found.
        # Check that flag at the top of this method, and if it's bad just return the answer right away (skip other blocks)
        
        # Check for missing/extra keys
        # This wouldn't catch it if one component had two of a valid field while another was missing that valid field
        # or any permutation of the same case (valid number of valid fields in an invalid combination on each component)
        # This case is handled when component value types are validated (presence of required fields is ensured) and
        # when the document is built (it is only built from the validated field names in the schema)
        error_info = self._chem_id_valid
        if error_info[0] == None:
            request_keys = ChemicalSchema.get_schema_dict_keys(
                self._lot_request_data
            )

            if self.SOURCE_KEY == "Purchased":
                schema_keys = ChemicalSchema.get_schema_dict_keys(
                    self.LOT_SCHEMA[self.PURCH_FIELD_KEY]
                )
            else:
                schema_keys = ChemicalSchema.get_schema_dict_keys(
                    self.LOT_SCHEMA[self.PREP_FIELD_KEY]
                )
                if not schema_keys[1] == 1:
                    # Add the correct number of duplicates for component keys from schema
                    for i in range(2, (schema_keys[1] + 1)):
                        for key in self.LOT_SCHEMA[self.PREP_FIELD_KEY]:
                            schema_keys[0].append(key)
            
            # Can safely discard the number of components in the request
            schema_keys = schema_keys[0]
            request_keys = request_keys[0]

            extra_keys = list(request_keys - schema_keys)

            if extra_keys:
                error_info = [extra_keys, 4]
        
        # Check types
        ##########when returning, add check for error type 3 "doesn't exist in validated list"
        ###Don't forget to add breaks (and take breaks, too)
        if error_info[0] == None:
            if self.SOURCE_KEY == "Purchased":
                for key in self.CHEMICAL_SCHEMA:
                    if not type(self._lot_request_data[key]) == self.CHEMICAL_SCHEMA[key]:
                        error_info = [key, 2]
            else:
                for key in self.CHEMICAL_SCHEMA:
                    if isinstance(self.CHEMICAL_SCHEMA[key], list):
                        # "Components" and "Amount" both have embedded lists as values
                        if isinstance(self.CHEMICAL_SCHEMA[key][0], dict):
                            # Loop through components and validate each

                            for element in self.CHEMICAL_SCHEMA[key]:
                                # Component value type check
                                # Also verify component field presence to catch misses from the validation above
                                prep_inner_dict = self.CHEMICAL_SCHEMA[key][element]
                                req_inner_dict = self._lot_request_data[key][element]
                                
                                for subkey in prep_inner_dict:
                                    if isinstance(prep_inner_dict[subkey], list):
                                        if not subkey in req_inner_dict:
                                            error_info = [f"{key}.Component #{element + 1}.{subkey}", 1]
                                        elif not type(req_inner_dict[subkey] in prep_inner_dict[subkey]):
                                            error_info = [f"{key}.{req_inner_dict[self.NAME_KEY]}.{subkey}", 2]
                                    else:
                                        if not subkey in req_inner_dict:
                                            error_info = [f"{key}.Component #{element + 1}.{subkey}", 1]
                                        elif not type(req_inner_dict[subkey] == prep_inner_dict[subkey]):
                                            error_info = [f"{key}.{req_inner_dict[self.NAME_KEY]}.{subkey}", 2]

                        else:
                            if not type(self._lot_request_data[key]) in self.CHEMICAL_SCHEMA[key]:
                               error_info = [key, 2]
                    else:
                        if not type(self._lot_request_data[key]) == self.CHEMICAL_SCHEMA[key]:
                            error_info = [key, 2]



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
        # Add a new chemical according to database schema.
        data = request.get_json()
        new_chemical = ChemicalSchema(data)

        if not data:
            response = jsonify({"error": "Missing request body"}), 400
        else:
            # Validate data in request
            form_val = new_chemical.validate_chemical_form()

            match form_val[1]:
                case 0:
                    record = new_chemical.build_record()
                    result = app.chemicals.insert_one(record)
                    response = jsonify({"inserted_id": str(result.inserted_id)}), 201
                case 1:
                    msg = f"Missing required field: {form_val[0]}."
                    response = jsonify({"error": msg}), 422
                case  2:
                    msg = f"Incorrect data type for field: {form_val[0]}."
                    response = jsonify({"error": msg}), 422
                case 3:
                    msg = f'Invalid entry of correct data type for {form_val[0]}.'
                    response = jsonify({"error": msg}), 422
                case 4:
                    response = jsonify({"error": f"Unexpected fields: {form_val[0]}."}), 422
        
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
        data = request.get_json()
        updated_chemical = ChemicalSchema(data)

        if not data:
            response = jsonify({"error": "Missing request body"}), 400
        else:
            # Validate data in request
            form_val = updated_chemical.validate_chemical_form()

            match form_val[1]:
                case 0:
                    try:
                        record = updated_chemical.build_record(app.lots, chemical_id, request.method)

                        result = app.chemicals.update_one(
                            {"_id": ObjectId(chemical_id)},
                            {"$set": record}
                            )
                        if result.matched_count == 0:
                            response = jsonify({"error": "Not found"}), 404
                        else:
                            response = jsonify({"modified_count": str(result.modified_count)}), 200
                    except InvalidId:
                        response = jsonify({"error": "Invalid ID format"}), 400
                case 1:
                    msg = f"Missing required field: {form_val[0]}."
                    response = jsonify({"error": msg}), 422
                case  2:
                    msg = f"Incorrect data type for field: {form_val[0]}."
                    response = jsonify({"error": msg}), 422
                case 3:
                    msg = f'Invalid entry of correct data type for {form_val[0]}.'
                    response = jsonify({"error": msg}), 422
                case 4:
                    response = jsonify({"error": f"Unexpected fields: {form_val[0]}."}), 422

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
def manage_lot(lot_id):
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