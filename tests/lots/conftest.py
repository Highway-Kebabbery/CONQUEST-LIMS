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


#RRRRRRRRRRRRRRRRRRREEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE Review this after all testing complete
* No required keys are missing from lot requests.
* No required values are left empty in lot requests.
* All fields in a lot request are the correct type.
* No fields in a lot request with entry constrained by a list contain values not in that list.
* No unexpected keys arrive in a lot request, nor in the fields of a purchased or prepared component in a lot request.
* PUT: The lot requested for update exists in the database.
* PUT: The lot request does not contain a malformed primary key.
* Additionally, the system is designed to short-circuit upon the first error found in lot form validation
and return that error message. The tests ensure that requests with two errors
return the error message for the first error.
* Confirm that primary keys match in the request body and address.


* Do I do this??????????RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRREEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE
* PUT: All configurations of valid lots are checked for successful update agaianst each
configuration of a valid lot.
* PUT: All invalid lot configurations are tested for failure to update against
all valid lot configurations.
*
*
*
**************************************************************************************
All notes above need to be.... checked once lot fixtures are built. With the main fixtures
in place I can begin to put together the finer details of checking lots.

### Strictly Lot-Related testing notes:

* Lots used for happy path testing confirm that null empty dates work
* All date strings in a lot request are in valid ISO 8601 format and include timezone offsets.

