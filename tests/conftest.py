"""
# Notes on Testing "/chemicals"

## Chemical Choice
* Mobile Phase B: A prepared chemical using three purchased chemicals
as components. These three chemicals are sufficient to test the system
as it is currently able to function
* Mobile Phase A: A prepared chemical using one purchased chemical and
one prepared chemical (Water, in-house) as components. This chemical will
be added to testing when the system supports the use of prepared lots
as components in another prepared lot. "/chemicals" testing is unaffected
by this but "/lots" end pointsare affected. **Do not attempt to create a lot
using another prepared lot.**

## Valid Chemical Configurations
Chemical requests can arrive in one of four configurations:

* Purchased materials
* Prepared materials with components that are purchased materials
* Prepared materials with components that are other prepared materials
* Prepared materials with components that are a mix of purchased and
prepared materials

The system is not currently configured to allow prepared materials to use
other prepared materials as components. This is marked for a future update.
In the mean time, these tests only builds a prepared chemical intended to use
exclusively purchased chemicals as components. A chemical meant to use
prepared reagents (e.g. an in-house water component) will be added to the
test suite after the system is changed to allow this. "All valid 
configurations" is currently taken to mean either purchased chemicals or
chemicals that use only purchased materials as components.

## Tests

### HTTP code 200:
* The tests verify that chemical objects of all valid configurations are
successfully modified in the database.

### HTTP code 400:
* The test confirms that missing request bodies return error code 400.
* The test confirms that malformed primary keys return error code 400.

### HTTP code 422:
All fields in the chemical document, the primary key (if applicable), and
the nature of the request itself are tested individually to verify that the
system properly validates all applicable error codes:

* No required keys are missing from chemical requests.
* No required values are left empty in chemical requests.
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
* The system is tested to ensure it removes aggregate fields from incoming requests.

"""

import sys
import os

# Had to explicitly add root to sys.path for pytest to find the Flask app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest, copy, mongomock
from flask import Flask
from pymongo import MongoClient
from chemical_inventory_api_v1 import ChemicalSchema, ListsSchema, ValidationErrorCodes
from chemical_inventory_api_v1 import app as flask_app

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

@pytest.fixture
def post_all_lists(client):
    lists_address = "/lists"
    
    # Validated lists
    classifications = {f"{ListsSchema.LIST_NAME_KEY}": ListsSchema.CLASSIF_LIST_KEY(), f"{ListsSchema.LIST_ENT_KEY}": ["Flammable solvent", "Strong acid", "Weak acid", "Strong base", "Weak base", "Mobile phase", "Reagent", "Standard", "Solid", "Dewer", "Gas cylinder", "Water"]}
    container_types = {f"{ListsSchema.LIST_NAME_KEY}": ListsSchema.CONT_TYPES_LIST_KEY(), f"{ListsSchema.LIST_ENT_KEY}": ["Ampoule", "Autosampler vial", "Bottle", "Vial"]}
    manufacturers = {f"{ListsSchema.LIST_NAME_KEY}": ListsSchema.MANU_LIST_KEY(), f"{ListsSchema.LIST_ENT_KEY}": ["3M", "Agilent", "Alfa Aesar", "Eppendorf", "Fisher Scientific", "Honeywell", "J.T. Baker", "Sigma-Aldrich", "Thermo Fisher Scientific", "VWR"]}
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


@pytest.fixture()
def valid_purchased_chemical_1():
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

    return valid_purchased_chemical_1

@pytest.fixture()
def valid_purchased_chemical_2():
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

    return valid_purchased_chemical_2

@pytest.fixture()
def valid_purchased_chemical_3():
    # Save this in lots but remove from chemicals conftest.py after lots has a conftest.py with it

    valid_purchased_chemical_3 = {
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

    return valid_purchased_chemical_3

@pytest.fixture()
def valid_prepared_chemical_1():
    """
    This chemical is suitable fot testing the /chemicals end poitns. It should not be
    used to test /lots end points until the system is reconfigured to allow the use of
    prepared lots as components in other prepared lots.
    """
    valid_prepared_chemical_1 = {
        ChemicalSchema.NAME_KEY: "Mobile Phase A: Water, 0.1 % Phosphoric Acid",
        ChemicalSchema.CAS_KEY: "7732-18-5, 7664-38-2",
        ChemicalSchema.CLASSIF_KEY: "Mobile phase",
        ChemicalSchema.STORAGE_KEY: "Ambient",
        ChemicalSchema.SOURCE_KEY: "Prepared",
        ChemicalSchema.PREP_FIELD_KEY: {
            ChemicalSchema.METH_REF_KEY: "SOP-00123.4.3.i"
            }
    }

    return valid_prepared_chemical_1

@pytest.fixture()
def valid_prepared_chemical_2():
    # Prepared chemical using only purchased components
    valid_prepared_chemical_2 = {
        ChemicalSchema.NAME_KEY: "Mobile Phase B: 40% Methanol in Water, 0.1 % Phosphoric Acid",
        ChemicalSchema.CAS_KEY: "67-56-1, 7732-18-5",
        ChemicalSchema.CLASSIF_KEY: "Mobile phase",
        ChemicalSchema.STORAGE_KEY: "Ambient",
        ChemicalSchema.SOURCE_KEY: "Prepared",
        ChemicalSchema.PREP_FIELD_KEY: {
            ChemicalSchema.METH_REF_KEY: "SOP-00123.4.3.ii"
            }
    }

    return valid_prepared_chemical_2

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
def valid_prepared_lot_prep_comps():
    """
    This object will be configured as a lot of a prepared chemical that itself uses
    a prepared chemical in one of its lot components for testing after a future
    upgrade to allow that configuration.
    
    When that feature is implemented this reagent would use "Water, in-house," itself
    a prepared reagent requiring a custom chemical record to document the in-house
    water system, as a source. No logic currently exists to support this schema.
    """