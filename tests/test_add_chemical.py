"""
# Valid Chemical Configurations
Chemical requests can arrive in one of four configurations:

* Purchased materials
* Prepared materials with components that are purchased materials
* Prepared materials with components that are pother prepared materials
* Prepared materials with components that are a mix of purchased and
prepared materials

The system is not currently configured to allow prepared materials to use
other prepared materials as coponents. This is marked for a future update.
In the meantime, this test only builds a prepared chemical intended to use
exclusively purchased chemicals as components. A chemical meant to use
prepared reagents (e.g. in-house water) will be added to the test suite
after the system is changed to allow this. "All valid configurations" is
currently taken to mean either purchased chemicals or chemicals that use
only purchased materials as components.

# HTTP code 201:
* The tests verify that chemical objects of all valid configurations are
successfully inserted into the database.

# HTTP code 400:
* The test confirms that missing request bodies return error code 400.

# HTTP code 422:
All fields in the chemical document, the primary key (if applicable),
the nature of the request itself are tested individually to verify that the
system properly validates all applicable error codes:

* No required keys are missing from the request.
* No required values are left empty.
* No fields with entry constrained by a list contain values not in that list.
* No unexpected keys arrive in the request.
* PUT: The chemical requested for update exists in the database.
* POST: The request does nto attempt to create a new chemical with the same 
combination of manufacturer, manufacturer part number, amount, unit, and
container type as an existing chemical to prevent duplicate entries of the
same reagent or standard under different names.
* PUT: The request does not contain a malformed primary key.
* Additionally, the system is designed to short-circuit upon the first error
and return that error message. The tests ensure that requests with two errors
return the error message for the first error.

"""

import pytest, copy
from chemical_inventory_api_v1 import ChemicalSchema, ListsSchema, ValidationErrorCodes


# Define valid chemicals
valid_purchased_chemical_1 = {
    ChemicalSchema.NAME_KEY: "Methanol (Certified ACS), Fisher Chemical",
    ChemicalSchema.CAS_KEY: "67-56-1",
    ChemicalSchema.CLASSIF_KEY: "Flammable solvent",
    ChemicalSchema.STORAGE_KEY: "Ambient",
    ChemicalSchema.SOURCE_KEY: "Purchased",
    ChemicalSchema.PURCH_FIELD_KEY: {
        ChemicalSchema.MANU_KEY: "Fisher Scientific",
        ChemicalSchema.MANU_PN_KEY: "A412-4",
        ChemicalSchema.AMT_KEY: 4,
        ChemicalSchema.UNIT_KEY: "L",
        ChemicalSchema.CONT_TYPE_KEY: "Bottle"
    }
}

valid_purchased_chemical_2 = {
    ChemicalSchema.NAME_KEY: "Water, Optima LC/MS Grade, Fisher Chemical",
    ChemicalSchema.CAS_KEY: "7732-18-5",
    ChemicalSchema.CLASSIF_KEY: "Water",
    ChemicalSchema.STORAGE_KEY: "Ambient",
    ChemicalSchema.SOURCE_KEY: "Purchased",
    ChemicalSchema.PURCH_FIELD_KEY: {
        ChemicalSchema.MANU_KEY: "Fisher Scientific",
        ChemicalSchema.MANU_PN_KEY: "W64",
        ChemicalSchema.AMT_KEY: 4,
        ChemicalSchema.UNIT_KEY: "L",
        ChemicalSchema.CONT_TYPE_KEY: "Bottle"
    }
}


# Prepared chemical using only purchased components
valid_prepared_chemical_1 = {
    ChemicalSchema.NAME_KEY: "Methanol, 40% in Water",
    ChemicalSchema.CAS_KEY: "67-56-1, 7732-18-5",
    ChemicalSchema.CLASSIF_KEY: "Mobile phase",
    ChemicalSchema.STORAGE_KEY: "Ambient",
    ChemicalSchema.SOURCE_KEY: "Prepared",
    ChemicalSchema.PREP_FIELD_KEY: {
        ChemicalSchema.METH_REF_KEY: "SOP-00123.4.3.i"
        }
}

# Prepared chemical using prepared components
# This slot reserved for testing after future upgrade
valid_prepared_chemical_2 = {}

