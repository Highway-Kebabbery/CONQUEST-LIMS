"""
Schema validation and record management for lot records.

This module defines the LotSchema class which validates input for
lot records submitted to the system, builds records to be inserted, 
and handles the insertion of those records. The schema supports
both purchased and prepared lots and handles validation of nested
fields, including component information for prepared lots. Lot records
are related to chemicals via a "is-a" relationship: a particular lot
is a physical instance of a bottle of a particular chemical part number
available through a particular manufacturer, or otherwise a particular 
chemical whose preparation is prescribed in laboratory procedures.

Records are built from scratch during every POST/PUT operation to avoid
retaining unvalidated data and using the internal schema definition to
avoid the accidental injection of invalid fields.

Validation is short-circuited at the first error detected, so a request
returned with one error may have multiple issues.

Lot documents contain all information in their parent chemical record aside
from the aggregate data. These data are pulled from the chemical database
during lot record construction to minimize errors.

Prepared lots must contain at least one component. Components exist as 
references to other existing lot records and may be either purchased or 
prepared materials.
"""
from pymongo.collection import Collection
from app.utils.helper_functions import HelperFunctions
from app.utils.validation_error_codes import ValidationErrorCodes
from app.models.chemicals import ChemicalSchema

from bson import ObjectId
from bson.errors import InvalidId

