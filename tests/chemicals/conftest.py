"""
# Chemical/Lot Choice as it Pertains to Test Design:

## Chemical Choice
* Mobile Phase A: A prepared chemical using one purchased chemical and
one prepared chemical (Water, in-house) as components.
* Mobile Phase B: A prepared chemical using three purchased chemicals
as components. These three chemicals are sufficient to test the system
as it is currently able to function
* The above prepared chemicals require several purchased chemicals and, by 
my contrivance, a prepared material (Water, in-house).

## Valid Chemical Configurations
Chemical requests can arrive in one of two configurations:

* Purchased materials
* Prepared materials

## Valid Lot Configurations:
It doesn't matter for the purposes of chemical testing, but these chemicals
were chosen because they can be used in lot testing to test all paths through
the lot validation logic. At the least, it is recommended to keep Mobile Phase A
for chemical testing. Between Mobile Phase A and its components, the entire lot
validation class will be tested. Note that a prepared lot with only prepared lots/
chemicals as components is not tested because Mobile Phase A will force both paths
to execute. The valid lot configurations are:

* Lots of purchased chemicals
* Lots of prepared chemicals that use only purchased chemicals as components
* Lots of prepared chemicals that use a mix of purchased and prepared chemicals as components.
* Lots of prepared chemicals that use only prepared materials as components (not tested)


# Scenarios Tested:

## HTTP code 200:
* The tests verify that chemical objects of all valid configurations are
successfully modified in or retrieved from the database.

## HTTP code 201
* The tests verify that chemical objects of all valid configurations are
successfully inserted in the database.

## HTTP code 204
* Chemical objects of all valid configurations are successfully deleted from 
the database.

## HTTP code 400
* Missing request bodies return error code 400.
* GET requests with malformed primary keys return error code 400

## HTTP code 404
* Chemicals not found in the database returr error code 404.

## HTTP code 422:
All fields in the chemical request body, the primary key (if applicable), and
the nature of the request itself are tested individually to verify that the
system properly validates all applicable error codes:

* No required keys are missing from chemical requests.
* No required values are left empty in chemical requests.
* All fields in a chemical request are the correct type.
* No fields in a chemical request with entry constrained by a list contain values not in that list.
* No unexpected keys arrive in a chemical request.
* PUT: The chemical requested for update exists in the database.
* POST: The chemical request does not attempt to create a new chemical with the same 
combination of manufacturer, manufacturer part number, amount, unit, and
container type as an existing chemical to prevent duplicate entries of the
same reagent or standard under different names.
* PUT: The chemical request does not contain a malformed primary key.
* Additionally, the system is designed to short-circuit upon the first error found in chemical form validation
and return that error message. The tests ensure that requests with two errors
return the error message for the first error.
* Confirm that primary keys match in the request body and address.
* PUT: All configurations of valid chemicals are checked for successful update agaianst each
configuration of a valid chemical.
* PUT: All invalid chemical configurations are tested for failure to update against
all valid chemical configurations.
"""

import sys
import os

# Had to explicitly add root to sys.path for pytest to find the Flask app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest, copy
from chemical_inventory_api_v1 import ChemicalSchema, ValidationErrorCodes

@pytest.fixture()
def purch_chem_1_extra_field(valid_purchased_chemical_1):
    # Unexpected Field
    purch_chem_1_extra_field = copy.deepcopy(valid_purchased_chemical_1)
    purch_chem_1_extra_field["foo"] = "bar"
    purch_chem_1_extra_field["fizz"] = "buzz"
    return purch_chem_1_extra_field

@pytest.fixture()
def purch_chem_2_extra_field(valid_purchased_chemical_2):
    # Unexpected Field
    purch_chem_2_extra_field = copy.deepcopy(valid_purchased_chemical_2)
    purch_chem_2_extra_field["foo"] = "bar"
    purch_chem_2_extra_field["fizz"] = "buzz"
    return purch_chem_2_extra_field

@pytest.fixture()
def prep_chem_1_extra_field(valid_prepared_chemical_1):
    # Unexpected Field
    prep_chem_1_extra_field = copy.deepcopy(valid_prepared_chemical_1)
    prep_chem_1_extra_field["foo"] = "bar"
    prep_chem_1_extra_field["fizz"] = "buzz"
    return prep_chem_1_extra_field