#_____________________________________________________________________________
# Permutations of valid HHTP requests with invalid data schema
# Magic numbers, types, and string literals in this section are chosen
# specifically to break schema validation without being invalid HTTP requests

# valid_purchased_chemical_1
# Name
val_purch_1_name_miss_field = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_name_miss_field.pop(ChemicalSchema.NAME_KEY)

val_purch_1_name_miss_value = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_name_miss_value[ChemicalSchema.NAME_KEY] = None

val_purch_1_name_type = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_name_type[ChemicalSchema.NAME_KEY] = 1

# CAS_Number
val_purch_1_cas_miss_field = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_cas_miss_field.pop(ChemicalSchema.CAS_KEY)

val_purch_1_cas_miss_value = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_cas_miss_value[ChemicalSchema.CAS_KEY] = None

val_purch_1_cas_type = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_cas_type[ChemicalSchema.CAS_KEY] = 1

# Classification
val_purch_1_classif_miss_field = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_classif_miss_field.pop(ChemicalSchema.CLASSIF_KEY)

val_purch_1_classif_miss_value = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_classif_miss_value[ChemicalSchema.CLASSIF_KEY] = None

val_purch_1_classif_type = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_classif_type[ChemicalSchema.CLASSIF_KEY] = 1

val_purch_1_classif_inval_list_entry = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_classif_inval_list_entry[ChemicalSchema.CLASSIF_KEY] = "Value of valid type but not in list"

# Source
val_purch_1_source_miss_field = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_source_miss_field.pop(ChemicalSchema.SOURCE_KEY)

val_purch_1_source_miss_value = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_source_miss_value[ChemicalSchema.SOURCE_KEY] = None

val_purch_1_source_type = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_source_type[ChemicalSchema.SOURCE_KEY] = 1

val_purch_1_source_inval_list_entry = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_source_inval_list_entry[ChemicalSchema.SOURCE_KEY] = "Value of valid type but not in list"

# Purchased_Fields
val_purch_1_purch_fields_miss_field = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_purch_fields_miss_field.pop(ChemicalSchema.PURCH_FIELD_KEY)

val_purch_1_purch_fields_miss_value = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_purch_fields_miss_value[ChemicalSchema.PURCH_FIELD_KEY] = None

val_purch_1_purch_fields_type = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_purch_fields_type[ChemicalSchema.PURCH_FIELD_KEY] = 1

# Manufacturer
val_purch_1_manu_miss_field = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_manu_miss_field[ChemicalSchema.PURCH_FIELD_KEY].pop(ChemicalSchema.MANU_KEY)

val_purch_1_manu_miss_value = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_manu_miss_value[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.MANU_KEY] = None

val_purch_1_manu_type = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_manu_type[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.MANU_KEY] = 1

val_purch_1_manu_inval_list_entry = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_manu_inval_list_entry[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.MANU_KEY] = "Value of valid type but not in list"

# Manufacturer_Part_Number
val_purch_1_manu_pn_miss_field = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_manu_pn_miss_field[ChemicalSchema.PURCH_FIELD_KEY].pop(ChemicalSchema.MANU_PN_KEY)

val_purch_1_manu_pn_miss_value = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_manu_pn_miss_value[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.MANU_PN_KEY] = None

val_purch_1_manu_pn_type = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_manu_pn_type[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.MANU_PN_KEY] = 1

# Amount
val_purch_1_amount_miss_field = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_amount_miss_field[ChemicalSchema.PURCH_FIELD_KEY].pop(ChemicalSchema.AMT_KEY)

val_purch_1_amount_miss_value = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_amount_miss_value[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.AMT_KEY] = None

val_purch_1_amount_type = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_amount_type[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.AMT_KEY] = "wrong type"

# Units
val_purch_1_units_miss_field = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_units_miss_field[ChemicalSchema.PURCH_FIELD_KEY].pop(ChemicalSchema.UNIT_KEY)

val_purch_1_units_miss_value = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_units_miss_value[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.UNIT_KEY] = None

val_purch_1_units_type = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_units_type[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.UNIT_KEY] = 1

val_purch_1_units_inval_list_entry = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_units_inval_list_entry[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.UNIT_KEY] = "Value of valid type but not in list"

# Container_Type
val_purch_1_container_miss_field = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_container_miss_field[ChemicalSchema.PURCH_FIELD_KEY].pop(ChemicalSchema.CONT_TYPE_KEY)

