"""
For a detailed account of lot and chemical testing, please see docstrings for tests/chemicals/conftest.py and
tests/lots/conftest.py

The aggregate fields "Available_Total" and "Available_Open" in the chemicals schema depend on the presence of lot records.
As such, their testing neither quite fits neatly into the chemicals/ nor the lots/ test groups.

# Chemical Total_Available and Total_Open field behaviour:
* Chemical aggregate fields are initialized to int(0) upon chemical template creation.
* Chemical aggregate fields will change as a result of lots being open, emptied, or their expiry date passing.
* Chemical aggregate fields are recalculated when a PUT or GET request is submitted for a chemical(s).
* Chemical aggregate fields are recalculated for a chemical template when lots are created or updated.
* Chemical aggregate fields are NOT recalculated when lots are deleted. Though the system currently supports lot deletion,
it is marked for an upgrade to remove the ability to delete lots (or anything, for that matter). A very high-level
user may need access to truly delete records, but the system should isntead have "Removed" field flags for all objects,
and "deleting" an object should merely set the "Removed" flaag to "True".
    * This would be considered a critical issue if this system were live.
* Chemical aggregate fields are technically updates when a chemical template receives a PUT request, but this is obfuscated by the
fact that chemical aggregate fields are updated when a GET request is received for the template.
"""

import sys
import os

# Had to explicitly add root to sys.path for pytest to find the Flask app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest, copy, mongomock

from app import create_app
from app.models.lists import ListsSchema
from app.models.chemicals import ChemicalSchema
from app.models.lots import LotSchema

chemicals_address = "/chemicals"
lots_address = "/lots"
lists_address = "/lists"

@pytest.fixture()
def app():
    flask_app = create_app()
    flask_app.config.update({
        "TESTING": True
    })

    flask_app.mongo_client = mongomock.MongoClient()
    flask_app.db = flask_app.mongo_client.conquest_lims
    flask_app.lists = flask_app.db.lists
    flask_app.chemicals = flask_app.db.chemicals
    flask_app.lots = flask_app.db.lots
    
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
def valid_purchased_chemical_4():
    valid_purchased_chemical_4 = {
        ChemicalSchema.NAME_KEY: "Milli-Q IQ 7000 Ultrapure Water Purification System",
        ChemicalSchema.CAS_KEY: "7732-18-5",
        ChemicalSchema.CLASSIF_KEY: "Water Dispenser",
        ChemicalSchema.STORAGE_KEY: "Ambient",
        ChemicalSchema.SOURCE_KEY: "Purchased",
        ChemicalSchema.PURCH_FIELD_KEY: {
            ChemicalSchema.MANU_KEY: "Milli-Q",
            ChemicalSchema.MANU_PN_KEY: "ZIQ7000T0C",
            ChemicalSchema.AMT_KEY: 99999,
            ChemicalSchema.UNIT_KEY: "N/A",
            ChemicalSchema.CONT_TYPE_KEY: "Instrument"
        }
    }

    return valid_purchased_chemical_4

@pytest.fixture()
def val_purch_chems(
    client,
    post_all_lists,
    valid_purchased_chemical_3,
    valid_purchased_chemical_4
):
    """
    valid_purchased_chemical_<1-4> build objects available for chemicals testing. 
    This method posts them for lots testing. Only the last two objects are needed.
    """
    val_purch_chem_1 = valid_purchased_chemical_4
    val_purch_chem_2 = valid_purchased_chemical_3

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
def valid_prepared_chemical_1():
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
def valid_prepared_chemical_3():
    # Prepared chemical using only purchased components
    valid_prepared_chemical_3 = {
        ChemicalSchema.NAME_KEY: "Water, in-house",
        ChemicalSchema.CAS_KEY: "7732-18-5",
        ChemicalSchema.CLASSIF_KEY: "Water",
        ChemicalSchema.STORAGE_KEY: "Ambient",
        ChemicalSchema.SOURCE_KEY: "Prepared",
        ChemicalSchema.PREP_FIELD_KEY: {
            ChemicalSchema.METH_REF_KEY: "N/A"
            }
    }

    return valid_prepared_chemical_3

@pytest.fixture()
def val_prep_chems(
    client,
    post_all_lists,
    valid_prepared_chemical_1,
    valid_prepared_chemical_3
):
    """
    valid_prepared_chemical_1, valid_prepared_chemical_2, and valid_prepared_chemical_3 build objects available
    for chemicals testing. This method posts them for lots testing. Only the first and last objects are needed.
    """
    val_prep_chem_1 = valid_prepared_chemical_3
    val_prep_chem_2 = valid_prepared_chemical_1

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
        LotSchema.EXPIRY_KEY: "2025-12-21T23:59:59-04:00",
        LotSchema.EMPTY_KEY: None
    }

    val_purch_lot_2 = {
        LotSchema.PARENT_CHEM_ID_KEY: val_purch_chem_h3po4_id,
        LotSchema.MANU_LOT_KEY: "00142J678F",
        LotSchema.OPEN_KEY: "2025-04-06T14:30:00-04:00",
        LotSchema.EXPIRY_KEY: "2028-04-06T14:30:00-04:00",
        LotSchema.EMPTY_KEY: None
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
