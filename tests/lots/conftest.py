"""
# Chemical/Lot Choice as it Pertains to Test Design:

## Chemical/Lot Choice
* Mobile Phase A: A prepared chemical/lot using one purchased chemical/lot and
one prepared chemical/lot (Water, in-house) as components.
* Mobile Phase B: A prepared chemical/lot using three purchased chemicals/lots
as components. These three chemicals/lots are sufficient to test the system
as it is currently able to function
* The above prepared chemicals/lots require several purchased chemicals/lots and, by 
my contrivance, a prepared material (Water, in-house).

## Valid Chemical Configurations
Chemical requests can arrive in one of two configurations:

* Purchased materials
* Prepared materials

## Valid Lot Configurations:
Between Mobile Phase A and its components, the entire lot
validation class will be tested. Note that a prepared lot with only prepared lots/
chemicals as components is not explicitly tested because Mobile Phase A will force both paths
to execute. The valid lot configurations are:

* Lots of purchased chemicals/lots
* Lots of prepared chemicals/lots that use only purchased chemicals/lots as components
* Lots of prepared chemicals/lots that use a mix of purchased and prepared chemicals/lots as components.
* Lots of prepared chemicals/lots that use only prepared materials as components (not tested)


# Scenarios Tested:

## HTTP code 200:
* Verify that lot objects of all valid configurations are
successfully modified in or retrieved from the database.

## HTTP code 201
* Verify that lot objects of all valid configurations are
successfully inserted in the database.

## HTTP code 204
* Lot objects of all valid configurations are successfully deleted from 
the database.

## HTTP code 400
* Missing request bodies return error code 400.
* GET requests with malformed primary keys return error code 400

## HTTP code 404
* Lots not found in the database returr error code 404.
* Lots with parent chemical templates not found in the database return error code 404.

## HTTP code 422:
All fields in the lot request body, the primary key (if applicable), and
the nature of the request itself are tested individually to verify that the
system properly validates all applicable error codes:

* No required keys are missing from lot requests.
* No required values are left empty in lot requests.
* Verify that all fields in a lot request are the correct type.
* No fields in a lot request with entry constrained by a list contain values not in that list.
* No unexpected keys arrive in a lot request, nor in the fields of a purchased or prepared component in a lot request.
* Verify that prepared lots contain at least one component.
* Verify that a lot request's parent chemical exists in the database.
* Verify that all date strings are in ISO 8601 format with timezone offsets.
* Verify that optional data fields are not flagged for missing values.
* Verify that lot records used as components on other prepared lots exist in the database.
* Additionally, the system is designed to short-circuit upon the first error found in lot form validation
and return that error message. The tests ensure that requests with two errors
return the error message for the first error.
* Verify primary keys in request body and address match each other.
* Verify that request body contains a primary key.
* PUT: Verify that the lot requested for update exists in the database.
* PUT: Verify that the lot request does not contain a malformed primary key.
"""

import sys
import os

# Had to explicitly add root to sys.path for pytest to find the Flask app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest, copy

from app.utils.validation_error_codes import ValidationErrorCodes
from app.models.lots import LotSchema

from tests.conftest import post_all_lots

@pytest.fixture()
def gen_lot_extra_fields(
    client,
    post_all_lists,
    val_purch_lots,
    val_prep_lots
        ):
    # Copy valid lot schema to make invalid changes
    lots = post_all_lots(
        client,
        post_all_lists,
        val_purch_lots,
        val_prep_lots
    )

    val_purch_lot_1 = lots["val_purch_lot_1"]
    val_purch_lot_2 = lots["val_purch_lot_2"]
    val_prep_lot_1 = lots["val_prep_lot_1"]
    val_prep_lot_2 = lots["val_prep_lot_2"]

    purch_lot_1_extra_field = copy.deepcopy(val_purch_lot_1)
    purch_lot_2_extra_field = copy.deepcopy(val_purch_lot_2)
    prep_lot_1_extra_field = copy.deepcopy(val_prep_lot_1)
    prep_lot_2_extra_field = copy.deepcopy(val_prep_lot_2)
    prep_lot_1_extra_comp_field = copy.deepcopy(val_prep_lot_1)
    prep_lot_2_extra_comp_field = copy.deepcopy(val_prep_lot_2)
    
    
    # Make invalid updates to lots
    purch_lot_1_extra_field["foo"] = "bar"
    purch_lot_1_extra_field["fizz"] = "buzz"
    
    purch_lot_2_extra_field["foo"] = "bar"
    purch_lot_2_extra_field["fizz"] = "buzz"

    prep_lot_1_extra_field["foo"] = "bar"
    prep_lot_1_extra_field["fizz"] = "buzz"
    
    prep_lot_2_extra_field["foo"] = "bar"
    prep_lot_2_extra_field["fizz"] = "buzz"

    # Extra field on purchased component
    prep_lot_1_extra_comp_field[LotSchema.COMPONENTS_KEY][0]["foo"] = "bar"
    prep_lot_1_extra_comp_field[LotSchema.COMPONENTS_KEY][0]["fizz"] = "buzz"
    
    # Extra field on prepared component
    prep_lot_2_extra_comp_field[LotSchema.COMPONENTS_KEY][0]["foo"] = "bar"
    prep_lot_2_extra_comp_field[LotSchema.COMPONENTS_KEY][0]["fizz"] = "buzz"

    return [
        purch_lot_1_extra_field,
        purch_lot_2_extra_field,
        prep_lot_1_extra_field,
        prep_lot_2_extra_field,
        prep_lot_1_extra_comp_field,
        prep_lot_2_extra_comp_field
    ]

