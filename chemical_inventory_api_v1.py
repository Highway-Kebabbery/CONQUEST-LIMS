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

Note in docs that all dates must be received as strings in ISO 8601 format and are converted to UTC, so they should be sent as local times with a timezone.
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

class ValidationErrorCodes():
    MISS_REQ_FIELD = 1
    WRONG_TYPE = 2
    INVAL_LIST_ENTRY = 3
    UNEXP_FIELD = 4
    CHEM_NOT_FOUND = 5
    WRONG_DATE_FORMAT = 6
    MISSING_COMP = 7


class ChemicalSchema(ValidationErrorCodes):
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
    def get_schema_keys(dictionary):
        # Returns all keys in a two-level dictionary or a dict-list-dict object as a list()
        # as well as the number of elements in the list if one value was a list
        # Expects that only one value in the dict will be a list. Need to know how many elements
        # exist because I need to know how many duplicates to expect to catch missing/extra
        # fields in lot validation of component fields.
        keys = []
        num_list_elements = 0

        for key, value in dictionary.items():
            if isinstance(value, dict):
                for subkey in value:
                    keys.append(f"{key}.{subkey}")
            elif isinstance(value, list):
                
                for element in value:
                    num_list_elements += 1
                    for subkey in element:
                        keys.append(f"{key}.{subkey}")
            else:
                keys.append(key)

        return [keys, num_list_elements]
    
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
                error_info = [self.SOURCE_KEY, self.MISS_REQ_FIELD]
            elif not type(self._chem_request_data[self.SOURCE_KEY]) == self.CHEMICAL_SCHEMA[self.SOURCE_KEY]:
                error_info = [self.SOURCE_KEY, self.WRONG_TYPE]
            elif not self._chem_request_data[self.SOURCE_KEY] in field_lists.sources:
                error_info = [self.SOURCE_KEY, self.INVAL_LIST_ENTRY]

        # Check for extra/missing fields 
        if error_info[0] == None: 
            request_keys = ChemicalSchema.get_schema_keys(
                self._chem_request_data
                )
            schema_keys = ChemicalSchema.get_schema_keys(
                self.CHEMICAL_SCHEMA
                )
            
            if self._chem_request_data[self.SOURCE_KEY] == "Purchased":
                irrelevant_keys = ChemicalSchema.get_schema_keys(
                    self.CHEMICAL_SCHEMA[self.PREP_FIELD_KEY]
                    )
                irrelevant_keys.append(self.PREP_FIELD_KEY)
            elif self._chem_request_data[self.SOURCE_KEY] == "Prepared":
                irrelevant_keys = ChemicalSchema.get_schema_keys(
                    self.CHEMICAL_SCHEMA[self.PURCH_FIELD_KEY]
                    )
                irrelevant_keys.append(self.PURCH_FIELD_KEY)
            
            # Reassign the list of keys. Other return value not needed
            schema_keys = schema_keys[0] - irrelevant_keys
            request_keys = request_keys[0]

            extra_keys = list(request_keys - schema_keys)

            if extra_keys:
                error_info = [extra_keys, self.UNEXP_FIELD]
        
        # Validate remaining fields. Assumes "Source" is last shared field.
        if error_info[0] == None:
            for key in self.CHEMICAL_SCHEMA:
                if not key in [self.SOURCE_KEY, self.PURCH_FIELD_KEY, self.PREP_FIELD_KEY]:
                    if not key in self._chem_request_data:
                        error_info = [key, self.MISS_REQ_FIELD]
                        break
                    if not type(self._chem_request_data[key]) == self.CHEMICAL_SCHEMA[key]:
                        error_info = [key, self.WRONG_TYPE]
                        break
                    elif key == self.CLASSIF_KEY:
                        if not self._chem_request_data[key] in field_lists.classifications:
                            error_info = [key, self.INVAL_LIST_ENTRY]
                        break
                    elif key == self.STORAGE_KEY:
                        if not self._chem_request_data[key] in field_lists.storage_conditions:
                            error_info = [key, self.INVAL_LIST_ENTRY]
                        break
                else:
                    # "Source" is only used to enter this code block; it's evaluated above.
                    # `key` stuck == "Source" in this block so new `key`-like variables are created.
                    if self._chem_request_data[key] == "Purchased":
                        # Validate "Purchased Fields" itself
                        outer_key = self.PURCH_FIELD_KEY

                        if not outer_key in self._chem_request_data:
                            error_info = [outer_key, self.MISS_REQ_FIELD]
                            break
                        if not type(self._chem_request_data[outer_key]) == type(self.CHEMICAL_SCHEMA[outer_key]):
                            error_info = [outer_key, self.WRONG_TYPE]
                            break

                        # Validate contents of "Purchased Fields"
                        purch_inner_dict = self.CHEMICAL_SCHEMA[outer_key]
                        req_inner_dict = self._chem_request_data[outer_key]

                        for inner_key in purch_inner_dict:
                            if not inner_key in req_inner_dict:
                                error_info = [inner_key, self.MISS_REQ_FIELD]
                                break
                            if isinstance(purch_inner_dict[inner_key], list):
                                if not type(req_inner_dict[inner_key]) in purch_inner_dict[inner_key]:
                                    error_info = [inner_key, self.WRONG_TYPE]
                                    break
                            elif not type(req_inner_dict[inner_key]) == purch_inner_dict[inner_key]:
                                error_info = [inner_key, self.WRONG_TYPE]
                                break
                            elif inner_key == self.UNIT_KEY:
                                if not req_inner_dict[inner_key] in field_lists.units:
                                    error_info = [inner_key, self.INVAL_LIST_ENTRY]
                                    break
                            elif inner_key == self.CONT_TYPE_KEY:
                                if not req_inner_dict[inner_key] in field_lists.containers:
                                    error_info = [inner_key, self.INVAL_LIST_ENTRY]
                                    break
                    
                    elif self._chem_request_data[key] == "Prepared":
                        # Validate "Prepared Fields" itself
                        outer_key = self.PREP_FIELD_KEY

                        if not outer_key in self._chem_request_data:
                            error_info = [outer_key, self.MISS_REQ_FIELD]
                            break
                        if not type(self._chem_request_data[outer_key]) == type(self.CHEMICAL_SCHEMA[outer_key]):
                            error_info = [outer_key, self.WRONG_TYPE]
                            break

                        # Validate contents of "Prepared Fields"
                        prep_inner_dict = self.CHEMICAL_SCHEMA[outer_key]
                        req_inner_dict = self._chem_request_data[outer_key]

                        for inner_key in prep_inner_dict:
                            if not inner_key in req_inner_dict:
                                error_info = [inner_key, self.MISS_REQ_FIELD]
                                break
                            if not type(req_inner_dict[inner_key]) == prep_inner_dict[inner_key]:
                                error_info = [inner_key, self.WRONG_TYPE]
                                break

                if not error_info[0] == None:
                    # This is in the event that inner loops found invalid data
                    break
       
        return error_info

    def build_chem_record(self, lots_collection=None, chemical_id=ObjectId(), req_method=""):
            # Build dictionary object to add new record using mandatory schema.
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
    CHEM_ID_KEY = "chemical_id"
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
        ChemicalSchema.UNIT_KEY: ChemicalSchema.CHEMICAL_SCHEMA[ChemicalSchema.UNIT_KEY],
        EXPIRY_KEY: str
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
        self._lot_request_data = data

        # Used to short-circuit validation if chemical not found
        self._chem_id_error = []

        # Pop _id and chemical_id to strip _lot_request_data for validation and build.
        self._chemical_id = self._lot_request_data.pop(self.CHEM_ID_KEY)
        if self.ID_KEY in self._lot_request_data:
            self.__req_id = self._lot_request_data.pop(self.ID_KEY)

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
            self._chem_id_error = ["chemical_id", self.CHEM_NOT_FOUND]
        
        return chem_data

    def validate_lot_form(self):
        # Internal lot number validation would be added when there's a reliable system to generate internal lot numbers
        error_info = self._chem_id_error

        # Check for extra keys
        if error_info[0] == None:
            request_keys = ChemicalSchema.get_schema_keys(
                self._lot_request_data
            )

            if self._chem_data[self.SOURCE_KEY] == self.PURCH_FIELD_KEY:
                schema_keys = ChemicalSchema.get_schema_keys(
                    self.LOT_SCHEMA[self.PURCH_FIELD_KEY]
                )
            else:
                schema_keys = ChemicalSchema.get_schema_keys(
                    self.LOT_SCHEMA[self.PREP_FIELD_KEY]
                )
                if schema_keys[1] == 0:
                    error_info = ["", self.MISSING_COMP]
                elif not schema_keys[1] == 1:
                    # Add the correct number of duplicates for component keys from schema
                    for i in range(2, (schema_keys[1] + 1)):
                        for key in self.LOT_SCHEMA[self.PREP_FIELD_KEY]:
                            schema_keys[0].append(key)
            
            # Keep only the list of keys
            schema_keys = schema_keys[0]
            request_keys = request_keys[0]

            extra_keys = list(request_keys - schema_keys)

            if extra_keys:
                if error_info[0] == None:
                    # Don't override error if components are missing.
                    error_info = [extra_keys, self.UNEXP_FIELD]
        
        # Check presence of keys, types of data, and whether list data are valid.
        if error_info[0] == None:
            if self.SOURCE_KEY == "Purchased":
                for key in self.LOT_SCHEMA:
                    if not type(self._lot_request_data[key]) == self.LOT_SCHEMA[key]:
                        error_info = [key, self.WRONG_TYPE]
                        break
                    elif key in [self.OPEN_KEY, self.EXPIRY_KEY, self.EMPTY_KEY]:
                        try:
                            dt = datetime.fromisoformat(self._lot_request_data[key])
                        except ValueError:
                            error_info = [key, self.WRONG_DATE_FORMAT]
                            break
            elif self.SOURCE_KEY == "Prepared":
                for key in self.LOT_SCHEMA:
                    if isinstance(self.LOT_SCHEMA[key], list):
                        # "Components" and "Amount" both have embedded lists as values
                        if key == self.COMPONENTS_KEY:
                            # Loop through components and validate each

                            for component in self._lot_request_data[key]:
                                prep_comp_dict = self.COMPONENT_SCHEMA
                                req_comp_dict = self._lot_request_data[key][component]
                                
                                for subkey in prep_comp_dict:
                                    if isinstance(prep_comp_dict[subkey], list):   # "Amount" field
                                        if not subkey in req_comp_dict:
                                            error_info = [f"{key}.Component #{component + 1}.{subkey}", self.MISS_REQ_FIELD]
                                            break
                                        elif not type(req_comp_dict[subkey]) in prep_comp_dict[subkey]:
                                            error_info = [f"{key}.{req_comp_dict[self.NAME_KEY]}.{subkey}", self.WRONG_TYPE]
                                            break
                                    else:
                                        if not subkey in req_comp_dict:
                                            error_info = [f"{key}.Component #{component + 1}.{subkey}", self.MISS_REQ_FIELD]
                                            break
                                        elif not type(req_comp_dict[subkey]) == prep_comp_dict[subkey]:
                                            error_info = [f"{key}.{req_comp_dict[self.NAME_KEY]}.{subkey}", self.WRONG_TYPE]
                                            break
                                        elif key in [self.PREP_DATE_KEY, self.EXPIRY_KEY, self.EMPTY_KEY]:
                                            try:
                                                dt = datetime.fromisoformat(self._lot_request_data[key])
                                            except ValueError:
                                                error_info = [key, self.WRONG_DATE_FORMAT]
                                                break
                                        elif subkey == self.UNIT_KEY:
                                            if not req_comp_dict[subkey] in field_lists.units:
                                                error_info = [subkey, self.INVAL_LIST_ENTRY]
                                                break
                                    
                                if not error_info[0] == None:
                                    # This is in the event that inner loops found invalid data
                                    break

                        else:
                            if not key in self._lot_request_data:
                                error_info = [key, self.MISS_REQ_FIELD]
                            elif not type(self._lot_request_data[key]) in self.LOT_SCHEMA[key]:
                               error_info = [key, self.WRONG_TYPE]
                               break
                    elif key in [self.PREP_DATE_KEY, self.EXPIRY_KEY, self.EMPTY_KEY]:
                        try:
                            dt = datetime.fromisoformat(self._lot_request_data[key])
                        except ValueError:
                            error_info = [key, self.WRONG_DATE_FORMAT]
                            break
                    else:
                        if not type(self._lot_request_data[key]) == self.LOT_SCHEMA[key]:
                            error_info = [key, self.WRONG_TYPE]
                            break
                    
                    if not error_info[0] == None:
                        # This is in the event that inner loops found invalid data
                        break
                
        return error_info
    
    def build_lot_record(self):
        pass
        # Build dictionary object to insert new lot document using mandatory schema
        
        # Add shared fields from chemical schema
        record = self.build_chem_record(self._chem_data)

        # Add lot fields in correct positions
        record.insert(0, {self.CHEM_ID_KEY: self._chemical_id})

        if self.SOURCE_KEY == "Purchased":
            record[6].insert(2, {
                self.MANU_LOT_KEY: self._lot_request_data[self.MANU_LOT_KEY]
                })
            record.insert(2, {
                self.INTERNAL_LOT_KEY: self._lot_request_data[self.INTERNAL_LOT_KEY]
                })
            record.insert(8, {
                self.OPEN_KEY: self._lot_request_data[self.OPEN_KEY]
                })
            record.insert(9, {
                self.EXPIRY_KEY: self._lot_request_data[self.EXPIRY_KEY]
                })
            record.insert(10, {
                self.EMPTY_KEY: self._lot_request_data[self.EMPTY_KEY]
                })
            
        elif self.SOURCE_KEY == "Prepared":
            record.insert(2, {
                self.INTERNAL_LOT_KEY: self._lot_request_data[self.INTERNAL_LOT_KEY]
                })
            record.insert(3, {
                self.AMT_KEY: self._lot_request_data[self.AMT_KEY]
                })
            record.insert(4, {
                self.UNIT_KEY: self._lot_request_data[self.UNIT_KEY]
                })
            record.insert(5, {
                self.CONT_TYPE_KEY: self._lot_request_data[self.CONT_TYPE_KEY]
                })
            record.insert(11, {
                self.PREP_DATE_KEY: self._lot_request_data[self.PREP_DATE_KEY]
                })
            record.insert(12, {
                self.EXPIRY_KEY: self._lot_request_data[self.EXPIRY_KEY]
                })
            record.insert(13, {
                self.EMPTY_KEY: self._lot_request_data[self.EMPTY_KEY]
                })
            record[14].insert{0, {
                self.COMPONENTS_KEY: []
            }}

            # Insert each component from the lot record request
            for component in self._lot_request_data[self.COMPONENTS_KEY]:
                # Build each component dictionary then add it to record[14][component]



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
                    record = new_chemical.build_chem_record()
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
                        record = updated_chemical.build_chem_record(
                            app.lots, chemical_id, request.method
                            )

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