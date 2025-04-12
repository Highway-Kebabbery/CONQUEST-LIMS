"""
Schema validation and record management for system lists.

This module defines the ListsSchema class which validates input for
list records submitted to the system, builds records to be inserted, 
and handles the insertion of those records. These lists are used to 
constrain user entry in various fields throughout the system to promote
data harmonization and to maintain compliance with laboratory or 
business documentation (e.g., approved manufacturers, storage conditions,
units, etc.).

This module also includes methods for easy retrieval of validated lists 
for use in other validation modules.
"""

from flask import current_app
from app.utils.helper_functions import HelperFunctions
from app.utils.validation_error_codes import ValidationErrorCodes
from app.models.chemicals import ChemicalSchema

from pymongo.collection import Collection
from pymongo.results import InsertOneResult, UpdateResult
from typing import Any, Union

class ListsSchema():    
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
    # I want lists.Name (primary key) linked to field definitions in ChemicalSchema
    # which is defined AFTER ListSchema. This was my workaround to make that happen.
    @classmethod
    def CLASSIF_LIST_KEY(cls) -> str:
        """
        Returns the string value of the Classification field key defined in ChemicalSchema.
        Used to align list names with schema fields requiring list validation.
        """
        return ChemicalSchema.CLASSIF_KEY
    
    @classmethod
    def CONT_TYPES_LIST_KEY(cls) -> str:
        """
        Returns the string value of the Container_Type field key defined in ChemicalSchema.
        """
        return ChemicalSchema.CONT_TYPE_KEY
    
    @classmethod
    def MANU_LIST_KEY(cls) -> str:
        """
        Returns the string value of the Manufacturer field key defined in ChemicalSchema.
        """
        return ChemicalSchema.MANU_KEY
    
    @classmethod
    def SOURCES_LIST_KEY(cls) -> str:
        """
        Returns the string value of the Source field key defined in ChemicalSchema.
        """
        return ChemicalSchema.SOURCE_KEY
    
    @classmethod
    def STOR_COND_LIST_KEY(cls) -> str:
        """
        Returns the string value of the Storage_Condition field key defined in ChemicalSchema.
        """
        return ChemicalSchema.STORAGE_KEY
    
    @classmethod
    def UNITS_LIST_KEY(cls) -> str:
        """
        Returns the string value of the Units field key defined in ChemicalSchema.
        """
        return ChemicalSchema.UNIT_KEY

    @property
    def storage_conditions(self) -> str:
        """
        Returns the current list of validated storage conditions from the database.
        """
        storage_conditions = current_app.lists.find_one(
            {ListsSchema.LIST_NAME_KEY: ListsSchema.STOR_COND_LIST_KEY()}
        )
        
        return storage_conditions[ListsSchema.LIST_ENT_KEY]
    
    @property
    def units(self) -> str:
        """
        Returns the current list of validated units from the database.
        """
        units = current_app.lists.find_one(
            {ListsSchema.LIST_NAME_KEY: ListsSchema.UNITS_LIST_KEY()}
        )
        
        return units[ListsSchema.LIST_ENT_KEY]
    
    @property
    def containers(self) -> str:
        """
        Returns the current list of validated container types from the database.
        """
        containers = current_app.lists.find_one(
            {ListsSchema.LIST_NAME_KEY: ListsSchema.CONT_TYPES_LIST_KEY()}
        )
        
        return containers[ListsSchema.LIST_ENT_KEY]
    
    @property
    def sources(self) -> str:
        """
        Returns the current list of validated sources from the database.
        """
        sources = current_app.lists.find_one(
            {ListsSchema.LIST_NAME_KEY: ListsSchema.SOURCES_LIST_KEY()}
        )

        return sources[ListsSchema.LIST_ENT_KEY]
    
    @property
    def classifications(self) -> str:
        """
        Returns the current list of validated classifications from the database.
        """
        classifications = current_app.lists.find_one(
            {ListsSchema.LIST_NAME_KEY: ListsSchema.CLASSIF_LIST_KEY()}
        )
        
        return classifications[ListsSchema.LIST_ENT_KEY]
    
    @property
    def manufacturers(self) -> str:
        """
        Returns the current list of validated manufacturers from the database.
        """
        manufacturers = current_app.lists.find_one(
            {ListsSchema.LIST_NAME_KEY: ListsSchema.MANU_LIST_KEY()}
        )
        
        return manufacturers[ListsSchema.LIST_ENT_KEY]
    
    @staticmethod
    def check_list_name_exist(list_name: str) -> list[dict]:
        """
        Checks whether a list document exists in the database with the given primary key.

        Parameters:
            list_name (str): Name of the list to check.

        Returns:
            list[dict]: List of documents matching the given name (should be 0 or 1).
        """
        
        result = list(current_app.lists.find(
            {ListsSchema.LIST_NAME_KEY: list_name}
        ))

        return result

    def validate_list_form(self, request_method: str) -> tuple[Union[str, list[str], None], int]:
        # This function is designed to short-circuit at the first error detection

        """
        Validates the structure and content of the request body for a list object.

        Parameters:
            request_method (str): The HTTP method used in the request (typically POST or PUT).

        Returns:
            tuple:
                - Index 0: Affected field(s), as a string or list of strings. None if no error.
                - Index 1: Error code corresponding to ValidationErrorCodes class.
        
        Behaviour:
            - Short-circuits at the first error detected.
        """
            
        error_info = (None, 0)   # (str(affected fields), int(error_code))
        
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
                error_info = (extra_keys, self._errs.UNEXP_FIELD)
        
        # Validate types and existence of fields and values
        if error_info[0] == None:
            for key in self.LIST_SCHEMA:
                if key == self.LIST_NAME_KEY:
                    if self._check.miss_req_field(key, self._list_request_data):
                        error_info = (key, self._errs.MISS_REQ_FIELD)
                        break
                    elif self._check.miss_req_value(self._list_request_data[key]):
                        error_info = (key, self._errs.MISS_REQ_VALUE)
                        break
                    elif self._check.wrong_type(self._list_request_data[key], self.LIST_SCHEMA[key]):
                        error_info = (key, self._errs.WRONG_TYPE)
                        break
                elif key == self.LIST_ENT_KEY:
                    if self._check.miss_req_field(key, self._list_request_data):
                        error_info = (key, self._errs.MISS_REQ_FIELD)
                        break
                    elif self._check.miss_req_value(self._list_request_data[key]):
                        error_info = (key, self._errs.MISS_REQ_VALUE)
                        break
                    elif self._check.wrong_type(self._list_request_data[key], self.LIST_SCHEMA[key]):
                        error_info = (key, self._errs.WRONG_TYPE)
                        break
                    for entry in self._list_request_data[key]:
                        # miss_req_value() catches empty lists
                        if self._check.wrong_type(entry, self.LIST_ENTRY_TYPE):
                            error_info = (f"List entry: entry = {str(entry)}", self._errs.WRONG_TYPE)
                            break
                
                if not error_info[0] == None:
                    # Break outer loop if inner loop finds error.
                    # Redundant in current schema; future-proofing.
                    break
        
        # Check for existence or non-existence of requested list name (primary key)
        if error_info[0] == None:
            if request_method.upper() == "POST":
                if ListsSchema.check_list_name_exist(
                    self._list_request_data[self.LIST_NAME_KEY]
                ):
                    error_info = (
                        self._list_request_data[self.LIST_NAME_KEY],
                        self._errs.LIST_DUPLICATE
                    )
            elif request_method.upper() == "PUT":
                if not ListsSchema.check_list_name_exist(
                    self._list_request_data[self.LIST_NAME_KEY]
                ):
                    error_info = (
                        self._list_request_data[self.LIST_NAME_KEY],
                        self._errs.LIST_NOT_FOUND
                    )

        return error_info

    def build_list_record(self) -> dict[str, Union[str, list[str]]]:
        """
        Constructs a valid list record for insertion or update in the database
        using only required fields from the schema.

        Returns:
            dict: A complete and valid list document.
        """
        record = {}
        entries = []

        record[self.LIST_NAME_KEY] = str(self._list_request_data[self.LIST_NAME_KEY])
        for entry in self._list_request_data[self.LIST_ENT_KEY]:
            entries.append(str(entry))
        record[self.LIST_ENT_KEY] = entries

        return record
    
    def insert_update_list_record(
        self,
        lists_collection: Collection,
        record: dict[str, Any],
        req_method: str,
        list_name: str = ""
    ) -> InsertOneResult | UpdateResult:
        """
        Inserts or updates a validated list record in the database.

        Parameters:
            lists_collection (Collection): The MongoDB collection containing validated lists.
            record (dict[str, Any]): A dictionary representing the validated list record to insert or update.
            req_method (str): Either "POST" (to insert) or "PUT" (to update).
            list_name (str, optional): The name of the list to update when using PUT. Not used for POST.

        Returns:
            InsertOneResult | UpdateResult:
                The result of the insert or update operation; used to confirm write success.

        Behaviour:
            - If the request method is POST: inserts the record as a new document.
            - If the request method is PUT: updates an existing list record that matches the list_name.

        Note:
            Upstream validation is expected to ensure that `record` is valid
            and that the request context is appropriate for the operation.
        """

        if req_method.upper() == "POST":
            result = lists_collection.insert_one(record)
        elif req_method.upper() == "PUT":
            result = lists_collection.update_one(
                {ListsSchema.LIST_NAME_KEY: list_name},
                {"$set": record}
            )
        
        return result