@pytest.fixture()
def gen_lots_bad_dates(
    client,
    post_all_lists,
    val_purch_lots,
    val_prep_lots
        ):
    # Copy valid lot schema to make invalid changes
    lots = post_all_lots(
        client,
        post_all_lists,
        val_purch_lots,
        val_prep_lots
    )

    val_purch_lot_1 = lots["val_purch_lot_1"]
    val_purch_lot_2 = lots["val_purch_lot_2"]
    val_prep_lot_1 = lots["val_prep_lot_1"]
    val_prep_lot_2 = lots["val_prep_lot_2"]

    purch_lot_1_open = copy.deepcopy(val_purch_lot_1)
    purch_lot_1_expiry = copy.deepcopy(val_purch_lot_1)
    purch_lot_1_empty = copy.deepcopy(val_purch_lot_1)
    purch_lot_2_open = copy.deepcopy(val_purch_lot_2)
    purch_lot_2_expiry = copy.deepcopy(val_purch_lot_2)
    purch_lot_2_empty = copy.deepcopy(val_purch_lot_2)
    prep_lot_1_prep = copy.deepcopy(val_prep_lot_1)
    prep_lot_1_expiry = copy.deepcopy(val_prep_lot_1)
    prep_lot_1_empty = copy.deepcopy(val_prep_lot_1)
    prep_lot_2_prep = copy.deepcopy(val_prep_lot_2)
    prep_lot_2_expiry = copy.deepcopy(val_prep_lot_2)
    prep_lot_2_empty = copy.deepcopy(val_prep_lot_2)

    purch_lot_1_open_offset = copy.deepcopy(val_purch_lot_1)
    purch_lot_1_expiry_offset = copy.deepcopy(val_purch_lot_1)
    purch_lot_1_empty_offset = copy.deepcopy(val_purch_lot_1)
    purch_lot_2_open_offset = copy.deepcopy(val_purch_lot_2)
    purch_lot_2_expiry_offset = copy.deepcopy(val_purch_lot_2)
    purch_lot_2_empty_offset = copy.deepcopy(val_purch_lot_2)
    prep_lot_1_prep_offset = copy.deepcopy(val_prep_lot_1)
    prep_lot_1_expiry_offset = copy.deepcopy(val_prep_lot_1)
    prep_lot_1_empty_offset = copy.deepcopy(val_prep_lot_1)
    prep_lot_2_prep_offset = copy.deepcopy(val_prep_lot_2)
    prep_lot_2_expiry_offset = copy.deepcopy(val_prep_lot_2)
    prep_lot_2_empty_offset = copy.deepcopy(val_prep_lot_2)
    
    # Make invalid updates to lots
    purch_lot_1_open[LotSchema.OPEN_KEY] = "1"
    purch_lot_1_expiry[LotSchema.EXPIRY_KEY] = "1"
    purch_lot_1_empty[LotSchema.EMPTY_KEY] = "1"
    purch_lot_2_open[LotSchema.OPEN_KEY] = "1"
    purch_lot_2_expiry[LotSchema.EXPIRY_KEY] = "1"
    purch_lot_2_empty[LotSchema.EMPTY_KEY] = "1"
    prep_lot_1_prep[LotSchema.PREP_DATE_KEY] = "1"
    prep_lot_1_expiry[LotSchema.EXPIRY_KEY] = "1"
    prep_lot_1_empty[LotSchema.EMPTY_KEY] = "1"
    prep_lot_2_prep[LotSchema.PREP_DATE_KEY] = "1"
    prep_lot_2_expiry[LotSchema.EXPIRY_KEY] = "1"
    prep_lot_2_empty[LotSchema.EMPTY_KEY] = "1"
    
    purch_lot_1_open_offset[LotSchema.OPEN_KEY] = "2025-05-08T14:15:00"
    purch_lot_1_expiry_offset[LotSchema.EXPIRY_KEY] = "2025-05-08T14:15:00"
    purch_lot_1_empty_offset[LotSchema.EMPTY_KEY] = "2025-05-08T14:15:00"
    purch_lot_2_open_offset[LotSchema.OPEN_KEY] = "2025-05-08T14:15:00"
    purch_lot_2_expiry_offset[LotSchema.EXPIRY_KEY] = "2025-05-08T14:15:00"
    purch_lot_2_empty_offset[LotSchema.EMPTY_KEY] = "2025-05-08T14:15:00"
    prep_lot_1_prep_offset[LotSchema.PREP_DATE_KEY] = "2025-05-08T14:15:00"
    prep_lot_1_expiry_offset[LotSchema.EXPIRY_KEY] = "2025-05-08T14:15:00"
    prep_lot_1_empty_offset[LotSchema.EMPTY_KEY] = "2025-05-08T14:15:00"
    prep_lot_2_prep_offset[LotSchema.PREP_DATE_KEY] = "2025-05-08T14:15:00"
    prep_lot_2_expiry_offset[LotSchema.EXPIRY_KEY] = "2025-05-08T14:15:00"
    prep_lot_2_empty_offset[LotSchema.EMPTY_KEY] = "2025-05-08T14:15:00"

    # I stop returning generated lots as dicts because it got really tedious right here.
    # It would be more clear, but the app was my focus; I jsut need the tests to work
    return [
        purch_lot_1_open,
        purch_lot_1_expiry,
        purch_lot_1_empty,
        purch_lot_2_open,
        purch_lot_2_expiry,
        purch_lot_2_empty,
        prep_lot_1_prep,
        prep_lot_1_expiry,
        prep_lot_1_empty,
        prep_lot_2_prep,
        prep_lot_2_expiry,
        prep_lot_2_empty,

        purch_lot_1_open_offset,
        purch_lot_1_expiry_offset,
        purch_lot_1_empty_offset,
        purch_lot_2_open_offset,
        purch_lot_2_expiry_offset,
        purch_lot_2_empty_offset,
        prep_lot_1_prep_offset,
        prep_lot_1_expiry_offset,
        prep_lot_1_empty_offset,
        prep_lot_2_prep_offset,
        prep_lot_2_expiry_offset,
        prep_lot_2_empty_offset
    ]