class LotSchema(ChemicalSchema):
    LOT_ID_KEY = "_id" 
    PARENT_CHEM_ID_KEY = "chemical_id"              # Linked to chemicals._id
    COMP_LOT_KEY = "lot_id"                         # Links to lots._id. Specifies the lot used in this component.
    MANU_LOT_KEY = "Manufacturer_Lot_Batch_Number"
    OPEN_KEY = "Open_Date"
    EXPIRY_KEY = "Expiry_Date"
    EMPTY_KEY = "Empty_Date"
    PREP_DATE_KEY = "Preparation_Date"
    COMPONENTS_KEY = "Components"

    # Per component added to prepared material.
    #
    # Prepared and purchased component schema are currently redundant, but are left
    # split out to aid potential future updates where they diverge.
    PURCH_COMP_SCHEMA = {
        COMP_LOT_KEY: str,
        ChemicalSchema.AMT_KEY: ChemicalSchema.CHEMICAL_SCHEMA[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.AMT_KEY],        # Calculations with amounts must be performed with Decimal()
        ChemicalSchema.UNIT_KEY: ChemicalSchema.CHEMICAL_SCHEMA[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.UNIT_KEY]
    }
    
    PREP_COMP_SCHEMA = {
        COMP_LOT_KEY: str,
        ChemicalSchema.AMT_KEY: ChemicalSchema.CHEMICAL_SCHEMA[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.AMT_KEY],
        ChemicalSchema.UNIT_KEY: ChemicalSchema.CHEMICAL_SCHEMA[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.UNIT_KEY]
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

    def __init__(
        self,
        data: dict,
        chemicals_collection,
        lots_collection
    ) -> None:
        """
        Initialize a LotSchema object and validate the parent chemical ID. Makes use of
        ChemicalSchema.__init__().
        
        Parameters:
            data (dict): Lot request payload.
            chemicals_collection: MongoDB collection for chemical templates.
            lots_collection: MongoDB collection for lots.

        Raises:
            Sets internal error state for validation failures related to parent chemical ID.
        """
        self._lot_request_data = data
        self._check = HelperFunctions()
        self._errs = ValidationErrorCodes()

        # Used to short-circuit validation if chemical not found
        self._chem_id_error = (None, 0)    # (Field name(s), ValidationErrorCodes error code)

        # Pop _id to strip _lot_request_data for validation and build.
        if self.LOT_ID_KEY in self._lot_request_data:
            self.__lot_req_id = self._lot_request_data.pop(self.LOT_ID_KEY)
        # The system won't always use MongoDB's "_id" as the primary key; 
        # this line accounts for that.
        if "_id" in self._lot_request_data:
            self.__mongo_id = self._lot_request_data.pop("_id")
        
        try:
            # Check for and return the parent chemical form's data. This is cleaned in 
            # ChemicalSchema.__init__(). The chemicals and lots collections are 
            # ChemicalSchema instance parameters and super().__init__() has not been
            # called yet, so they must be passed using the parameter names in 
            # LotSchema.__init__() before they can be referenced using "self."
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
                # This checks the type using the purchased chemical schema, but both schema 
                # should always have same type and position for this field.
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
            # query result, but the ChemicalSchema name "self._chem_data" may be confusing 
            # in the context of a lot object.
            #
            # Rename to "self._chem_data," which makes more sense in the context of
            # LotSchema's use case.
            self._chem_data = self._chem_request_data
        
        except InvalidId:
            self._chem_id_error = [
                str(self._lot_request_data[self.PARENT_CHEM_ID_KEY,]),
                self._errs.INVALID_ID
            ]
        
        # For the following exceptions: error has been stored. validate_lot_form()
        # will catch it immediately.
        except KeyError:
            pass
        except ValueError:
            pass
        except TypeError:
            pass
        except FileNotFoundError:
            pass
        
    def validate_lot_form(
        self,
        request_method: str
    ) -> tuple[str | list[str] | None, int]:
        """
        Validates the lot request form against the defined record schema. Checks
        for: presence of required fields and value, validity of value types, presence 
        of list-entry fields values in validated lists, presence of unexpected request
        fields, existence of parent chemical template record in the databse, date
        strings in ISO 8601 format with timezone offset, presence of at least one 
        component (prepared lots), existence of the lot to be updated or of a lot 
        referenced in a prepared lot's components in the database (PUT), and 
        whether the provided primary key is a string form of a valid ObjectId
        object.

        Parameters:
            request_method (str): HTTP method, ("POST" or "PUT").

        Returns:
            tuple: (bad_key(s), validation_error_code). Returns (None, 0) if no errors are found.
                * ValidationErrorCodes returned: 1, 2, 3, 4, 5, 6, 7, 8, 10, and 11.

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
            record insertion. (Mirrors update to ChemicalSchema.validate_chemical_form().)
        """
        # Now is the time to validate errors encountered in LotSchema.__init__()
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
                    error_info = ("", self._errs.MISSING_COMP)
                elif not request_keys[1] == 1:
                    # request_keys[1] returns the number of components in the request. This block
                    # adds, once for every component in the request beyond one component, each
                    # field associated with the components schema; including the "Components" key
                    # itself.This is required for the extra_keys logic to work.
                    # 
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
                    error_info = (extra_keys, self._errs.UNEXP_FIELD)
        
        # Validate fields in request
        #
        ## PARENT_CHEM_ID validated in LotSchema.__init__() for type and 
        ## existence in database.
        ##
        ## Note that a lot itself can have a prepared or purchased parent chemical 
        ## template, but so also can the components of a prepared lot have a 
        ## purchased or prepared parent chemical template.
        if error_info[0] == None:
            if self._chem_data[ChemicalSchema.SOURCE_KEY] == "Purchased":
                purch_schema = self.LOT_SCHEMA[ChemicalSchema.PURCH_FIELD_KEY]
                for key in purch_schema:
                    if key in [self.OPEN_KEY, self.EXPIRY_KEY, self.EMPTY_KEY]:
                        if self._check.miss_req_field(
                            key,
                            self._lot_request_data
                        ):
                            error_info = (key, self._errs.MISS_REQ_FIELD)
                            break
                        elif (key in [self.OPEN_KEY, self.EMPTY_KEY]) and \
                            self._lot_request_data[key] == None:
                            # These VALUES are optional. Skip remaining checks.
                            continue
                        elif self._check.miss_req_value(
                            self._lot_request_data[key]
                        ):
                            # Check expiry date for value presence. Redundant for other two date fields.
                            error_info = (key, self._errs.MISS_REQ_VALUE)
                            break
                        elif self._check.wrong_type(
                            self._lot_request_data[key],
                            purch_schema[key]
                        ):
                            error_info = (key, self._errs.WRONG_TYPE)
                            break
                        else:
                            try:
                                self._check.to_datetime_utc(
                                    self._lot_request_data[key]
                                )
                            except ValueError:
                                error_info = (key, self._errs.WRONG_DATE_FORMAT)
                                break

                    elif self._check.miss_req_field(
                        key,
                        self._lot_request_data
                    ):
                        error_info = (key, self._errs.MISS_REQ_FIELD)
                        break
                    elif self._check.miss_req_value(self._lot_request_data[key]) and \
                        (not key in [self.OPEN_KEY, self.EMPTY_KEY]):
                            error_info = (key, self._errs.MISS_REQ_VALUE)
                            break
                    elif self._check.wrong_type(self._lot_request_data[key], purch_schema[key]):
                        error_info = (key, self._errs.WRONG_TYPE)
                        break
            elif self._chem_data[ChemicalSchema.SOURCE_KEY] == "Prepared":
                prep_schema = self.LOT_SCHEMA[ChemicalSchema.PREP_FIELD_KEY]
                for key in prep_schema:
                    if key in [self.PREP_DATE_KEY, self.EXPIRY_KEY, self.EMPTY_KEY]:
                        if self._check.miss_req_field(
                            key,
                            self._lot_request_data
                        ):
                            error_info = (key, self._errs.MISS_REQ_FIELD)
                            break
                        elif (key == self.EMPTY_KEY) and \
                            self._lot_request_data[key] == None:
                            # This VALUE is optional. Skip remaining checks.
                            continue
                        elif self._check.miss_req_value(
                            self._lot_request_data[key]
                        ):
                            # Check expiry date. Redundant for other two date fields.
                            error_info = (key, self._errs.MISS_REQ_VALUE)
                            break
                        elif self._check.wrong_type(
                            self._lot_request_data[key],
                            prep_schema[key]
                        ):
                            error_info = (key, self._errs.WRONG_TYPE)
                            break
                        else:
                            try:
                                self._check.to_datetime_utc(
                                    self._lot_request_data[key]
                                )
                            except ValueError:
                                error_info = (key, self._errs.WRONG_DATE_FORMAT)
                                break

                    elif isinstance(prep_schema[key], list):
                        # "Components" and "Amount" both have embedded lists as values
                        if key == self.COMPONENTS_KEY:
                            # Validate "Components" itself
                            if self._check.miss_req_field(
                                key,
                                self._lot_request_data
                            ):
                                error_info = (key, self._errs.MISS_REQ_FIELD)
                                break
                            elif self._check.miss_req_value(
                                self._lot_request_data[key]
                            ):
                                error_info = (key, self._errs.MISS_REQ_VALUE)
                                break
                            elif self._check.wrong_type(
                                self._lot_request_data[key],
                                prep_schema[key]
                            ):
                                error_info = (key, self._errs.WRONG_TYPE)
                                break
                            
                            # Loop through components and validate each
                            for component in self._lot_request_data[key]:
                                comp_index = self._lot_request_data[key].index(component)
                                req_comp_dict = self._lot_request_data[key][comp_index]
                                
                                # Validate LotSchema.COMP_LOT_KEY first to then determine whether component 
                                # gets prepared lot fields or purchased lot fields from the parent chemical 
                                # template.
                                if self._check.miss_req_field(
                                    LotSchema.COMP_LOT_KEY,
                                    req_comp_dict
                                ):
                                    error_info = (LotSchema.COMP_LOT_KEY, self._errs.MISS_REQ_FIELD)
                                    break
                                elif self._check.miss_req_value(
                                    req_comp_dict[LotSchema.COMP_LOT_KEY]
                                ):
                                        error_info = (LotSchema.COMP_LOT_KEY, self._errs.MISS_REQ_VALUE)
                                        break
                                elif self._check.wrong_type(
                                    req_comp_dict[LotSchema.COMP_LOT_KEY],
                                    prep_schema[LotSchema.COMPONENTS_KEY][0][LotSchema.COMP_LOT_KEY]
                                ):
                                    error_info = (LotSchema.COMP_LOT_KEY, self._errs.WRONG_TYPE)
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
                                            error_info = (
                                                f"{key}.Component #{comp_index + 1}.{LotSchema.COMP_LOT_KEY}",
                                                self._errs.LOT_NOT_FOUND
                                            )
                                            break
                                
                                except InvalidId:
                                    error_info = (
                                        f"{key}.Component #{comp_index + 1}.{LotSchema.COMP_LOT_KEY}",
                                        self._errs.INVALID_ID
                                    )

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
                                    if isinstance(schema_comp_dict[subkey], list):
                                        # "Amount" field
                                        if self._check.miss_req_field(
                                            subkey,
                                            req_comp_dict
                                        ):
                                            error_info = (
                                                f"{key}.Component #{comp_index + 1}.{subkey}",
                                                self._errs.MISS_REQ_FIELD
                                            )
                                            break
                                        elif self._check.miss_req_value(
                                            req_comp_dict[subkey]
                                        ):
                                            error_info = (
                                                f"{key}.Component #{comp_index + 1}.{subkey}",
                                                self._errs.MISS_REQ_VALUE
                                            )
                                            break
                                        elif self._check.wrong_type(
                                            req_comp_dict[subkey],
                                            schema_comp_dict[subkey]
                                        ):
                                            error_info = (
                                                f"{key}.Component #{comp_index + 1}.{subkey}",
                                                self._errs.WRONG_TYPE
                                            )
                                            break
                                    else:
                                        if self._check.miss_req_field(
                                            subkey, 
                                            req_comp_dict
                                        ):
                                            error_info = (
                                                f"{key}.Component #{comp_index + 1}.{subkey}",
                                                self._errs.MISS_REQ_FIELD
                                            )
                                            break
                                        elif self._check.miss_req_value(
                                            req_comp_dict[subkey]
                                        ):
                                            error_info = (
                                                f"{key}.Component #{comp_index + 1}.{subkey}",
                                                self._errs.MISS_REQ_VALUE
                                            )
                                            break
                                        elif self._check.wrong_type(
                                            req_comp_dict[subkey],
                                            schema_comp_dict[subkey]
                                        ):
                                            error_info = (
                                                f"{key}.Component #{comp_index + 1}.{subkey}",
                                                self._errs.WRONG_TYPE
                                            )
                                            break
                                        elif subkey == self.UNIT_KEY:
                                            if self._check.inval_list_entry(
                                                req_comp_dict[subkey],
                                                self._field_lists.units
                                                ):
                                                error_info = (
                                                    f"{key}.Component #{comp_index + 1}.{subkey}",
                                                    self._errs.INVAL_LIST_ENTRY
                                                )
                                                break
                                

                                if not error_info[0] == None:
                                    # Break outer loop if inner loops found an error
                                    break

                        else:
                            # Valiate "Amount" field
                            if self._check.miss_req_field(
                                key,
                                self._lot_request_data
                            ):
                                error_info = (key, self._errs.MISS_REQ_FIELD)
                                break
                            elif self._check.miss_req_value(
                                self._lot_request_data[key]
                            ):
                                error_info = (key, self._errs.MISS_REQ_VALUE)
                                break
                            elif self._check.wrong_type(
                                self._lot_request_data[key],
                                prep_schema[key]
                            ):
                               error_info = (key, self._errs.WRONG_TYPE)
                               break
                    elif self._check.miss_req_field(
                        key, self._lot_request_data
                    ):
                        error_info = (key, self._errs.MISS_REQ_FIELD)
                        break
                    elif self._check.miss_req_value(
                        self._lot_request_data[key]
                    ):
                        error_info = (key, self._errs.MISS_REQ_VALUE)
                        break
                    elif self._check.wrong_type(
                        self._lot_request_data[key],
                        prep_schema[key]
                    ):
                        error_info = (key, self._errs.WRONG_TYPE)
                        break
                    elif key == self.UNIT_KEY:
                        if self._check.inval_list_entry(
                            self._lot_request_data[key],
                            self._field_lists.units
                        ):
                            error_info = (key, self._errs.INVAL_LIST_ENTRY)
                            break
                    elif key == self.CONT_TYPE_KEY:
                        if self._check.inval_list_entry(
                            self._lot_request_data[key],
                            self._field_lists.containers
                        ):
                            error_info = (key, self._errs.INVAL_LIST_ENTRY)
                            break
                    
                    if not error_info[0] == None:
                        # Break outer loop if inner loops found an error
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
                        error_info = (
                            str(self.__lot_req_id),
                            self._errs.LOT_NOT_FOUND
                        )
                        
                except InvalidId:
                    error_info = (self.__lot_req_id, self._errs.INVALID_ID)
        
        return error_info
    
    def build_lot_record(self) -> dict:
        """
        Build a lot record dictionary object for insertion or update.

        Returns:
            dict: Validated lot record ready for insertion or update.
        """
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
            # 
            # Lot record info shared with parent chemical is pulled from chemical database
            # where applicable to prevent entry errors.
            for component in request[self.COMPONENTS_KEY]:
                component_attrs = {}

                # Primary key already evaluated to be valid.
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
    
    def insert_update_lot_record(
        self,
        chemicals_collection: Collection,
        lots_collection: Collection,
        record: dict,
        req_method: str,
        lot_id: str = ""
    ):
        """
        Inserts or updates a lot record in the lots collection. Also updates
        associated aggregate total fields on the related chemical record.

        Parameters:
            chemicals_collection: MongoDB chemicals collection
            lots_collection: MongoDB lots collection
            record (dict): Validated lot data verified by this class ready for database 
                insertion.
            req_method (str): HTTP method used ("POST" or "PUT")
            lot_id (str, optional): Primary key of the lot to update

        Returns:
            InsertOneResult | UpdateResult:
                Result object from the database operation.
        """
        if req_method.upper() == "POST":
            result = lots_collection.insert_one(record)
        
        elif req_method.upper() == "PUT":
            result = lots_collection.update_one(
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