val_purch_1_container_miss_value = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_container_miss_value[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.CONT_TYPE_KEY] = None

val_purch_1_container_type = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_container_type[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.CONT_TYPE_KEY] = 1

val_purch_1_container_inval_list_entry = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_container_inval_list_entry[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.CONT_TYPE_KEY] = "Value of valid type but not in list"

# Unexpected Field
val_purch_1_container_extra_field = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_container_extra_field["foo"] = "bar"
val_purch_1_container_extra_field["fizz"] = "buzz"

# Do two error return the first-encountered error as expected?
val_purch_1_miss_field_type = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_miss_field_type.pop(ChemicalSchema.NAME_KEY)
val_purch_1_miss_field_type[ChemicalSchema.CAS_KEY] = True




# valid_purchased_chemical_2
# Name
val_purch_2_name_miss_field = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_name_miss_field.pop(ChemicalSchema.NAME_KEY)

val_purch_2_name_miss_value = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_name_miss_value[ChemicalSchema.NAME_KEY] = None

val_purch_2_name_type = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_name_type[ChemicalSchema.NAME_KEY] = 1

# CAS_Number
val_purch_2_cas_miss_field = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_cas_miss_field.pop(ChemicalSchema.CAS_KEY)

val_purch_2_cas_miss_value = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_cas_miss_value[ChemicalSchema.CAS_KEY] = None

val_purch_2_cas_type = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_cas_type[ChemicalSchema.CAS_KEY] = 1

# Classification
val_purch_2_classif_miss_field = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_classif_miss_field.pop(ChemicalSchema.CLASSIF_KEY)

val_purch_2_classif_miss_value = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_classif_miss_value[ChemicalSchema.CLASSIF_KEY] = None

val_purch_2_classif_type = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_classif_type[ChemicalSchema.CLASSIF_KEY] = 1

val_purch_2_classif_inval_list_entry = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_classif_inval_list_entry[ChemicalSchema.CLASSIF_KEY] = "Value of valid type but not in list"

# Source
val_purch_2_source_miss_field = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_source_miss_field.pop(ChemicalSchema.SOURCE_KEY)

val_purch_2_source_miss_value = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_source_miss_value[ChemicalSchema.SOURCE_KEY] = None

val_purch_2_source_type = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_source_type[ChemicalSchema.SOURCE_KEY] = 1

val_purch_2_source_inval_list_entry = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_source_inval_list_entry[ChemicalSchema.SOURCE_KEY] = "Value of valid type but not in list"

# Purchased_Fields
val_purch_2_purch_fields_miss_field = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_purch_fields_miss_field.pop(ChemicalSchema.PURCH_FIELD_KEY)

val_purch_2_purch_fields_miss_value = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_purch_fields_miss_value[ChemicalSchema.PURCH_FIELD_KEY] = None

val_purch_2_purch_fields_type = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_purch_fields_type[ChemicalSchema.PURCH_FIELD_KEY] = 1

# Manufacturer
val_purch_2_manu_miss_field = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_manu_miss_field[ChemicalSchema.PURCH_FIELD_KEY].pop(ChemicalSchema.MANU_KEY)

val_purch_2_manu_miss_value = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_manu_miss_value[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.MANU_KEY] = None

val_purch_2_manu_type = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_manu_type[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.MANU_KEY] = 1

val_purch_2_manu_inval_list_entry = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_manu_inval_list_entry[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.MANU_KEY] = "Value of valid type but not in list"

# Manufacturer_Part_Number
val_purch_2_manu_pn_miss_field = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_manu_pn_miss_field[ChemicalSchema.PURCH_FIELD_KEY].pop(ChemicalSchema.MANU_PN_KEY)

val_purch_2_manu_pn_miss_value = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_manu_pn_miss_value[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.MANU_PN_KEY] = None

val_purch_2_manu_pn_type = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_manu_pn_type[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.MANU_PN_KEY] = 1

# Amount
val_purch_2_amount_miss_field = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_amount_miss_field[ChemicalSchema.PURCH_FIELD_KEY].pop(ChemicalSchema.AMT_KEY)

val_purch_2_amount_miss_value = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_amount_miss_value[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.AMT_KEY] = None

val_purch_2_amount_type = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_amount_type[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.AMT_KEY] = "wrong type"