"""

import sys
import os

# Had to explicitly add root to sys.path for pytest to find the Flask app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

import pytest, copy, mongomock
from flask import Flask
from pymongo import MongoClient
from chemical_inventory_api_v1 import ChemicalSchema, ListsSchema, LotSchema, ValidationErrorCodes
from chemical_inventory_api_v1 import app as flask_app

chemicals_address = "/chemicals"
lots_address = "/lots"
lists_address = "/lists"

@pytest.fixture()
def app():
    flask_app.config.update({
        "TESTING": True
    })

    flask_app.mongo_client = mongomock.MongoClient()
    flask_app.db = flask_app.mongo_client.conquest_lims
    flask_app.chemicals = flask_app.db.chemicals
    flask_app.lots = flask_app.db.lots
    flask_app.lists = flask_app.db.lists
    
    with flask_app.mongo_client as client:
        # Not technically necessary since mongomock is in-memory, but left as reminder
        # when I check back that it's important to use something like `with` to clean
        # up connections after testing. This is a learning project for me.
        yield flask_app

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def post_all_lists(client):
    # Validated lists
    classifications = {f"{ListsSchema.LIST_NAME_KEY}": ListsSchema.CLASSIF_LIST_KEY(), f"{ListsSchema.LIST_ENT_KEY}": ["Flammable solvent", "Strong acid", "Weak acid", "Strong base", "Weak base", "Mobile phase", "Reagent", "Standard", "Solid", "Dewer", "Gas cylinder", "Water", "Water Dispenser"]}
    container_types = {f"{ListsSchema.LIST_NAME_KEY}": ListsSchema.CONT_TYPES_LIST_KEY(), f"{ListsSchema.LIST_ENT_KEY}": ["Ampoule", "Autosampler vial", "Bottle", "Vial", "Instrument", "N/A"]}
    manufacturers = {f"{ListsSchema.LIST_NAME_KEY}": ListsSchema.MANU_LIST_KEY(), f"{ListsSchema.LIST_ENT_KEY}": ["3M", "Agilent", "Alfa Aesar", "Eppendorf", "Fisher Scientific", "Honeywell", "J.T. Baker", "Milli-Q", "Sigma-Aldrich", "Thermo Fisher Scientific", "VWR"]}
    sources = {f"{ListsSchema.LIST_NAME_KEY}": ListsSchema.SOURCES_LIST_KEY(), f"{ListsSchema.LIST_ENT_KEY}": ["Purchased", "Prepared"]}
    storage_conditions = {f"{ListsSchema.LIST_NAME_KEY}": ListsSchema.STOR_COND_LIST_KEY(), f"{ListsSchema.LIST_ENT_KEY}": ["-80 °C", "-20 °C", "2-8 °C", "Ambient", "Ambient, dark", "Room temperature"]}
    units = {f"{ListsSchema.LIST_NAME_KEY}": ListsSchema.UNITS_LIST_KEY(), f"{ListsSchema.LIST_ENT_KEY}": ["g", "kg", "L", "mL", "µL", "N/A"]}

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


@pytest.fixture()
def val_purch_chems(client, post_all_lists):
    val_purch_chem_1 = {
        ChemicalSchema.NAME_KEY: "Milli-Q IQ 7000 Ultrapure Water Purification System. IPN: WAT-GNV-001",
        ChemicalSchema.CAS_KEY: "7732-18-5",
        ChemicalSchema.CLASSIF_KEY: "Water Dispenser",
        ChemicalSchema.STORAGE_KEY: "Ambient",
        ChemicalSchema.SOURCE_KEY: "Purchased",
        ChemicalSchema.PURCH_FIELD_KEY: {
            ChemicalSchema.MANU_KEY: "Milli-Q",
            ChemicalSchema.MANU_PN_KEY: "ZIQ7000T0C",
            ChemicalSchema.AMT_KEY: 999999,
            ChemicalSchema.UNIT_KEY: "N/A",
            ChemicalSchema.CONT_TYPE_KEY: "N/A"
        }
    }
    
    val_purch_chem_2 = {
        ChemicalSchema.NAME_KEY: "Phosphoric acid, J.T. Baker",
        ChemicalSchema.CAS_KEY: "7664-38-2",
        ChemicalSchema.CLASSIF_KEY: "Weak acid",
        ChemicalSchema.STORAGE_KEY: "Ambient",
        ChemicalSchema.SOURCE_KEY: "Purchased",
        ChemicalSchema.PURCH_FIELD_KEY: {
            ChemicalSchema.MANU_KEY: "Fisher Scientific",
            ChemicalSchema.MANU_PN_KEY: "02-003-602",
            ChemicalSchema.AMT_KEY: 500,
            ChemicalSchema.UNIT_KEY: "mL",
            ChemicalSchema.CONT_TYPE_KEY: "Bottle"
        }
    }

    response_1 = client.post(chemicals_address, json=val_purch_chem_1)
    response_2 = client.post(chemicals_address, json=val_purch_chem_2)

    assert response_1.status_code == 201
    assert response_2.status_code == 201

    id_1 = response_1.get_json()["inserted_id"]
    id_2 = response_2.get_json()["inserted_id"]

    return {
        "val_purch_chem_1": {
            **val_purch_chem_1, ChemicalSchema.CHEM_ID_KEY: id_1
        },
        "val_purch_chem_2": {
            **val_purch_chem_2, ChemicalSchema.CHEM_ID_KEY: id_2
        }
    }

@pytest.fixture()
def val_prep_chems(client, post_all_lists):
    # Prepared chemical using only purchased components (water dispenser)
    val_prep_chem_1 = {
        ChemicalSchema.NAME_KEY: "Water, In-House",
        ChemicalSchema.CAS_KEY: "7732-18-5",
        ChemicalSchema.CLASSIF_KEY: "Water",
        ChemicalSchema.STORAGE_KEY: "Ambient",
        ChemicalSchema.SOURCE_KEY: "Prepared",
        ChemicalSchema.PREP_FIELD_KEY: {
            ChemicalSchema.METH_REF_KEY: "Water Dispenser: WAT-GNV-001"
            }
    }

    # Prepared chemical using a prepared component
    val_prep_chem_2 = {
        ChemicalSchema.NAME_KEY: "Mobile Phase A: Water, 0.1 % Phosphoric Acid",
        ChemicalSchema.CAS_KEY: "7732-18-5, 7664-38-2",
        ChemicalSchema.CLASSIF_KEY: "Mobile phase",
        ChemicalSchema.STORAGE_KEY: "Ambient",
        ChemicalSchema.SOURCE_KEY: "Prepared",
        ChemicalSchema.PREP_FIELD_KEY: {
            ChemicalSchema.METH_REF_KEY: "SOP-00123.4.3.i"
            }
    }

    response_1 = client.post(chemicals_address, json=val_prep_chem_1)
    response_2 = client.post(chemicals_address, json=val_prep_chem_2)

    assert response_1.status_code == 201
    assert response_2.status_code == 201

    id_1 = response_1.get_json()["inserted_id"]
    id_2 = response_2.get_json()["inserted_id"]

    return {
        "val_prep_chem_1": {
            **val_prep_chem_1, ChemicalSchema.CHEM_ID_KEY: id_1
        },
        "val_prep_chem_2": {
            **val_prep_chem_2, ChemicalSchema.CHEM_ID_KEY: id_2
        }
    }

@pytest.fixture()
def val_purch_lots(val_purch_chems):
    # Returns two purchased lot objects
    val_purch_chem_milliq = copy.deepcopy(val_purch_chems["val_purch_chem_1"])
    val_purch_chem_h3po4 = copy.deepcopy(val_purch_chems["val_purch_chem_2"])
    
    val_purch_chem_milliq_id = val_purch_chem_milliq[ChemicalSchema.CHEM_ID_KEY]
    val_purch_chem_h3po4_id = val_purch_chem_h3po4[ChemicalSchema.CHEM_ID_KEY]

    # A future upgrade to add "Comments" fields would allow a user to note that
    # the "Manufacturer Lot" field correseponds to "Instrument S/N," that "Open Date"
    # corresponds to "Last PM Date,"" and that "Expiry Date" corresponds to "PM Due
    # Date." This could serve as a stop-gap way to document instrument information.
    val_purch_lot_1 = {
        LotSchema.PARENT_CHEM_ID_KEY: val_purch_chem_milliq_id,
        LotSchema.MANU_LOT_KEY: "124078GSJDLKGH98245-1254",
        LotSchema.OPEN_KEY: "2024-12-21T14:30:00-04:00",
        LotSchema.EXPIRY_KEY:"2025-12-21T23:59:59-04:00",
        LotSchema.EMPTY_KEY: None,
    }

    val_purch_lot_2 = {
        LotSchema.PARENT_CHEM_ID_KEY: val_purch_chem_h3po4_id,
        LotSchema.MANU_LOT_KEY: "00142J678F",
        LotSchema.OPEN_KEY: "2025-04-06T14:30:00-04:00",
        LotSchema.EXPIRY_KEY: "2028-04-06T14:30:00-04:00",
        LotSchema.EMPTY_KEY: None,
    }

    return {
        "val_purch_lot_1": val_purch_lot_1,
        "val_purch_lot_2": val_purch_lot_2
    }

@pytest.fixture()
def val_prep_lots(val_prep_chems):
    """
    The objects cannot be fully built in the fixture because a POST action is 
    required to retrieve the primary keys needed to link components to their
    existing lot records. Tests should first post val_purch_lot_1 and val_purch_lot_2.
    val_purch_lot_2's primary key will be used as the lot_id component in 
    val_prep_lot_1. At this point, val_prep_lot_1 should be posted. val_prep_lot_1
    and val_purch_lot_2's primary keys will be used as lot_ids in the components
    of val_prep_lot_2.

    val_prep_lot_1["Components"][0] corresponds to val_purch_lot_1
    val_prep_lot_2["Components"][0] corresponds to val_prep_lot 1
    val_prep_lot_2["Components"][1] corresponds to val_purch_lot 2
    """
    # Assign parent chemical IDs (PARENT_CHEM_ID) for the prepared lots themselves
    val_prep_chem_in_house_water = copy.deepcopy(val_prep_chems["val_prep_chem_1"])
    val_prep_chem_mpa = copy.deepcopy(val_prep_chems["val_prep_chem_2"])

    val_prep_chem_in_house_water_id = val_prep_chem_in_house_water[ChemicalSchema.CHEM_ID_KEY]
    val_prep_chem_mpa_id = val_prep_chem_mpa[ChemicalSchema.CHEM_ID_KEY]

    # Prepared lot using a purchased component
    # A future upgrade to add "Comments" fields would allow a user to note that
    # the "Amount" field is irrelevant since this lot is used to log any water
    # from the water dispenser.
    val_prep_lot_1 = {
        LotSchema.PARENT_CHEM_ID_KEY: val_prep_chem_in_house_water_id,
        LotSchema.AMT_KEY: 999999,
        LotSchema.UNIT_KEY: "N/A",
        LotSchema.CONT_TYPE_KEY: "Instrument",
        LotSchema.PREP_DATE_KEY: "2025-04-08T14:30:00-04:00",
        LotSchema.EXPIRY_KEY: "2025-05-08T14:30:00-04:00",
        LotSchema.EMPTY_KEY: None,
        LotSchema.COMPONENTS_KEY: [
            {
                LotSchema.COMP_LOT_KEY: None,   # MilliQ
                LotSchema.AMT_KEY: 999999,
                LotSchema.UNIT_KEY: "N/A"
            }
        ]
    }

    # Prepared lot using both purchased and prepared components
    val_prep_lot_2 = {
        LotSchema.PARENT_CHEM_ID_KEY: val_prep_chem_mpa_id,
        LotSchema.AMT_KEY: 4,
        LotSchema.UNIT_KEY: "L",
        LotSchema.CONT_TYPE_KEY: "Bottle",
        LotSchema.PREP_DATE_KEY: "2025-04-08T14:15:00-04:00",
        LotSchema.EXPIRY_KEY: "2025-05-08T14:15:00-04:00",
        LotSchema.EMPTY_KEY: None,
        LotSchema.COMPONENTS_KEY: [
            {
                LotSchema.COMP_LOT_KEY: None,    # Water, In-House
                LotSchema.AMT_KEY: 4000,
                LotSchema.UNIT_KEY: "mL"
            },
            {
                LotSchema.COMP_LOT_KEY: None,    # H3PO4
                LotSchema.AMT_KEY: 4,
                LotSchema.UNIT_KEY: "mL"
            }
        ]
    }

    return {
        "val_prep_lot_1": val_prep_lot_1,
        "val_prep_lot_2": val_prep_lot_2
    }

# Setting up lots is tedious given their referential nature. This isn't a fixture
# so as to avoid automatic posting of lots when running test_add_lot.py.
def post_all_lots(
    client,
    post_all_lists,
    val_purch_lots,
    val_prep_lots
):
    valid_purchased_lot_1 = val_purch_lots["val_purch_lot_1"]
    valid_purchased_lot_2 = val_purch_lots["val_purch_lot_2"]
    valid_prepared_lot_1 = val_prep_lots["val_prep_lot_1"]
    valid_prepared_lot_2 = val_prep_lots["val_prep_lot_2"]

    milliq_lot = copy.deepcopy(valid_purchased_lot_1)
    h3po4_lot = copy.deepcopy(valid_purchased_lot_2)
    house_water_lot = copy.deepcopy(valid_prepared_lot_1)
    mpa_lot = copy.deepcopy(valid_prepared_lot_2)

    # POST val_purch_lots in order to retrieve primary keys needed for components in val_prep_lots
    milliq_lot_resp = client.post(lots_address, json=milliq_lot)
    h3po4_lot_resp = client.post(lots_address, json=h3po4_lot)

    milliq_id = milliq_lot_resp.get_json()["inserted_id"]
    h3po4_id = h3po4_lot_resp.get_json()["inserted_id"]

    assert milliq_lot_resp.status_code == 201
    assert h3po4_lot_resp.status_code == 201

    get_milliq_resp = client.get(f"{lots_address}/{milliq_id}")
    get_h3po4_resp = client.get(f"{lots_address}/{h3po4_id}")

    milliq_data = get_milliq_resp.get_json()
    h3po4_data = get_h3po4_resp.get_json()

    # Add primary key for MilliQ to Water, In-House, POST Water, In-House, and
    # return primary key from Water, In-House to use in Mobile Phase A
    component = house_water_lot[LotSchema.COMPONENTS_KEY][0]
    component[LotSchema.COMP_LOT_KEY] = milliq_data[LotSchema.LOT_ID_KEY]

    post_house_water_resp = client.post(lots_address, json=house_water_lot)
    house_water_id = post_house_water_resp.get_json()["inserted_id"]
    
    assert post_house_water_resp.status_code == 201

    get_house_water_resp = client.get(f"{lots_address}/{house_water_id}")

    house_water_data = get_house_water_resp.get_json()

    # Add component primary keys in Mobile Phase A and POST Mobile Phase A
    house_water_component = mpa_lot[LotSchema.COMPONENTS_KEY][0]
    house_water_component[LotSchema.COMP_LOT_KEY] = house_water_data[LotSchema.LOT_ID_KEY]
    h3po4_component = mpa_lot[LotSchema.COMPONENTS_KEY][1]
    h3po4_component[LotSchema.COMP_LOT_KEY] = h3po4_data[LotSchema.LOT_ID_KEY]

    # POST Mobile Phase A and confirm success
    mpa_resp = client.post(lots_address, json=mpa_lot)

    mpa_id = mpa_resp.get_json()["inserted_id"]

    assert mpa_resp.status_code == 201

    return {
        "val_purch_lot_1": {
            **milliq_lot, LotSchema.LOT_ID_KEY: milliq_id
        },
        "val_purch_lot_2": {
            **h3po4_lot, LotSchema.LOT_ID_KEY: h3po4_id
        },
        "val_prep_lot_1": {
            **house_water_lot, LotSchema.LOT_ID_KEY: house_water_id
        },
        "val_prep_lot_2": {
            **mpa_lot, LotSchema.LOT_ID_KEY: mpa_id
        }
    }

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
    invalid_lots = [
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

    return invalid_lots