@pytest.fixture()
def gen_lots_good_optional_dates(
    client,
    post_all_lists,
    val_purch_lots,
    val_prep_lots
        ):
    # Copy valid lot schema to make invalid changes
    lots = post_all_lots(
        client,
        post_all_lists,
        val_purch_lots,
        val_prep_lots
    )

    val_purch_lot_1 = lots["val_purch_lot_1"]
    val_purch_lot_2 = lots["val_purch_lot_2"]
    val_prep_lot_1 = lots["val_prep_lot_1"]
    val_prep_lot_2 = lots["val_prep_lot_2"]

    purch_lot_1_valid_open = copy.deepcopy(val_purch_lot_1)
    purch_lot_1_valid_empty = copy.deepcopy(val_purch_lot_1)
    purch_lot_2_valid_open = copy.deepcopy(val_purch_lot_2)
    purch_lot_2_valid_empty = copy.deepcopy(val_purch_lot_2)
    prep_lot_1_valid_empty = copy.deepcopy(val_prep_lot_1)
    prep_lot_2_valid_empty = copy.deepcopy(val_prep_lot_2)

    purch_lot_1_valid_open[LotSchema.OPEN_KEY] = "2025-04-08T14:30:00-04:00"
    purch_lot_1_valid_empty[LotSchema.EMPTY_KEY] = "2025-04-09T14:30:00-04:00"
    purch_lot_2_valid_open[LotSchema.OPEN_KEY] = "2025-04-08T14:30:00-04:00"
    purch_lot_2_valid_empty[LotSchema.EMPTY_KEY] = "2025-04-09T14:30:00-04:00"
    prep_lot_1_valid_empty[LotSchema.EMPTY_KEY] = "2025-04-09T14:30:00-04:00"
    prep_lot_2_valid_empty[LotSchema.EMPTY_KEY] = "2025-04-09T14:30:00-04:00"

    return [
        purch_lot_1_valid_open,
        purch_lot_1_valid_empty,
        purch_lot_2_valid_open,
        purch_lot_2_valid_empty,
        prep_lot_1_valid_empty,
        prep_lot_2_valid_empty,
    ]


@pytest.fixture()
def gen_lots_miss_comp(
    client,
    post_all_lists,
    val_purch_lots,
    val_prep_lots
        ):
    # Copy valid lot schema to make invalid changes
    lots = post_all_lots(
        client,
        post_all_lists,
        val_purch_lots,
        val_prep_lots
    )

    val_prep_lot_1 = lots["val_prep_lot_1"]
    val_prep_lot_2 = lots["val_prep_lot_2"]

    prep_lot_1_miss_comp = copy.deepcopy(val_prep_lot_1)
    prep_lot_2_miss_comp = copy.deepcopy(val_prep_lot_2)

    # Make invalid updates to lots
    prep_lot_1_miss_comp[LotSchema.COMPONENTS_KEY] = []
    prep_lot_2_miss_comp[LotSchema.COMPONENTS_KEY] = []

    return [
        prep_lot_1_miss_comp,
        prep_lot_2_miss_comp
    ]

@pytest.fixture()
def gen_multiple_errors(
    client,
    post_all_lists,
    val_purch_lots,
    val_prep_lots
        ):
    # Copy valid lot schema to make invalid changes
    lots = post_all_lots(
        client,
        post_all_lists,
        val_purch_lots,
        val_prep_lots
    )

    val_purch_lot_1 = lots["val_purch_lot_1"]
    val_purch_lot_2 = lots["val_purch_lot_2"]
    val_prep_lot_1 = lots["val_prep_lot_1"]
    val_prep_lot_2 = lots["val_prep_lot_2"]

    purch_lot_1_extra_field_type = copy.deepcopy(val_purch_lot_1)
    purch_lot_2_extra_field_type = copy.deepcopy(val_purch_lot_2)
    prep_lot_1_extra_field_type = copy.deepcopy(val_prep_lot_1)
    prep_lot_2_extra_field_type = copy.deepcopy(val_prep_lot_2)

    purch_lot_1_extra_field_type["foo"] = "bar"
    purch_lot_2_extra_field_type["foo"] = "bar"
    prep_lot_1_extra_field_type["foo"] = "bar"
    prep_lot_2_extra_field_type["foo"] = "bar"

    purch_lot_1_extra_field_type.pop(LotSchema.MANU_LOT_KEY)
    purch_lot_2_extra_field_type.pop(LotSchema.MANU_LOT_KEY)
    prep_lot_1_extra_field_type.pop(LotSchema.AMT_KEY)
    prep_lot_2_extra_field_type.pop(LotSchema.AMT_KEY)

    return [
        purch_lot_1_extra_field_type,
        purch_lot_2_extra_field_type,
        prep_lot_1_extra_field_type,
        prep_lot_2_extra_field_type
    ]