@pytest.fixture()
def prep_chem_2_extra_field(valid_prepared_chemical_2):
    # Unexpected Field
    prep_chem_2_extra_field = copy.deepcopy(valid_prepared_chemical_2)
    prep_chem_2_extra_field["foo"] = "bar"
    prep_chem_2_extra_field["fizz"] = "buzz"
    return prep_chem_2_extra_field
    
@pytest.fixture()
def purch_chem_1_miss_field_type(valid_purchased_chemical_1):
    # Do two error return the first-encountered error as expected?
    purch_chem_1_miss_field_type = copy.deepcopy(valid_purchased_chemical_1)
    purch_chem_1_miss_field_type.pop(ChemicalSchema.NAME_KEY)
    purch_chem_1_miss_field_type[ChemicalSchema.CAS_KEY] = True
    return purch_chem_1_miss_field_type

@pytest.fixture()
def purch_chem_2_miss_field_type(valid_purchased_chemical_2):
    # Do two error return the first-encountered error as expected?
    purch_chem_2_miss_field_type = copy.deepcopy(valid_purchased_chemical_2)
    purch_chem_2_miss_field_type.pop(ChemicalSchema.NAME_KEY)
    purch_chem_2_miss_field_type[ChemicalSchema.CAS_KEY] = True
    return purch_chem_2_miss_field_type

@pytest.fixture()
def prep_chem_1_miss_field_type(valid_prepared_chemical_1):
    # Do two error return the first-encountered error as expected?
    prep_chem_1_miss_field_type = copy.deepcopy(valid_prepared_chemical_1)
    prep_chem_1_miss_field_type.pop(ChemicalSchema.NAME_KEY)
    prep_chem_1_miss_field_type[ChemicalSchema.CAS_KEY] = True
    return prep_chem_1_miss_field_type

@pytest.fixture()
def prep_chem_2_miss_field_type(valid_prepared_chemical_2):
    # Do two error return the first-encountered error as expected?
    prep_chem_2_miss_field_type = copy.deepcopy(valid_prepared_chemical_2)
    prep_chem_2_miss_field_type.pop(ChemicalSchema.NAME_KEY)
    prep_chem_2_miss_field_type[ChemicalSchema.CAS_KEY] = True
    return prep_chem_2_miss_field_type

