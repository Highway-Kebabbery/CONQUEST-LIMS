"""
Schema validation and record management for chemical templates.

This module defines the ChemicalSchema class which validates input for
chemical records submitted to the system, builds records to be inserted, 
and handles the insertion of those records. It distinguishes between
purchased and prepared chemicals and enforces correct key usage and
data typing. It also handles recalculation of aggregate fields, such as 
"Available_Total" and "Available_Open", when lot records are created or 
modified and when chemical records are modified or retrieved.

Records are built from scratch during every POST/PUT operation to avoid
retaining unvalidated data and using the internal schema definition to
avoid the accidental injection of invalid fields.

Validation is short-circuited at the first error detected, so a request
returned with one error may have multiple issues.
"""

from app.utils.helper_functions import HelperFunctions
from app.utils.validation_error_codes import ValidationErrorCodes

# Imported lazily to avoid circular reference:
# from app.models.lists import ListsSchema
# from app.models.lots import LotSchema

from bson import ObjectId
from bson.errors import InvalidId

from datetime import datetime, timezone

from typing import List

class ChemicalSchema():
    CHEM_ID_KEY = "_id"                       # Using MongoDB's _id field as the primary key for now
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

    AVAIL_TOTAL_KEY = "Total_Available_Lots"  # Added at document creation, refreshed otherwise
    AVAIL_OPEN_KEY = "Total_Open_Lots"        # Added at document creation, refreshed otherwise

    CHEMICAL_SCHEMA = {
        NAME_KEY: str,
        CAS_KEY: str,
        CLASSIF_KEY: str,
        STORAGE_KEY: str,
        SOURCE_KEY: str,

        PURCH_FIELD_KEY: {
            MANU_KEY: str,
            MANU_PN_KEY: str,
            AMT_KEY: [float, int],            # Calculations with amounts must be performed with Decimal()
            UNIT_KEY: str,
            CONT_TYPE_KEY: str,
        },

        PREP_FIELD_KEY: {
            METH_REF_KEY: str
        }
    }

    def __init__(
        self,
        data: dict,
        chemicals_collection,
        lots_collection
    ):
        """
        Initialize a ChemicalSchema instance.

        Args:
            data (dict): Request body for chemical record.
            chemicals_collection: Reference to MongoDB collection for chemicals.
            lots_collection: Reference to MongoDB collection for lots.

        Notes:
            * Fields not used in validation are stripped and stored as instanace parameters.
                * This is also utilized when initializing LotSchema objects to strip the 
                parent chemical record data for use in the construction of a lot record.
        """

        # Single underscore prevents name mangling (easier to call in child class)
        self._chem_request_data = data
        self._chemicals_collection = chemicals_collection
        self._lots_collection = lots_collection
        
        # Lazy import to break circular reference
        from app.models.lists import ListsSchema

        self._field_lists = ListsSchema()
        self._check = HelperFunctions()
        self._errs = ValidationErrorCodes()
        
        # Fields stripped from self._chem_request_data to allow reuse of data validation
        # logic for both POST and PUT requests.
        if self.CHEM_ID_KEY in self._chem_request_data:
            self.__chem_req_id = self._chem_request_data.pop(self.CHEM_ID_KEY)
        if self.AVAIL_TOTAL_KEY in self._chem_request_data:
            self.__req_total = self._chem_request_data.pop(self.AVAIL_TOTAL_KEY)
        if self.AVAIL_OPEN_KEY in self._chem_request_data:
            self.__req_open = self._chem_request_data.pop(self.AVAIL_OPEN_KEY)
        # The system won't always use MongoDB's "_id" as the primary key; 
        # this line accounts for that.
        if "_id" in self._chem_request_data:
            self.__mongo_id = self._chem_request_data.pop("_id")
    
    @staticmethod
    def query_current_totals(
        chemicals_collection,
        lots_collection,
        chem_ids: List[str],
        update_records: bool = False
    ) -> dict:
        """
        Query and optionally update aggregate lot availability fields for chemical(s).

        Args:
            chemicals_collection: MongoDB collection containing chemical documents.
            lots_collection: MongoDB collection containing lot documents.
            chem_ids (List[str]): List of chemical document _ids.
            update_records (bool): If True, updates the database records in-place.

        Returns:
            dict: A dictionary containing 'Available_Total' and 'Available_Open' counts
                for the last chemical ID checked in chem_ids.
        """        
        # Lazy import to break circular reference
        from app.models.lots import LotSchema

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
                # Update record in database with refreshed totals
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

    def find_chemical_form(
        self,
        query: dict,
        chemicals_collection=None
    ) -> dict:
        """
        Find and return a single chemical document matching the query.

        Args:
            query (dict): Any valid MongoDB query dictionary.
            chemicals_collection (optional): Optional override for the chemicals collection.
                * ChemicalSchema.__init__() sets self._chemicals_collection for both LotSchema
                and ChemicalSchema objects. LotSchema.__init__() calls this method before it
                calls super().__init__() and initializes the ChemicalSchema instance parameters,
                including self._chemicals_collection, so in that case the chemicals collection 
                must be passed directly to this method.

        Returns:
            dict: Document retrieved from the chemicals collection.
        """
        if chemicals_collection == None:
            chem_data = self._chemicals_collection.find_one(
                query
            )
        else:
            chem_data = chemicals_collection.find_one(
                query
            )
        
        return chem_data

    def find_lot_form(
        self,
        query: dict,
        lots_collection
    ) -> dict:
        """
        Retrieve a specific lot record from the lots collection.

        Args:
            query (dict): Any valid MongoDB query.
            lots_collection: Reference to MongoDB lots collection.

        Returns:
            dict: Document retrieved from the lots collection.
        """
        lot_data = lots_collection.find_one(query)

        return lot_data

    def validate_chemical_form(
        self,
        request_method: str
    ) -> tuple:
        """
        Validates the chemical requesta form against the defined record schema. Checks
        for: presence of required fields and value, validity of value types, presence 
        of list-entry fields values in validated lists, presence of unexpected request
        fields, existence of chemicals to be updated in the database (PUT), whether the
        request is a duplicate of an existing record (POST), whether the provided 
        primary key is a string form of a valid ObjectId object.

        Args:
            request_method (str): HTTP request method, e.g., "POST" or "PUT".

        Returns:
            tuple: (bad_key(s), validation_error_code). Returns (None, 0) if no errors are found.
                * ValidationErrorCodes returned: 1, 2, 3, 4, 5 (PUT only), 9 (POST only), 
                10 (PUT only), and 11.
        Notes:
            - Field validation is context-sensitive based on the Source field's value.
        
        Future updates: 
            * Maintain current request structure, but flatten requests for validation. It
            would be easier to separate the concern of validation by field or by validation 
            check. I would likely create a list of fields for each validation check and loop 
            through the validation list checking flattened_request[validated_field_list_element] 
            values in the order that validation checks must be run (missing field, missing 
            value, wrong type, and invalid list entry, followed by checks like datetime 
            format, primary key validity, and existence in the database). This would make 
            it easier both to skip optional values in the miss_req_value check and to 
            include the "N/A" string as a valid entry for fields not typed as strings. 
            Records would be reconstructed according to the scema definition prior to 
            record insertion.
        """
        error_info = (None, 0)  # (bad_key, error_type)
        
        # Validate "Source" field in request first to simplify paths
        if error_info[0] == None:
            if self._check.miss_req_field(self.SOURCE_KEY, self._chem_request_data):
                error_info = (self.SOURCE_KEY, self._errs.MISS_REQ_FIELD)
            elif self._check.miss_req_value(self._chem_request_data[self.SOURCE_KEY]):
                error_info = (self.SOURCE_KEY, self._errs.MISS_REQ_VALUE)
            elif self._check.wrong_type(
                self._chem_request_data[self.SOURCE_KEY],
                self.CHEMICAL_SCHEMA[self.SOURCE_KEY]
            ):
                error_info = (self.SOURCE_KEY, self._errs.WRONG_TYPE)
            elif self._check.inval_list_entry(
                self._chem_request_data[self.SOURCE_KEY],
                self._field_lists.sources
            ):
                error_info = (self.SOURCE_KEY, self._errs.INVAL_LIST_ENTRY)

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
                error_info = (extra_keys, self._errs.UNEXP_FIELD)
        
        # Validate remaining request fields. Assumes that "Source" is the last field 
        # shared between purchased and prepared chemicals to be validated.
        if error_info[0] == None:
            for key in self.CHEMICAL_SCHEMA:
                if not key in [self.SOURCE_KEY, self.PURCH_FIELD_KEY, self.PREP_FIELD_KEY]:
                    if self._check.miss_req_field(key, self._chem_request_data):
                        error_info = (key, self._errs.MISS_REQ_FIELD)
                        break
                    elif self._check.miss_req_value(self._chem_request_data[key]):
                        error_info = (key, self._errs.MISS_REQ_VALUE)
                        break
                    elif self._check.wrong_type(self._chem_request_data[key], self.CHEMICAL_SCHEMA[key]):
                        error_info = (key, self._errs.WRONG_TYPE)
                        break
                    elif key == self.CLASSIF_KEY:
                        if self._check.inval_list_entry(
                            self._chem_request_data[key],
                            self._field_lists.classifications
                        ):
                            error_info = (key, self._errs.INVAL_LIST_ENTRY)
                            break
                    elif key == self.STORAGE_KEY:
                        if self._check.inval_list_entry(
                            self._chem_request_data[key],
                            self._field_lists.storage_conditions
                        ):
                            error_info = (key, self._errs.INVAL_LIST_ENTRY)
                            break

                elif key == self.PURCH_FIELD_KEY and \
                    self._chem_request_data[self.SOURCE_KEY] == "Purchased":
                    # Validate "Purchased Fields" itself
                    if self._check.miss_req_field(key, self._chem_request_data):
                        error_info = (key, self._errs.MISS_REQ_FIELD)
                        break
                    elif self._check.miss_req_value(self._chem_request_data[key]):
                        error_info = (key, self._errs.MISS_REQ_VALUE)
                        break
                    elif self._check.wrong_type(
                        self._chem_request_data[key],
                        self.CHEMICAL_SCHEMA[key]
                    ):
                        error_info = (key, self._errs.WRONG_TYPE)
                        break

                    # Validate contents of "Purchased Fields"
                    purch_inner_dict = self.CHEMICAL_SCHEMA[key]
                    req_inner_dict = self._chem_request_data[key]

                    for inner_key in purch_inner_dict:
                        if self._check.miss_req_field(inner_key, req_inner_dict):
                            error_info = (inner_key, self._errs.MISS_REQ_FIELD)
                            break
                        elif self._check.miss_req_value(req_inner_dict[inner_key]):
                            error_info = (inner_key, self._errs.MISS_REQ_VALUE)
                            break
                        elif isinstance(purch_inner_dict[inner_key], list):
                            if self._check.wrong_type(req_inner_dict[inner_key], purch_inner_dict[inner_key]):
                                error_info = (inner_key, self._errs.WRONG_TYPE)
                                break
                        elif self._check.wrong_type(req_inner_dict[inner_key], purch_inner_dict[inner_key]):
                            error_info = (inner_key, self._errs.WRONG_TYPE)
                            break
                        elif inner_key == self.MANU_KEY:
                            if self._check.inval_list_entry(
                                req_inner_dict[inner_key],
                                self._field_lists.manufacturers
                            ):
                                error_info = (inner_key, self._errs.INVAL_LIST_ENTRY)
                                break
                        elif inner_key == self.UNIT_KEY:
                            if self._check.inval_list_entry(
                                req_inner_dict[inner_key],
                                self._field_lists.units
                            ):
                                error_info = (inner_key, self._errs.INVAL_LIST_ENTRY)
                                break
                        elif inner_key == self.CONT_TYPE_KEY:
                            if self._check.inval_list_entry(
                                req_inner_dict[inner_key],
                                self._field_lists.containers
                            ):
                                error_info = (inner_key, self._errs.INVAL_LIST_ENTRY)
                                break
                
                elif key == self.PREP_FIELD_KEY and \
                    self._chem_request_data[self.SOURCE_KEY] == "Prepared":
                    # Validate "Prepared Fields" itself
                    if self._check.miss_req_field(key, self._chem_request_data):
                        error_info = (key, self._errs.MISS_REQ_FIELD)
                        break
                    elif self._check.miss_req_value(self._chem_request_data[key]):
                        error_info = (key, self._errs.MISS_REQ_VALUE)
                        break
                    elif self._check.wrong_type(
                        self._chem_request_data[key],
                        self.CHEMICAL_SCHEMA[key]
                    ):
                        error_info = (key, self._errs.WRONG_TYPE)
                        break

                    # Validate contents of "Prepared Fields"
                    prep_inner_dict = self.CHEMICAL_SCHEMA[key]
                    req_inner_dict = self._chem_request_data[key]

                    for inner_key in prep_inner_dict:
                        if self._check.miss_req_field(inner_key, req_inner_dict):
                            error_info = (inner_key, self._errs.MISS_REQ_FIELD)
                            break
                        elif self._check.miss_req_value(req_inner_dict[inner_key]):
                            error_info = (inner_key, self._errs.MISS_REQ_VALUE)
                            break
                        elif self._check.wrong_type(req_inner_dict[inner_key], prep_inner_dict[inner_key]):
                            error_info = (inner_key, self._errs.WRONG_TYPE)
                            break

                if not error_info[0] == None:
                    # Break outer loop if inner loops found an error
                    break

        if error_info[0] == None:
            # Chemical record existence validation
            # This follows validation because the form values are used in the queries.
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
                    error_info = (
                        chem_data[ChemicalSchema.CHEM_ID_KEY],
                        self._errs.CHEM_DUPLICATE
                    )

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
                        # Don't overwrite error code if primary key was not valid ObjectId
                        error_info = (str(self.__chem_req_id), self._errs.CHEM_NOT_FOUND)
        
                except InvalidId:
                    error_info = (str(self.__chem_req_id), self._errs.INVALID_ID)
                    
        return error_info

    def build_chem_record(
        self,
        req_method: str,
        chemical_id: ObjectId = ObjectId()
    ) -> dict:
        """
        Build a chemical record dictionary object for insertion or update.

        Args:
            req_method (str): HTTP request method.
            chemical_id (ObjectId): Primary key used for updating aggregate fields (PUT only).

        Returns:
            dict: Validated chemical record ready for insertion or update.
        """
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