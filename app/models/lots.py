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

    def __init__(self, data, chemicals_collection, lots_collection):
        self._lot_request_data = data
        self._check = HelperFunctions()
        self._errs = ValidationErrorCodes()

        # Used to short-circuit validation if chemical not found
        self._chem_id_error = (None, 0)    # (Field name(s), ValidationErrorCodes error code)

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
                    error_info = ("", self._errs.MISSING_COMP)
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
                    error_info = (extra_keys, self._errs.UNEXP_FIELD)
        
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
                                
                                # Validate LotSchema.COMP_LOT_KEY first to then determine whether component gets
                                # prepared lot fields or purchased lot fields from the parent chemical template.
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
                                    if isinstance(schema_comp_dict[subkey], list):   # "Amount" field
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
                                    # This is in the event that inner loops found invalid data
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
                        error_info = (
                            str(self.__lot_req_id),
                            self._errs.LOT_NOT_FOUND
                        )
                        
                except InvalidId:
                    error_info = (self.__lot_req_id, self._errs.INVALID_ID)
        
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