@pytest.fixture()
def invalid_chemicals(
    valid_purchased_chemical_1,
    valid_purchased_chemical_2,
    valid_prepared_chemical_1,
    valid_prepared_chemical_2
    ):
    """
    Defines permutations of valid HTTP request bodies with invalid data schema.
    Magic numbers, types, and string literals in this section are chosen
    specifically to break schema validation without being invalid HTTP requests.

    Returns a list of tuples containing (payload, expected error) of type
    (dict, str)
    """

    # Unexpected Field
    val_purch_1_container_extra_field = copy.deepcopy(valid_purchased_chemical_1)
    val_purch_1_container_extra_field["foo"] = "bar"
    val_purch_1_container_extra_field["fizz"] = "buzz"

    # Unexpected Field
    val_purch_2_container_extra_field = copy.deepcopy(valid_purchased_chemical_2)
    val_purch_2_container_extra_field["foo"] = "bar"
    val_purch_2_container_extra_field["fizz"] = "buzz"

    # Unexpected Field
    val_prep_1_container_extra_field = copy.deepcopy(valid_prepared_chemical_1)
    val_prep_1_container_extra_field["foo"] = "bar"
    val_prep_1_container_extra_field["fizz"] = "buzz"

    # Unexpected Field
    val_prep_2_container_extra_field = copy.deepcopy(valid_prepared_chemical_2)
    val_prep_2_container_extra_field["foo"] = "bar"
    val_prep_2_container_extra_field["fizz"] = "buzz"

    # Do two error return the first-encountered error as expected?
    val_purch_1_miss_field_type = copy.deepcopy(valid_purchased_chemical_1)
    val_purch_1_miss_field_type.pop(ChemicalSchema.NAME_KEY)
    val_purch_1_miss_field_type[ChemicalSchema.CAS_KEY] = True

    # Do two error return the first-encountered error as expected?
    val_purch_2_miss_field_type = copy.deepcopy(valid_purchased_chemical_2)
    val_purch_2_miss_field_type.pop(ChemicalSchema.NAME_KEY)
    val_purch_2_miss_field_type[ChemicalSchema.CAS_KEY] = True

    # Do two error return the first-encountered error as expected?
    val_prep_1_miss_field_type = copy.deepcopy(valid_prepared_chemical_1)
    val_prep_1_miss_field_type.pop(ChemicalSchema.NAME_KEY)
    val_prep_1_miss_field_type[ChemicalSchema.CAS_KEY] = True

    # Do two error return the first-encountered error as expected?
    val_prep_2_miss_field_type = copy.deepcopy(valid_prepared_chemical_2)
    val_prep_2_miss_field_type.pop(ChemicalSchema.NAME_KEY)
    val_prep_2_miss_field_type[ChemicalSchema.CAS_KEY] = True




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




    # valid_prepared_chemical_2
    # Name
    val_prep_2_name_miss_field = copy.deepcopy(valid_prepared_chemical_2)
    val_prep_2_name_miss_field.pop(ChemicalSchema.NAME_KEY)

    val_prep_2_name_miss_value = copy.deepcopy(valid_prepared_chemical_2)
    val_prep_2_name_miss_value[ChemicalSchema.NAME_KEY] = None

    val_prep_2_name_type = copy.deepcopy(valid_prepared_chemical_2)
    val_prep_2_name_type[ChemicalSchema.NAME_KEY] = 1

    # CAS_Number
    val_prep_2_cas_miss_field = copy.deepcopy(valid_prepared_chemical_2)
    val_prep_2_cas_miss_field.pop(ChemicalSchema.CAS_KEY)

    val_prep_2_cas_miss_value = copy.deepcopy(valid_prepared_chemical_2)
    val_prep_2_cas_miss_value[ChemicalSchema.CAS_KEY] = None

    val_prep_2_cas_type = copy.deepcopy(valid_prepared_chemical_2)
    val_prep_2_cas_type[ChemicalSchema.CAS_KEY] = 1

    # Classification
    val_prep_2_classif_miss_field = copy.deepcopy(valid_prepared_chemical_2)
    val_prep_2_classif_miss_field.pop(ChemicalSchema.CLASSIF_KEY)

    val_prep_2_classif_miss_value = copy.deepcopy(valid_prepared_chemical_2)
    val_prep_2_classif_miss_value[ChemicalSchema.CLASSIF_KEY] = None

    val_prep_2_classif_type = copy.deepcopy(valid_prepared_chemical_2)
    val_prep_2_classif_type[ChemicalSchema.CLASSIF_KEY] = 1

    val_prep_2_classif_inval_list_entry = copy.deepcopy(valid_prepared_chemical_2)
    val_prep_2_classif_inval_list_entry[ChemicalSchema.CLASSIF_KEY] = "Value of valid type but not in list"

    # Storage_Condition
    val_prep_2_stor_cond_miss_field = copy.deepcopy(valid_prepared_chemical_2)
    val_prep_2_stor_cond_miss_field.pop(ChemicalSchema.STORAGE_KEY)

    val_prep_2_stor_cond_miss_value = copy.deepcopy(valid_prepared_chemical_2)
    val_prep_2_stor_cond_miss_value[ChemicalSchema.STORAGE_KEY] = None

    val_prep_2_stor_cond_type = copy.deepcopy(valid_prepared_chemical_2)
    val_prep_2_stor_cond_type[ChemicalSchema.STORAGE_KEY] = 1

    val_prep_2_stor_cond_inval_list_entry = copy.deepcopy(valid_prepared_chemical_2)
    val_prep_2_stor_cond_inval_list_entry[ChemicalSchema.STORAGE_KEY] = "Value of valid type but not in list"

    # Source
    val_prep_2_source_miss_field = copy.deepcopy(valid_prepared_chemical_2)
    val_prep_2_source_miss_field.pop(ChemicalSchema.SOURCE_KEY)

    val_prep_2_source_miss_value = copy.deepcopy(valid_prepared_chemical_2)
    val_prep_2_source_miss_value[ChemicalSchema.SOURCE_KEY] = None

    val_prep_2_source_type = copy.deepcopy(valid_prepared_chemical_2)
    val_prep_2_source_type[ChemicalSchema.SOURCE_KEY] = 1

    val_prep_2_source_inval_list_entry = copy.deepcopy(valid_prepared_chemical_2)
    val_prep_2_source_inval_list_entry[ChemicalSchema.SOURCE_KEY] = "Value of valid type but not in list"

    # Prepared_Fields
    val_prep_2_prep_fields_miss_field = copy.deepcopy(valid_prepared_chemical_2)
    val_prep_2_prep_fields_miss_field.pop(ChemicalSchema.PREP_FIELD_KEY)

    val_prep_2_prep_fields_miss_value = copy.deepcopy(valid_prepared_chemical_2)
    val_prep_2_prep_fields_miss_value[ChemicalSchema.PREP_FIELD_KEY] = None

    val_prep_2_prep_fields_type = copy.deepcopy(valid_prepared_chemical_2)
    val_prep_2_prep_fields_type[ChemicalSchema.PREP_FIELD_KEY] = 1

    # Method_Step_Reference
    val_prep_2_meth_miss_field = copy.deepcopy(valid_prepared_chemical_2)
    # This particular error actually generates "Missing required value" for "Prepared_Fields"
    # because it removes the only field in "Prepared_Fields" and leaves an empty dictionary.
    # Rewrite test is schema is ever updated to allow multiple fields within Prepared_Fields.
    val_prep_2_meth_miss_field[ChemicalSchema.PREP_FIELD_KEY].pop(ChemicalSchema.METH_REF_KEY)

    val_prep_2_meth_miss_value = copy.deepcopy(valid_prepared_chemical_2)
    val_prep_2_meth_miss_value[ChemicalSchema.PREP_FIELD_KEY][ChemicalSchema.METH_REF_KEY] = None

    val_prep_2_meth_type = copy.deepcopy(valid_prepared_chemical_2)
    val_prep_2_meth_type[ChemicalSchema.PREP_FIELD_KEY][ChemicalSchema.METH_REF_KEY] = 1


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
        (val_prep_1_meth_type, ValidationErrorCodes.WRONG_TYPE_MSG),

        # Invalid prepared chemical 2 permutations
        (val_prep_2_name_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
        (val_prep_2_name_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
        (val_prep_2_name_type, ValidationErrorCodes.WRONG_TYPE_MSG),
        (val_prep_2_cas_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
        (val_prep_2_cas_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
        (val_prep_2_cas_type, ValidationErrorCodes.WRONG_TYPE_MSG),
        (val_prep_2_classif_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),               # Payload 100
        (val_prep_2_classif_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
        (val_prep_2_classif_type, ValidationErrorCodes.WRONG_TYPE_MSG),
        (val_prep_2_classif_inval_list_entry, ValidationErrorCodes.INVAL_LIST_ENTRY_MSG),
        (val_prep_2_stor_cond_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
        (val_prep_2_stor_cond_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
        (val_prep_2_stor_cond_type, ValidationErrorCodes.WRONG_TYPE_MSG),
        (val_prep_2_stor_cond_inval_list_entry, ValidationErrorCodes.INVAL_LIST_ENTRY_MSG),
        (val_prep_2_source_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
        (val_prep_2_source_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
        (val_prep_2_source_type, ValidationErrorCodes.WRONG_TYPE_MSG),                          # Payload 110
        (val_prep_2_source_inval_list_entry, ValidationErrorCodes.INVAL_LIST_ENTRY_MSG),
        (val_prep_2_prep_fields_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
        (val_prep_2_prep_fields_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
        (val_prep_2_meth_miss_field, ValidationErrorCodes.MISS_REQ_VALUE_MSG),  # See note in this payloads creation
        (val_prep_2_meth_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
        (val_prep_2_meth_type, ValidationErrorCodes.WRONG_TYPE_MSG)
    ]

    return invalid_chemicals