# Units
val_purch_2_units_miss_field = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_units_miss_field[ChemicalSchema.PURCH_FIELD_KEY].pop(ChemicalSchema.UNIT_KEY)

val_purch_2_units_miss_value = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_units_miss_value[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.UNIT_KEY] = None

val_purch_2_units_type = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_units_type[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.UNIT_KEY] = 1

val_purch_2_units_inval_list_entry = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_units_inval_list_entry[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.UNIT_KEY] = "Value of valid type but not in list"

# Container_Type
val_purch_2_container_miss_field = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_container_miss_field[ChemicalSchema.PURCH_FIELD_KEY].pop(ChemicalSchema.CONT_TYPE_KEY)

val_purch_2_container_miss_value = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_container_miss_value[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.CONT_TYPE_KEY] = None

val_purch_2_container_type = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_container_type[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.CONT_TYPE_KEY] = 1

val_purch_2_container_inval_list_entry = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_container_inval_list_entry[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.CONT_TYPE_KEY] = "Value of valid type but not in list"

# Unexpected Field
val_purch_2_container_extra_field = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_container_extra_field["foo"] = "bar"
val_purch_2_container_extra_field["fizz"] = "buzz"

# Do two error return the first-encountered error as expected?
val_purch_2_miss_field_type = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_miss_field_type.pop(ChemicalSchema.NAME_KEY)
val_purch_2_miss_field_type[ChemicalSchema.CAS_KEY] = True




# valid_prepared_chemical_1
# Name
val_prep_1_name_miss_field = copy.deepcopy(valid_prepared_chemical_1)
val_prep_1_name_miss_field.pop(ChemicalSchema.NAME_KEY)

val_prep_1_name_miss_value = copy.deepcopy(valid_prepared_chemical_1)
val_prep_1_name_miss_value[ChemicalSchema.NAME_KEY] = None

val_prep_1_name_type = copy.deepcopy(valid_prepared_chemical_1)
val_prep_1_name_type[ChemicalSchema.NAME_KEY] = 1

# CAS_Number
val_prep_1_cas_miss_field = copy.deepcopy(valid_prepared_chemical_1)
val_prep_1_cas_miss_field.pop(ChemicalSchema.CAS_KEY)

val_prep_1_cas_miss_value = copy.deepcopy(valid_prepared_chemical_1)
val_prep_1_cas_miss_value[ChemicalSchema.CAS_KEY] = None

val_prep_1_cas_type = copy.deepcopy(valid_prepared_chemical_1)
val_prep_1_cas_type[ChemicalSchema.CAS_KEY] = 1

# Classification
val_prep_1_classif_miss_field = copy.deepcopy(valid_prepared_chemical_1)
val_prep_1_classif_miss_field.pop(ChemicalSchema.CLASSIF_KEY)

val_prep_1_classif_miss_value = copy.deepcopy(valid_prepared_chemical_1)
val_prep_1_classif_miss_value[ChemicalSchema.CLASSIF_KEY] = None

val_prep_1_classif_type = copy.deepcopy(valid_prepared_chemical_1)
val_prep_1_classif_type[ChemicalSchema.CLASSIF_KEY] = 1

val_prep_1_classif_inval_list_entry = copy.deepcopy(valid_prepared_chemical_1)
val_prep_1_classif_inval_list_entry[ChemicalSchema.CLASSIF_KEY] = "Value of valid type but not in list"

# Storage_Condition
val_prep_1_stor_cond_miss_field = copy.deepcopy(valid_prepared_chemical_1)
val_prep_1_stor_cond_miss_field.pop(ChemicalSchema.STORAGE_KEY)

val_prep_1_stor_cond_miss_value = copy.deepcopy(valid_prepared_chemical_1)
val_prep_1_stor_cond_miss_value[ChemicalSchema.STORAGE_KEY] = None

val_prep_1_stor_cond_type = copy.deepcopy(valid_prepared_chemical_1)
val_prep_1_stor_cond_type[ChemicalSchema.STORAGE_KEY] = 1

val_prep_1_stor_cond_inval_list_entry = copy.deepcopy(valid_prepared_chemical_1)
val_prep_1_stor_cond_inval_list_entry[ChemicalSchema.STORAGE_KEY] = "Value of valid type but not in list"