@pytest.fixture()
def invalid_lots(
    client,
    post_all_lists,
    val_purch_lots,
    val_prep_lots
        ):
    """
    Defines permutations of valid HTTP request bodies with invalid data schema.
    Magic numbers, types, and string literals in this section are chosen
    specifically to break schema validation without being invalid HTTP requests.

    Returns a list of tuples containing (payload, expected error) of type
    (dict, str)

    Ideally this would be generated here as a fixture, but I couldn't get it to 
    work inside  my tests when using pytest.mark.parametrize. I copied/pasted into
    the tests that use it, but in the future would like to learn how to pass in
    the fixture.
    """
    # Copy valid lot schema to make invalid changes
    lots = post_all_lots(
        client,
        post_all_lists,
        val_purch_lots,
        val_prep_lots
    )

    valid_purchased_lot_1 = lots["val_purch_lot_1"]
    valid_purchased_lot_2 = lots["val_purch_lot_2"]
    valid_prepared_lot_1 = lots["val_prep_lot_1"]
    valid_prepared_lot_2 = lots["val_prep_lot_2"]

    # val_purch_lot_1 invalid permutations
    val_purch_1_chem_id_miss_field = copy.deepcopy(valid_purchased_lot_1)
    val_purch_1_chem_id_miss_field.pop(LotSchema.PARENT_CHEM_ID_KEY)

    val_purch_1_chem_id_miss_value = copy.deepcopy(valid_purchased_lot_1)
    val_purch_1_chem_id_miss_value[LotSchema.PARENT_CHEM_ID_KEY] = None

    val_purch_1_chem_id_type = copy.deepcopy(valid_purchased_lot_1)
    val_purch_1_chem_id_type[LotSchema.PARENT_CHEM_ID_KEY] = 1

    val_purch_1_manu_lot_miss_field = copy.deepcopy(valid_purchased_lot_1)
    val_purch_1_manu_lot_miss_field.pop(LotSchema.MANU_LOT_KEY)

    val_purch_1_manu_lot_miss_value = copy.deepcopy(valid_purchased_lot_1)
    val_purch_1_manu_lot_miss_value[LotSchema.MANU_LOT_KEY] = None

    val_purch_1_manu_lot_type = copy.deepcopy(valid_purchased_lot_1)
    val_purch_1_manu_lot_type[LotSchema.MANU_LOT_KEY] = 1

    val_purch_1_open_miss_field = copy.deepcopy(valid_purchased_lot_1)
    val_purch_1_open_miss_field.pop(LotSchema.OPEN_KEY)

    val_purch_1_open_type = copy.deepcopy(valid_purchased_lot_1)
    val_purch_1_open_type[LotSchema.OPEN_KEY] = 1

    val_purch_1_expiry_miss_field = copy.deepcopy(valid_purchased_lot_1)
    val_purch_1_expiry_miss_field.pop(LotSchema.EXPIRY_KEY)

    val_purch_1_expiry_miss_value = copy.deepcopy(valid_purchased_lot_1)
    val_purch_1_expiry_miss_value[LotSchema.EXPIRY_KEY] = None

    val_purch_1_expiry_type = copy.deepcopy(valid_purchased_lot_1)
    val_purch_1_expiry_type[LotSchema.EXPIRY_KEY] = 1

    val_purch_1_empty_miss_field = copy.deepcopy(valid_purchased_lot_1)
    val_purch_1_empty_miss_field.pop(LotSchema.EMPTY_KEY)

    val_purch_1_empty_type = copy.deepcopy(valid_purchased_lot_1)
    val_purch_1_empty_type[LotSchema.EMPTY_KEY] = 1


    # val_purch_lot_2 invalid permutations
    val_purch_2_chem_id_miss_field = copy.deepcopy(valid_purchased_lot_2)
    val_purch_2_chem_id_miss_field.pop(LotSchema.PARENT_CHEM_ID_KEY)

    val_purch_2_chem_id_miss_value = copy.deepcopy(valid_purchased_lot_2)
    val_purch_2_chem_id_miss_value[LotSchema.PARENT_CHEM_ID_KEY] = None

    val_purch_2_chem_id_type = copy.deepcopy(valid_purchased_lot_2)
    val_purch_2_chem_id_type[LotSchema.PARENT_CHEM_ID_KEY] = 1

    val_purch_2_manu_lot_miss_field = copy.deepcopy(valid_purchased_lot_2)
    val_purch_2_manu_lot_miss_field.pop(LotSchema.MANU_LOT_KEY)

    val_purch_2_manu_lot_miss_value = copy.deepcopy(valid_purchased_lot_2)
    val_purch_2_manu_lot_miss_value[LotSchema.MANU_LOT_KEY] = None

    val_purch_2_manu_lot_type = copy.deepcopy(valid_purchased_lot_2)
    val_purch_2_manu_lot_type[LotSchema.MANU_LOT_KEY] = 1

    val_purch_2_open_miss_field = copy.deepcopy(valid_purchased_lot_2)
    val_purch_2_open_miss_field.pop(LotSchema.OPEN_KEY)
    val_purch_2_open_type = copy.deepcopy(valid_purchased_lot_2)
    val_purch_2_open_type[LotSchema.OPEN_KEY] = 1

    val_purch_2_expiry_miss_field = copy.deepcopy(valid_purchased_lot_2)
    val_purch_2_expiry_miss_field.pop(LotSchema.EXPIRY_KEY)

    val_purch_2_expiry_miss_value = copy.deepcopy(valid_purchased_lot_2)
    val_purch_2_expiry_miss_value[LotSchema.EXPIRY_KEY] = None

    val_purch_2_expiry_type = copy.deepcopy(valid_purchased_lot_2)
    val_purch_2_expiry_type[LotSchema.EXPIRY_KEY] = 1

    val_purch_2_empty_miss_field = copy.deepcopy(valid_purchased_lot_2)
    val_purch_2_empty_miss_field.pop(LotSchema.EMPTY_KEY)

    val_purch_2_empty_type = copy.deepcopy(valid_purchased_lot_2)
    val_purch_2_empty_type[LotSchema.EMPTY_KEY] = 1


    # val_prep_lot_1 invalid permutations (purchased component only)
    val_prep_1_chem_id_miss_field = copy.deepcopy(valid_prepared_lot_1)
    val_prep_1_chem_id_miss_field.pop(LotSchema.PARENT_CHEM_ID_KEY)

    val_prep_1_chem_id_miss_value = copy.deepcopy(valid_prepared_lot_1)
    val_prep_1_chem_id_miss_value[LotSchema.PARENT_CHEM_ID_KEY] = None

    val_prep_1_chem_id_type = copy.deepcopy(valid_prepared_lot_1)
    val_prep_1_chem_id_type[LotSchema.PARENT_CHEM_ID_KEY] = 1

    val_prep_1_amt_miss_field = copy.deepcopy(valid_prepared_lot_1)
    val_prep_1_amt_miss_field.pop(LotSchema.AMT_KEY)

    val_prep_1_amt_miss_value = copy.deepcopy(valid_prepared_lot_1)
    val_prep_1_amt_miss_value[LotSchema.AMT_KEY] = None

    val_prep_1_amt_type = copy.deepcopy(valid_prepared_lot_1)
    val_prep_1_amt_type[LotSchema.AMT_KEY] = "Invalid type"

    val_prep_1_units_miss_field = copy.deepcopy(valid_prepared_lot_1)
    val_prep_1_units_miss_field.pop(LotSchema.UNIT_KEY)

    val_prep_1_units_miss_value = copy.deepcopy(valid_prepared_lot_1)
    val_prep_1_units_miss_value[LotSchema.UNIT_KEY] = None

    val_prep_1_units_type = copy.deepcopy(valid_prepared_lot_1)
    val_prep_1_units_type[LotSchema.UNIT_KEY] = 1

    val_prep_1_units_inval_list = copy.deepcopy(valid_prepared_lot_1)
    val_prep_1_units_inval_list[LotSchema.UNIT_KEY] = "Valid type that's not in list."
    
    val_prep_1_cont_miss_field = copy.deepcopy(valid_prepared_lot_1)
    val_prep_1_cont_miss_field.pop(LotSchema.CONT_TYPE_KEY)

    val_prep_1_cont_miss_value = copy.deepcopy(valid_prepared_lot_1)
    val_prep_1_cont_miss_value[LotSchema.CONT_TYPE_KEY] = None

    val_prep_1_cont_type = copy.deepcopy(valid_prepared_lot_1)
    val_prep_1_cont_type[LotSchema.CONT_TYPE_KEY] = 1

    val_prep_1_cont_inval_list = copy.deepcopy(valid_prepared_lot_1)
    val_prep_1_cont_inval_list[LotSchema.UNIT_KEY] = "Valid type that's not in list."

    val_prep_1_prep_miss_field = copy.deepcopy(valid_prepared_lot_1)
    val_prep_1_prep_miss_field.pop(LotSchema.PREP_DATE_KEY)

    val_prep_1_prep_miss_value = copy.deepcopy(valid_prepared_lot_1)
    val_prep_1_prep_miss_value[LotSchema.PREP_DATE_KEY] = None

    val_prep_1_prep_type = copy.deepcopy(valid_prepared_lot_1)
    val_prep_1_prep_type[LotSchema.PREP_DATE_KEY] = 1

    val_prep_1_expiry_miss_field = copy.deepcopy(valid_prepared_lot_1)
    val_prep_1_expiry_miss_field.pop(LotSchema.EXPIRY_KEY)

    val_prep_1_expiry_miss_value = copy.deepcopy(valid_prepared_lot_1)
    val_prep_1_expiry_miss_value[LotSchema.EXPIRY_KEY] = None

    val_prep_1_expiry_type = copy.deepcopy(valid_prepared_lot_1)
    val_prep_1_expiry_type[LotSchema.EXPIRY_KEY] = 1

    val_prep_1_empty_miss_field = copy.deepcopy(valid_prepared_lot_1)
    val_prep_1_empty_miss_field.pop(LotSchema.EMPTY_KEY)

    val_prep_1_empty_type = copy.deepcopy(valid_prepared_lot_1)
    val_prep_1_empty_type[LotSchema.EMPTY_KEY] = 1

    val_prep_1_comp_1_lot_id_miss_field = copy.deepcopy(valid_prepared_lot_1)
    val_prep_1_comp_1_lot_id_miss_field[LotSchema.COMPONENTS_KEY][0].pop(LotSchema.COMP_LOT_KEY)

    val_prep_1_comp_1_lot_id_miss_value = copy.deepcopy(valid_prepared_lot_1)
    val_prep_1_comp_1_lot_id_miss_value[LotSchema.COMPONENTS_KEY][0][LotSchema.COMP_LOT_KEY] = None

    val_prep_1_comp_1_lot_id_type = copy.deepcopy(valid_prepared_lot_1)
    val_prep_1_comp_1_lot_id_type[LotSchema.COMPONENTS_KEY][0][LotSchema.COMP_LOT_KEY] = 1

    val_prep_1_comp_1_amt_miss_field = copy.deepcopy(valid_prepared_lot_1)
    val_prep_1_comp_1_amt_miss_field[LotSchema.COMPONENTS_KEY][0].pop(LotSchema.AMT_KEY)

    val_prep_1_comp_1_amt_miss_value = copy.deepcopy(valid_prepared_lot_1)
    val_prep_1_comp_1_amt_miss_value[LotSchema.COMPONENTS_KEY][0][LotSchema.AMT_KEY] = None

    val_prep_1_comp_1_amt_type = copy.deepcopy(valid_prepared_lot_1)
    val_prep_1_comp_1_amt_type[LotSchema.COMPONENTS_KEY][0][LotSchema.AMT_KEY] = "Invalid type"

    val_prep_1_comp_1_units_miss_field = copy.deepcopy(valid_prepared_lot_1)
    val_prep_1_comp_1_units_miss_field[LotSchema.COMPONENTS_KEY][0].pop(LotSchema.UNIT_KEY)

    val_prep_1_comp_1_units_miss_value = copy.deepcopy(valid_prepared_lot_1)
    val_prep_1_comp_1_units_miss_value[LotSchema.COMPONENTS_KEY][0][LotSchema.UNIT_KEY] = None

    val_prep_1_comp_1_units_type = copy.deepcopy(valid_prepared_lot_1)
    val_prep_1_comp_1_units_type[LotSchema.COMPONENTS_KEY][0][LotSchema.UNIT_KEY] = 1

    val_prep_1_comp_1_units_inval_list = copy.deepcopy(valid_prepared_lot_1)
    val_prep_1_comp_1_units_inval_list[LotSchema.COMPONENTS_KEY][0][LotSchema.UNIT_KEY] = "Valid type that's not in list."


    # val_prep_lot_2 invalid permutations (checks both invalid prepased and prepared components)
    val_prep_2_chem_id_miss_field = copy.deepcopy(valid_prepared_lot_2)
    val_prep_2_chem_id_miss_field.pop(LotSchema.PARENT_CHEM_ID_KEY)

    val_prep_2_chem_id_miss_value = copy.deepcopy(valid_prepared_lot_2)
    val_prep_2_chem_id_miss_value[LotSchema.PARENT_CHEM_ID_KEY] = None

    val_prep_2_chem_id_type = copy.deepcopy(valid_prepared_lot_2)
    val_prep_2_chem_id_type[LotSchema.PARENT_CHEM_ID_KEY] = 1

    val_prep_2_amt_miss_field = copy.deepcopy(valid_prepared_lot_2)
    val_prep_2_amt_miss_field.pop(LotSchema.AMT_KEY)

    val_prep_2_amt_miss_value = copy.deepcopy(valid_prepared_lot_2)
    val_prep_2_amt_miss_value[LotSchema.AMT_KEY] = None

    val_prep_2_amt_type = copy.deepcopy(valid_prepared_lot_2)
    val_prep_2_amt_type[LotSchema.AMT_KEY] = "Invalid type"

    val_prep_2_units_miss_field = copy.deepcopy(valid_prepared_lot_2)
    val_prep_2_units_miss_field.pop(LotSchema.UNIT_KEY)

    val_prep_2_units_miss_value = copy.deepcopy(valid_prepared_lot_2)
    val_prep_2_units_miss_value[LotSchema.UNIT_KEY] = None

    val_prep_2_units_type = copy.deepcopy(valid_prepared_lot_2)
    val_prep_2_units_type[LotSchema.UNIT_KEY] = 1

    val_prep_2_units_inval_list = copy.deepcopy(valid_prepared_lot_2)
    val_prep_2_units_inval_list[LotSchema.UNIT_KEY] = "Valid type that's not in list."
    
    val_prep_2_cont_miss_field = copy.deepcopy(valid_prepared_lot_2)
    val_prep_2_cont_miss_field.pop(LotSchema.CONT_TYPE_KEY)

    val_prep_2_cont_miss_value = copy.deepcopy(valid_prepared_lot_2)
    val_prep_2_cont_miss_value[LotSchema.CONT_TYPE_KEY] = None

    val_prep_2_cont_type = copy.deepcopy(valid_prepared_lot_2)
    val_prep_2_cont_type[LotSchema.CONT_TYPE_KEY] = 1

    val_prep_2_cont_inval_list = copy.deepcopy(valid_prepared_lot_2)
    val_prep_2_cont_inval_list[LotSchema.CONT_TYPE_KEY] = "Valid type that's not in list."

    val_prep_2_prep_miss_field = copy.deepcopy(valid_prepared_lot_2)
    val_prep_2_prep_miss_field.pop(LotSchema.PREP_DATE_KEY)

    val_prep_2_prep_miss_value = copy.deepcopy(valid_prepared_lot_2)
    val_prep_2_prep_miss_value[LotSchema.PREP_DATE_KEY] = None

    val_prep_2_prep_type = copy.deepcopy(valid_prepared_lot_2)
    val_prep_2_prep_type[LotSchema.PREP_DATE_KEY] = 1

    val_prep_2_expiry_miss_field = copy.deepcopy(valid_prepared_lot_2)
    val_prep_2_expiry_miss_field.pop(LotSchema.EXPIRY_KEY)

    val_prep_2_expiry_miss_value = copy.deepcopy(valid_prepared_lot_2)
    val_prep_2_expiry_miss_value[LotSchema.EXPIRY_KEY] = None

    val_prep_2_expiry_type = copy.deepcopy(valid_prepared_lot_2)
    val_prep_2_expiry_type[LotSchema.EXPIRY_KEY] = 1

    val_prep_2_empty_miss_field = copy.deepcopy(valid_prepared_lot_2)
    val_prep_2_empty_miss_field.pop(LotSchema.EMPTY_KEY)

    val_prep_2_empty_type = copy.deepcopy(valid_prepared_lot_2)
    val_prep_2_empty_type[LotSchema.EMPTY_KEY] = 1

    val_prep_2_comp_1_lot_id_miss_field = copy.deepcopy(valid_prepared_lot_2)
    val_prep_2_comp_1_lot_id_miss_field[LotSchema.COMPONENTS_KEY][0].pop(LotSchema.COMP_LOT_KEY)

    val_prep_2_comp_1_lot_id_miss_value = copy.deepcopy(valid_prepared_lot_2)
    val_prep_2_comp_1_lot_id_miss_value[LotSchema.COMPONENTS_KEY][0][LotSchema.COMP_LOT_KEY] = None

    val_prep_2_comp_1_lot_id_type = copy.deepcopy(valid_prepared_lot_2)
    val_prep_2_comp_1_lot_id_type[LotSchema.COMPONENTS_KEY][0][LotSchema.COMP_LOT_KEY] = 1

    val_prep_2_comp_1_amt_miss_field = copy.deepcopy(valid_prepared_lot_2)
    val_prep_2_comp_1_amt_miss_field[LotSchema.COMPONENTS_KEY][0].pop(LotSchema.AMT_KEY)

    val_prep_2_comp_1_amt_miss_value = copy.deepcopy(valid_prepared_lot_2)
    val_prep_2_comp_1_amt_miss_value[LotSchema.COMPONENTS_KEY][0][LotSchema.AMT_KEY] = None

    val_prep_2_comp_1_amt_type = copy.deepcopy(valid_prepared_lot_2)
    val_prep_2_comp_1_amt_type[LotSchema.COMPONENTS_KEY][0][LotSchema.AMT_KEY] = "Invalid type"

    val_prep_2_comp_1_units_miss_field = copy.deepcopy(valid_prepared_lot_2)
    val_prep_2_comp_1_units_miss_field[LotSchema.COMPONENTS_KEY][0].pop(LotSchema.UNIT_KEY)

    val_prep_2_comp_1_units_miss_value = copy.deepcopy(valid_prepared_lot_2)
    val_prep_2_comp_1_units_miss_value[LotSchema.COMPONENTS_KEY][0][LotSchema.UNIT_KEY] = None

    val_prep_2_comp_1_units_type = copy.deepcopy(valid_prepared_lot_2)
    val_prep_2_comp_1_units_type[LotSchema.COMPONENTS_KEY][0][LotSchema.UNIT_KEY] = 1

    val_prep_2_comp_1_units_inval_list = copy.deepcopy(valid_prepared_lot_2)
    val_prep_2_comp_1_units_inval_list[LotSchema.COMPONENTS_KEY][0][LotSchema.UNIT_KEY] = "Valid type that's not in list."

    val_prep_2_comp_2_lot_id_miss_field = copy.deepcopy(valid_prepared_lot_2)
    val_prep_2_comp_2_lot_id_miss_field[LotSchema.COMPONENTS_KEY][1].pop(LotSchema.COMP_LOT_KEY)

    val_prep_2_comp_2_lot_id_miss_value = copy.deepcopy(valid_prepared_lot_2)
    val_prep_2_comp_2_lot_id_miss_value[LotSchema.COMPONENTS_KEY][1][LotSchema.COMP_LOT_KEY] = None

    val_prep_2_comp_2_lot_id_type = copy.deepcopy(valid_prepared_lot_2)
    val_prep_2_comp_2_lot_id_type[LotSchema.COMPONENTS_KEY][1][LotSchema.COMP_LOT_KEY] = 1

    val_prep_2_comp_2_amt_miss_field = copy.deepcopy(valid_prepared_lot_2)
    val_prep_2_comp_2_amt_miss_field[LotSchema.COMPONENTS_KEY][1].pop(LotSchema.AMT_KEY)

    val_prep_2_comp_2_amt_miss_value = copy.deepcopy(valid_prepared_lot_2)
    val_prep_2_comp_2_amt_miss_value[LotSchema.COMPONENTS_KEY][1][LotSchema.AMT_KEY] = None

    val_prep_2_comp_2_amt_type = copy.deepcopy(valid_prepared_lot_2)
    val_prep_2_comp_2_amt_type[LotSchema.COMPONENTS_KEY][1][LotSchema.AMT_KEY] = "Invalid type"

    val_prep_2_comp_2_units_miss_field = copy.deepcopy(valid_prepared_lot_2)
    val_prep_2_comp_2_units_miss_field[LotSchema.COMPONENTS_KEY][1].pop(LotSchema.UNIT_KEY)

    val_prep_2_comp_2_units_miss_value = copy.deepcopy(valid_prepared_lot_2)
    val_prep_2_comp_2_units_miss_value[LotSchema.COMPONENTS_KEY][1][LotSchema.UNIT_KEY] = None

    val_prep_2_comp_2_units_type = copy.deepcopy(valid_prepared_lot_2)
    val_prep_2_comp_2_units_type[LotSchema.COMPONENTS_KEY][1][LotSchema.UNIT_KEY] = 1

    val_prep_2_comp_2_units_inval_list = copy.deepcopy(valid_prepared_lot_2)
    val_prep_2_comp_2_units_inval_list[LotSchema.COMPONENTS_KEY][1][LotSchema.UNIT_KEY] = "Valid type that's not in list."

    # By now I've learned that I can inclue a name with the payload and expected error message,
    # but I declined to do so because it's a lot more copy/pasting for little gain right now.
    invalid_purch_lots = [
        # Invalid purchased lot 1 permutations
        (val_purch_1_chem_id_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
        (val_purch_1_chem_id_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
        (val_purch_1_chem_id_type, ValidationErrorCodes.WRONG_TYPE_MSG),
        (val_purch_1_manu_lot_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
        (val_purch_1_manu_lot_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
        (val_purch_1_manu_lot_type, ValidationErrorCodes.WRONG_TYPE_MSG),
        (val_purch_1_open_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
        (val_purch_1_open_type, ValidationErrorCodes.WRONG_TYPE_MSG),
        (val_purch_1_expiry_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
        (val_purch_1_expiry_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
        (val_purch_1_expiry_type, ValidationErrorCodes.WRONG_TYPE_MSG),                     # Payload 10
        (val_purch_1_empty_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
        (val_purch_1_empty_type, ValidationErrorCodes.WRONG_TYPE_MSG),

        # Invalid purchased lot 2 permutations
        (val_purch_2_chem_id_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
        (val_purch_2_chem_id_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
        (val_purch_2_chem_id_type, ValidationErrorCodes.WRONG_TYPE_MSG),
        (val_purch_2_manu_lot_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
        (val_purch_2_manu_lot_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
        (val_purch_2_manu_lot_type, ValidationErrorCodes.WRONG_TYPE_MSG),
        (val_purch_2_open_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),  
        (val_purch_2_open_type, ValidationErrorCodes.WRONG_TYPE_MSG),                       # Payload 20
        (val_purch_2_expiry_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
        (val_purch_2_expiry_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
        (val_purch_2_expiry_type, ValidationErrorCodes.WRONG_TYPE_MSG),
        (val_purch_2_empty_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
        (val_purch_2_empty_type, ValidationErrorCodes.WRONG_TYPE_MSG),
    ]

    invalid_prep_lots = [    
        # Invalid prepared lot 1 permutations
        (val_prep_1_chem_id_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
        (val_prep_1_chem_id_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
        (val_prep_1_chem_id_type, ValidationErrorCodes.WRONG_TYPE_MSG),
        (val_prep_1_amt_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
        (val_prep_1_amt_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),               # Payload 30
        (val_prep_1_amt_type, ValidationErrorCodes.WRONG_TYPE_MSG),
        (val_prep_1_units_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
        (val_prep_1_units_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
        (val_prep_1_units_type, ValidationErrorCodes.WRONG_TYPE_MSG),
        (val_prep_1_units_inval_list, ValidationErrorCodes.INVAL_LIST_ENTRY_MSG),
        (val_prep_1_cont_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
        (val_prep_1_cont_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
        (val_prep_1_cont_type, ValidationErrorCodes.WRONG_TYPE_MSG),
        (val_prep_1_cont_inval_list, ValidationErrorCodes.INVAL_LIST_ENTRY_MSG),
        (val_prep_1_prep_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),              # Payload 40
        (val_prep_1_prep_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
        (val_prep_1_prep_type, ValidationErrorCodes.WRONG_TYPE_MSG),
        (val_prep_1_expiry_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
        (val_prep_1_expiry_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
        (val_prep_1_expiry_type, ValidationErrorCodes.WRONG_TYPE_MSG),
        (val_prep_1_empty_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),  
        (val_prep_1_empty_type, ValidationErrorCodes.WRONG_TYPE_MSG),
        (val_prep_1_comp_1_lot_id_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
        (val_prep_1_comp_1_lot_id_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
        (val_prep_1_comp_1_lot_id_type, ValidationErrorCodes.WRONG_TYPE_MSG),               # Payload 50
        (val_prep_1_comp_1_amt_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
        (val_prep_1_comp_1_amt_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
        (val_prep_1_comp_1_amt_type, ValidationErrorCodes.WRONG_TYPE_MSG),
        (val_prep_1_comp_1_units_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
        (val_prep_1_comp_1_units_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
        (val_prep_1_comp_1_units_type, ValidationErrorCodes.WRONG_TYPE_MSG),
        (val_prep_1_comp_1_units_inval_list, ValidationErrorCodes.INVAL_LIST_ENTRY_MSG),

        # Invalid prepared lot 2 permutations
        (val_prep_2_chem_id_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
        (val_prep_2_chem_id_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
        (val_prep_2_chem_id_type, ValidationErrorCodes.WRONG_TYPE_MSG),                     # Payload 60
        (val_prep_2_amt_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
        (val_prep_2_amt_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
        (val_prep_2_amt_type, ValidationErrorCodes.WRONG_TYPE_MSG),
        (val_prep_2_units_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
        (val_prep_2_units_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
        (val_prep_2_units_type, ValidationErrorCodes.WRONG_TYPE_MSG),
        (val_prep_2_units_inval_list, ValidationErrorCodes.INVAL_LIST_ENTRY_MSG),
        (val_prep_2_cont_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
        (val_prep_2_cont_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
        (val_prep_2_cont_type, ValidationErrorCodes.WRONG_TYPE_MSG),                        # Payload 70
        (val_prep_2_cont_inval_list, ValidationErrorCodes.INVAL_LIST_ENTRY_MSG),
        (val_prep_2_prep_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
        (val_prep_2_prep_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
        (val_prep_2_prep_type, ValidationErrorCodes.WRONG_TYPE_MSG),
        (val_prep_2_expiry_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
        (val_prep_2_expiry_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
        (val_prep_2_expiry_type, ValidationErrorCodes.WRONG_TYPE_MSG),
        (val_prep_2_empty_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
        (val_prep_2_empty_type, ValidationErrorCodes.WRONG_TYPE_MSG),
        (val_prep_2_comp_1_lot_id_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),     # Payload 80
        (val_prep_2_comp_1_lot_id_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
        (val_prep_2_comp_1_lot_id_type, ValidationErrorCodes.WRONG_TYPE_MSG),
        (val_prep_2_comp_1_amt_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
        (val_prep_2_comp_1_amt_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
        (val_prep_2_comp_1_amt_type, ValidationErrorCodes.WRONG_TYPE_MSG),
        (val_prep_2_comp_1_units_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
        (val_prep_2_comp_1_units_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
        (val_prep_2_comp_1_units_type, ValidationErrorCodes.WRONG_TYPE_MSG),
        (val_prep_2_comp_1_units_inval_list, ValidationErrorCodes.INVAL_LIST_ENTRY_MSG),
        (val_prep_2_comp_2_lot_id_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),     # Payload 90
        (val_prep_2_comp_2_lot_id_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
        (val_prep_2_comp_2_lot_id_type, ValidationErrorCodes.WRONG_TYPE_MSG),
        (val_prep_2_comp_2_amt_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
        (val_prep_2_comp_2_amt_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
        (val_prep_2_comp_2_amt_type, ValidationErrorCodes.WRONG_TYPE_MSG),
        (val_prep_2_comp_2_units_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
        (val_prep_2_comp_2_units_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
        (val_prep_2_comp_2_units_type, ValidationErrorCodes.WRONG_TYPE_MSG),
        (val_prep_2_comp_2_units_inval_list, ValidationErrorCodes.INVAL_LIST_ENTRY_MSG),
    ]

    return {
        "invalid_purch_lots": invalid_purch_lots,
        "invalid_prep_lots": invalid_prep_lots
    }