# Source
val_prep_1_source_miss_field = copy.deepcopy(valid_prepared_chemical_1)
val_prep_1_source_miss_field.pop(ChemicalSchema.SOURCE_KEY)

val_prep_1_source_miss_value = copy.deepcopy(valid_prepared_chemical_1)
val_prep_1_source_miss_value[ChemicalSchema.SOURCE_KEY] = None

val_prep_1_source_type = copy.deepcopy(valid_prepared_chemical_1)
val_prep_1_source_type[ChemicalSchema.SOURCE_KEY] = 1

val_prep_1_source_inval_list_entry = copy.deepcopy(valid_prepared_chemical_1)
val_prep_1_source_inval_list_entry[ChemicalSchema.SOURCE_KEY] = "Value of valid type but not in list"

# Prepared_Fields
val_prep_1_prep_fields_miss_field = copy.deepcopy(valid_prepared_chemical_1)
val_prep_1_prep_fields_miss_field.pop(ChemicalSchema.PREP_FIELD_KEY)

val_prep_1_prep_fields_miss_value = copy.deepcopy(valid_prepared_chemical_1)
val_prep_1_prep_fields_miss_value[ChemicalSchema.PREP_FIELD_KEY] = None

val_prep_1_prep_fields_type = copy.deepcopy(valid_prepared_chemical_1)
val_prep_1_prep_fields_type[ChemicalSchema.PREP_FIELD_KEY] = 1

# Method_Step_Reference
val_prep_1_meth_miss_field = copy.deepcopy(valid_prepared_chemical_1)
# This particular error actually generates "Missing required value" for "Prepared_Fields"
# because it removes the only field in "Prepared_Fields" and leaves an empty dictionary.
# Rewrite test is schema is ever updated to allow multiple fields within Prepared_Fields.
val_prep_1_meth_miss_field[ChemicalSchema.PREP_FIELD_KEY].pop(ChemicalSchema.METH_REF_KEY)

val_prep_1_meth_miss_value = copy.deepcopy(valid_prepared_chemical_1)
val_prep_1_meth_miss_value[ChemicalSchema.PREP_FIELD_KEY][ChemicalSchema.METH_REF_KEY] = None

val_prep_1_meth_type = copy.deepcopy(valid_prepared_chemical_1)
val_prep_1_meth_type[ChemicalSchema.PREP_FIELD_KEY][ChemicalSchema.METH_REF_KEY] = 1

# Unexpected Field
val_prep_1_container_extra_field = copy.deepcopy(valid_prepared_chemical_1)
val_prep_1_container_extra_field["foo"] = "bar"
val_prep_1_container_extra_field["fizz"] = "buzz"

# Do two error return the first-encountered error as expected?
val_prep_1_miss_field_type = copy.deepcopy(valid_prepared_chemical_1)
val_prep_1_miss_field_type.pop(ChemicalSchema.NAME_KEY)
val_prep_1_miss_field_type[ChemicalSchema.CAS_KEY] = True



invalid_chemicals = [
    # Invalid purchased chemical 1 permutations
    (val_purch_1_name_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (val_purch_1_name_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_purch_1_name_type, ValidationErrorCodes.WRONG_TYPE_MSG),
    (val_purch_1_cas_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (val_purch_1_cas_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_purch_1_cas_type, ValidationErrorCodes.WRONG_TYPE_MSG),
    (val_purch_1_classif_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (val_purch_1_classif_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_purch_1_classif_type, ValidationErrorCodes.WRONG_TYPE_MSG),
    (val_purch_1_classif_inval_list_entry, ValidationErrorCodes.INVAL_LIST_ENTRY_MSG),
    (val_purch_1_source_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),               # Payload 10
    (val_purch_1_source_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_purch_1_source_type, ValidationErrorCodes.WRONG_TYPE_MSG),
    (val_purch_1_source_inval_list_entry, ValidationErrorCodes.INVAL_LIST_ENTRY_MSG),
    (val_purch_1_purch_fields_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (val_purch_1_purch_fields_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_purch_1_purch_fields_type, ValidationErrorCodes.WRONG_TYPE_MSG),
    (val_purch_1_manu_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (val_purch_1_manu_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_purch_1_manu_type, ValidationErrorCodes.WRONG_TYPE_MSG),
    (val_purch_1_manu_inval_list_entry, ValidationErrorCodes.INVAL_LIST_ENTRY_MSG),         # Payload 20
    (val_purch_1_manu_pn_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (val_purch_1_manu_pn_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_purch_1_manu_pn_type, ValidationErrorCodes.WRONG_TYPE_MSG),
    (val_purch_1_amount_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (val_purch_1_amount_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_purch_1_amount_type, ValidationErrorCodes.WRONG_TYPE_MSG),
    (val_purch_1_units_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (val_purch_1_units_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_purch_1_units_type, ValidationErrorCodes.WRONG_TYPE_MSG),
    (val_purch_1_units_inval_list_entry, ValidationErrorCodes.INVAL_LIST_ENTRY_MSG),        # Paylaod 30
    (val_purch_1_container_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (val_purch_1_container_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_purch_1_container_type, ValidationErrorCodes.WRONG_TYPE_MSG),
    (val_purch_1_container_inval_list_entry, ValidationErrorCodes.INVAL_LIST_ENTRY_MSG),
    
    # Invalid purchased chemical 2 permutations
    (val_purch_2_name_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (val_purch_2_name_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_purch_2_name_type, ValidationErrorCodes.WRONG_TYPE_MSG),
    (val_purch_2_cas_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (val_purch_2_cas_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_purch_2_cas_type, ValidationErrorCodes.WRONG_TYPE_MSG),                            # Payload 40
    (val_purch_2_classif_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (val_purch_2_classif_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_purch_2_classif_type, ValidationErrorCodes.WRONG_TYPE_MSG),
    (val_purch_2_classif_inval_list_entry, ValidationErrorCodes.INVAL_LIST_ENTRY_MSG),
    (val_purch_2_source_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (val_purch_2_source_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_purch_2_source_type, ValidationErrorCodes.WRONG_TYPE_MSG),
    (val_purch_2_source_inval_list_entry, ValidationErrorCodes.INVAL_LIST_ENTRY_MSG),
    (val_purch_2_purch_fields_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (val_purch_2_purch_fields_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),         # Payload 50
    (val_purch_2_purch_fields_type, ValidationErrorCodes.WRONG_TYPE_MSG),
    (val_purch_2_manu_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (val_purch_2_manu_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_purch_2_manu_type, ValidationErrorCodes.WRONG_TYPE_MSG),
    (val_purch_2_manu_inval_list_entry, ValidationErrorCodes.INVAL_LIST_ENTRY_MSG),
    (val_purch_2_manu_pn_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (val_purch_2_manu_pn_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_purch_2_manu_pn_type, ValidationErrorCodes.WRONG_TYPE_MSG),
    (val_purch_2_amount_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (val_purch_2_amount_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),               # Paylaod 60
    (val_purch_2_amount_type, ValidationErrorCodes.WRONG_TYPE_MSG),
    (val_purch_2_units_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (val_purch_2_units_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_purch_2_units_type, ValidationErrorCodes.WRONG_TYPE_MSG),
    (val_purch_2_units_inval_list_entry, ValidationErrorCodes.INVAL_LIST_ENTRY_MSG),
    (val_purch_2_container_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (val_purch_2_container_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_purch_2_container_type, ValidationErrorCodes.WRONG_TYPE_MSG),
    (val_purch_2_container_inval_list_entry, ValidationErrorCodes.INVAL_LIST_ENTRY_MSG),

    # Invalid prepared chemical 1 permutations
    (val_prep_1_name_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),                  # Payload 70
    (val_prep_1_name_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_prep_1_name_type, ValidationErrorCodes.WRONG_TYPE_MSG),
    (val_prep_1_cas_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (val_prep_1_cas_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_prep_1_cas_type, ValidationErrorCodes.WRONG_TYPE_MSG),
    (val_prep_1_classif_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (val_prep_1_classif_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_prep_1_classif_type, ValidationErrorCodes.WRONG_TYPE_MSG),
    (val_prep_1_classif_inval_list_entry, ValidationErrorCodes.INVAL_LIST_ENTRY_MSG),
    (val_prep_1_stor_cond_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),             # Payload 80
    (val_prep_1_stor_cond_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_prep_1_stor_cond_type, ValidationErrorCodes.WRONG_TYPE_MSG),
    (val_prep_1_stor_cond_inval_list_entry, ValidationErrorCodes.INVAL_LIST_ENTRY_MSG),
    (val_prep_1_source_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (val_prep_1_source_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_prep_1_source_type, ValidationErrorCodes.WRONG_TYPE_MSG),
    (val_prep_1_source_inval_list_entry, ValidationErrorCodes.INVAL_LIST_ENTRY_MSG),
    (val_prep_1_prep_fields_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (val_prep_1_prep_fields_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_prep_1_prep_fields_type, ValidationErrorCodes.WRONG_TYPE_MSG),                     # Payload 90
    (val_prep_1_meth_miss_field, ValidationErrorCodes.MISS_REQ_VALUE_MSG),  # See note in this payloads creation
    (val_prep_1_meth_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_prep_1_meth_type, ValidationErrorCodes.WRONG_TYPE_MSG)
]
#_____________________________________________________________________________

chemicals_address = "/chemicals"
lists_address = "/lists"

@pytest.fixture
def post_all_lists(client):
    # Validated lists
    classifications = {f"{ListsSchema.LIST_NAME_KEY}": ListsSchema.CLASSIF_LIST_KEY(), f"{ListsSchema.LIST_ENT_KEY}": ["Flammable solvent", "Strong acid", "Weak acid", "Strong base", "Weak base", "Mobile phase", "Reagent", "Standard", "Solid", "Dewer", "Gas cylinder", "Water"]}
    container_types = {f"{ListsSchema.LIST_NAME_KEY}": ListsSchema.CONT_TYPES_LIST_KEY(), f"{ListsSchema.LIST_ENT_KEY}": ["Ampoule", "Autosampler vial", "Bottle", "Vial"]}
    manufacturers = {f"{ListsSchema.LIST_NAME_KEY}": ListsSchema.MANU_LIST_KEY(), f"{ListsSchema.LIST_ENT_KEY}": ["3M", "Agilent", "Alfa Aesar", "Eppendorf", "Fisher Scientific", "Honeywell", "Sigma-Aldrich", "Thermo Fisher Scientific", "VWR"]}
    sources = {f"{ListsSchema.LIST_NAME_KEY}": ListsSchema.SOURCES_LIST_KEY(), f"{ListsSchema.LIST_ENT_KEY}": ["Purchased", "Prepared"]}
    storage_conditions = {f"{ListsSchema.LIST_NAME_KEY}": ListsSchema.STOR_COND_LIST_KEY(), f"{ListsSchema.LIST_ENT_KEY}": ["-80 °C", "-20 °C", "2-8 °C", "Ambient", "Ambient, dark", "Room temperature"]}
    units = {f"{ListsSchema.LIST_NAME_KEY}": ListsSchema.UNITS_LIST_KEY(), f"{ListsSchema.LIST_ENT_KEY}": ["g", "kg", "L", "mL", "µL"]}

    # POST valid lists and confirm success
    post_list_response_1 = client.post(lists_address, json=classifications)
    post_list_response_2 = client.post(lists_address, json=container_types)
    post_list_response_3 = client.post(lists_address, json=manufacturers)
    post_list_response_4 = client.post(lists_address, json=sources)
    post_list_response_5 = client.post(lists_address, json=storage_conditions)
    post_list_response_6 = client.post(lists_address, json=units)

    assert post_list_response_1.status_code == 201
    assert post_list_response_2.status_code == 201
    assert post_list_response_3.status_code == 201
    assert post_list_response_4.status_code == 201
    assert post_list_response_5.status_code == 201
    assert post_list_response_6.status_code == 201

 
def test_add_chemicals(client, post_all_lists):
    # POST valid chemicals of all types and confirm success
    #'''
    post_chem_response_1 = client.post(chemicals_address, json=valid_purchased_chemical_1)
    post_chem_response_2 = client.post(chemicals_address, json=valid_purchased_chemical_2)
    post_chem_response_3 = client.post(chemicals_address, json=valid_prepared_chemical_1)
    #post_chem_response_4 = client.post(chemicals_address, json=valid_prepared_chemical_2)

    assert post_chem_response_1.status_code == 201
    assert post_chem_response_2.status_code == 201
    assert post_chem_response_3.status_code == 201
    #assert post_chem_response_4.status_code == 201

    # Chemical duplicate
    post_chem_dup_response_purch = client.post(chemicals_address, json=valid_purchased_chemical_1)
    post_chem_dup_response_prep = client.post(chemicals_address, json=valid_prepared_chemical_1)

    data_1 = post_chem_dup_response_purch.get_json()
    data_2 = post_chem_dup_response_prep.get_json()

    assert post_chem_dup_response_purch.status_code == 422
    assert data_1["error"].startswith(ValidationErrorCodes.CHEM_DUPLICATE_MSG)
    assert post_chem_dup_response_prep.status_code == 422
    assert data_1["error"].startswith(ValidationErrorCodes.CHEM_DUPLICATE_MSG)

    # Confirm POST requests with empty body return 400
    empty_request_body = {}
    empty_body_reponse = client.post(chemicals_address, json=empty_request_body)

    assert empty_body_reponse.status_code == 400

    ## HTTP Code 422 response body Testing
    """
    Ensure all valid HTTP requests that fail ChemicalSchema validation return 422
    and the appropriate error message in the request body. Missing field, missing
    value, wrong type, and invalid list entry are handled in test_invalid_chemicals().
    """

    # Unexpected fields
    extra_field_chem_response_1 = client.post(chemicals_address, json=val_purch_1_container_extra_field)
    extra_field_chem_response_2 = client.post(chemicals_address, json=val_purch_2_container_extra_field)
    extra_field_chem_response_3= client.post(chemicals_address, json=val_prep_1_container_extra_field)

    data_1 = extra_field_chem_response_1.get_json()
    data_2 = extra_field_chem_response_2.get_json()
    data_3 = extra_field_chem_response_3.get_json()

    assert extra_field_chem_response_1.status_code == 422
    assert data_1["error"].startswith(ValidationErrorCodes.UNEXP_FIELD_MSG)
    assert extra_field_chem_response_2.status_code == 422
    assert data_2["error"].startswith(ValidationErrorCodes.UNEXP_FIELD_MSG)
    assert extra_field_chem_response_3.status_code == 422
    assert data_3["error"].startswith(ValidationErrorCodes.UNEXP_FIELD_MSG)

    # Two errors should return the first-encountered error
    miss_field_type_response_1 = client.post(chemicals_address, json=val_purch_1_miss_field_type)
    miss_field_type_response_2 = client.post(chemicals_address, json=val_purch_2_miss_field_type)
    miss_field_type_response_3 = client.post(chemicals_address, json=val_prep_1_miss_field_type)

    data_1 = miss_field_type_response_1.get_json()
    data_2 = miss_field_type_response_2.get_json()
    data_3 = miss_field_type_response_3.get_json()

    assert miss_field_type_response_1.status_code == 422
    assert data_1["error"].startswith(ValidationErrorCodes.MISS_REQ_FIELD_MSG)
    assert miss_field_type_response_2.status_code == 422
    assert data_2["error"].startswith(ValidationErrorCodes.MISS_REQ_FIELD_MSG)
    assert miss_field_type_response_3.status_code == 422
    assert data_3["error"].startswith(ValidationErrorCodes.MISS_REQ_FIELD_MSG)
    #'''

    # Comment out all other tests as well as test_invalid_chemicals and uncomment
    # this section for isolated troubleshooting of individual payloads
    '''
    payload = val_prep_1_meth_miss_field
    expected_error = ValidationErrorCodes.MISS_REQ_FIELD_MSG
    expected_status_code = 422

    response = client.post(chemicals_address, json=payload)
    data = response.get_json()

    print(f"Payload: {payload}")
    print(f"Expected error: {expected_error}")
    print(f"Error: {data['error']}")
    print(f"Expected status code: {expected_status_code}")
    print(f"Status code: {response.status_code}")
    

    assert response.status_code == expected_status_code
    assert data["error"].startswith(expected_error)
    '''

#'''
# Missing fields, missing values, wrong types, and invalid list entries
@pytest.mark.parametrize("payload, expected_error_prefix", invalid_chemicals)
def test_invalid_chemicals(client, payload, expected_error_prefix, post_all_lists):
    response = client.post(chemicals_address, json=copy.deepcopy(payload))
    data = response.get_json()

    assert response.status_code == 422
    if not data["error"].startswith(str(expected_error_prefix)):
        print(f"Payload: {payload}")
        print(f"Expected error: {expected_error_prefix}")
        print(f"Returned error: {data['error']}")
    assert data["error"].startswith(str(expected_error_prefix))
#'''