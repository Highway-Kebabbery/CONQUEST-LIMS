"""
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
        * (It's not live; it's a portfolio piece that I'm burned out on after 11 days of LITERAL dawn-to-dusk effort.)
* Chemical aggregate fields are technically updates when a chemical template receives a PUT request, but this is obfuscated by the
fact that chemical aggregate fields are updated when a GET request is received for the template.




# Test design:
* ***************************************Post all cehmical templates and store objects and primary keys.
* *******************************************************************Check aggregate data on chemical templates. Total/Open should be 0/0 for purchased lots and 1/1 for prepared lots.
* *********************************************************************Run post_all_lots() and store objects and primary keys.
* ***********************************************************************Check aggregate data on chemical templates again. Total/Open should be 2/0 for purchased lots and 2/2 for prepared lots.
* ************************************************Update purchased lots to give them an open date.
* ***************************************Check aggregate data on chemical templates again. Total/Open should be 2/2 for purchased lots and 2/2 for prepared lots.
* ****************************************Update all lots to have an empty date.
* ***************************************************Check aggregate data on chemical templates again. Total/Open should be 0/0 for purchased lots and 0/0 for prepared lots.
* ***************************************Update all lots to have no empty date.
* ****************************************************Check aggregate data on chemical templates again. Total/Open should be 2/2 for purchased lots and 2/2 for prepared lots.
* *************************************************************Update all lots to have a passed expiry date.
* Check aggregate data on chemical templates again. Total/Open should be 0/0 for purchased lots and 0/0 for prepared lots.
* If possible, set all lots to have expiry dates 15 seconds from now and update them.
* Check aggregate data on chemical templates again. Total/Open should be 2/2 for purchased lots and 2/2 for prepared lots.
* After waiting for 15 seconds, check aggregate data on chemical templates again. Total/Open should be 0/0 for purchased lots and 0/0 for prepared lots.
"""
import copy
from tests.conftest import post_all_lots
from chemical_inventory_api_v1 import ChemicalSchema, LotSchema

chemicals_address = "/chemicals"
lots_address = "/lots"

def test_aggregate_chemical_fields(
    client,
    post_all_lists,
    val_purch_chems,
    val_prep_chems,
    val_purch_lots,
    val_prep_lots,
):
    # Create references to chemical objects and primary keys
    purch_chem_1 = copy.deepcopy(val_purch_chems["val_purch_chem_1"])
    purch_chem_2 = copy.deepcopy(val_purch_chems["val_purch_chem_2"])
    prep_chem_1 = copy.deepcopy(val_prep_chems["val_prep_chem_1"])
    prep_chem_2 = copy.deepcopy(val_prep_chems["val_prep_chem_2"])

    purch_chem_1_id = purch_chem_1[ChemicalSchema.CHEM_ID_KEY]
    purch_chem_2_id = purch_chem_2[ChemicalSchema.CHEM_ID_KEY]
    prep_chem_1_id = prep_chem_1[ChemicalSchema.CHEM_ID_KEY]
    prep_chem_2_id = prep_chem_2[ChemicalSchema.CHEM_ID_KEY]

    # Verify that aggregate fields are initialized to int(0)
    purch_chem_1_resp = client.get(f"{chemicals_address}/{purch_chem_1_id}")
    purch_chem_2_resp = client.get(f"{chemicals_address}/{purch_chem_2_id}")
    prep_chem_1_resp = client.get(f"{chemicals_address}/{prep_chem_1_id}")
    prep_chem_2_resp = client.get(f"{chemicals_address}/{prep_chem_2_id}")

    purch_data_1 = purch_chem_1_resp.get_json()
    purch_data_2 = purch_chem_2_resp.get_json()
    prep_data_1 = prep_chem_1_resp.get_json()
    prep_data_2 = prep_chem_2_resp.get_json()

    assert purch_data_1[ChemicalSchema.AVAIL_TOTAL_KEY] == 0
    assert purch_data_1[ChemicalSchema.AVAIL_OPEN_KEY] == 0
    assert purch_data_2[ChemicalSchema.AVAIL_TOTAL_KEY] == 0
    assert purch_data_2[ChemicalSchema.AVAIL_OPEN_KEY] == 0
    assert prep_data_1[ChemicalSchema.AVAIL_TOTAL_KEY] == 0
    assert prep_data_1[ChemicalSchema.AVAIL_OPEN_KEY] == 0
    assert prep_data_2[ChemicalSchema.AVAIL_TOTAL_KEY] == 0
    assert prep_data_2[ChemicalSchema.AVAIL_OPEN_KEY] == 0

    # Post lots; create references to objects and primary keys; close lots (re-using fixtures from another test)
    val_lots = post_all_lots(
        client,
        post_all_lists,
        val_purch_lots,
        val_prep_lots
    )
    
    purch_lot_1 = val_lots[0]
    purch_lot_2 = val_lots[1]
    prep_lot_1 = val_lots[2]
    prep_lot_2 = val_lots[3]

    purch_lot_1[LotSchema.OPEN_KEY] = None
    purch_lot_2[LotSchema.OPEN_KEY] = None

    # Verify that aggregate fields were updated
    purch_chem_1_resp = client.get(f"{chemicals_address}/{purch_chem_1_id}")
    purch_chem_2_resp = client.get(f"{chemicals_address}/{purch_chem_2_id}")
    prep_chem_1_resp = client.get(f"{chemicals_address}/{prep_chem_1_id}")
    prep_chem_2_resp = client.get(f"{chemicals_address}/{prep_chem_2_id}")

    purch_data_1 = purch_chem_1_resp.get_json()
    purch_data_2 = purch_chem_2_resp.get_json()
    prep_data_1 = prep_chem_1_resp.get_json()
    prep_data_2 = prep_chem_2_resp.get_json()

    assert purch_data_1[ChemicalSchema.AVAIL_TOTAL_KEY] == 1
    assert purch_data_1[ChemicalSchema.AVAIL_OPEN_KEY] == 0
    assert purch_data_2[ChemicalSchema.AVAIL_TOTAL_KEY] == 1
    assert purch_data_2[ChemicalSchema.AVAIL_OPEN_KEY] == 0
    assert prep_data_1[ChemicalSchema.AVAIL_TOTAL_KEY] == 1
    assert prep_data_1[ChemicalSchema.AVAIL_OPEN_KEY] == 1
    assert prep_data_2[ChemicalSchema.AVAIL_TOTAL_KEY] == 1
    assert prep_data_2[ChemicalSchema.AVAIL_OPEN_KEY] == 1

    # Post lots again; create references to objects and primary keys; close lots (re-using fixtures from another test)
    val_lots = post_all_lots(
        client,
        post_all_lists,
        val_purch_lots,
        val_prep_lots
    )
    
    purch_lot_3 = val_lots[0]
    purch_lot_4 = val_lots[1]
    prep_lot_3 = val_lots[2]
    prep_lot_4 = val_lots[3]

    purch_lot_3[LotSchema.OPEN_KEY] = None
    purch_lot_4[LotSchema.OPEN_KEY] = None

    # Verify that aggregate fields were updated
    purch_chem_1_resp = client.get(f"{chemicals_address}/{purch_chem_1_id}")
    purch_chem_2_resp = client.get(f"{chemicals_address}/{purch_chem_2_id}")
    prep_chem_1_resp = client.get(f"{chemicals_address}/{prep_chem_1_id}")
    prep_chem_2_resp = client.get(f"{chemicals_address}/{prep_chem_2_id}")

    purch_data_1 = purch_chem_1_resp.get_json()
    purch_data_2 = purch_chem_2_resp.get_json()
    prep_data_1 = prep_chem_1_resp.get_json()
    prep_data_2 = prep_chem_2_resp.get_json()

    assert purch_data_1[ChemicalSchema.AVAIL_TOTAL_KEY] == 2
    assert purch_data_1[ChemicalSchema.AVAIL_OPEN_KEY] == 0
    assert purch_data_2[ChemicalSchema.AVAIL_TOTAL_KEY] == 2
    assert purch_data_2[ChemicalSchema.AVAIL_OPEN_KEY] == 0
    assert prep_data_1[ChemicalSchema.AVAIL_TOTAL_KEY] == 2
    assert prep_data_1[ChemicalSchema.AVAIL_OPEN_KEY] == 2
    assert prep_data_2[ChemicalSchema.AVAIL_TOTAL_KEY] == 2
    assert prep_data_2[ChemicalSchema.AVAIL_OPEN_KEY] == 2

    # Open purchased lots
    purch_lot_1[LotSchema.OPEN_KEY] = "2024-12-21T14:30:00-04:00"
    purch_lot_2[LotSchema.OPEN_KEY] = "2024-12-21T14:30:00-04:00"
    purch_lot_3[LotSchema.OPEN_KEY] = "2024-12-21T14:30:00-04:00"
    purch_lot_4[LotSchema.OPEN_KEY] = "2024-12-21T14:30:00-04:00"

    # Verify that aggregate fields were updated
    purch_chem_1_resp = client.get(f"{chemicals_address}/{purch_chem_1_id}")
    purch_chem_2_resp = client.get(f"{chemicals_address}/{purch_chem_2_id}")

    purch_data_1 = purch_chem_1_resp.get_json()
    purch_data_2 = purch_chem_2_resp.get_json()

    assert purch_data_1[ChemicalSchema.AVAIL_TOTAL_KEY] == 2
    assert purch_data_1[ChemicalSchema.AVAIL_OPEN_KEY] == 2
    assert purch_data_2[ChemicalSchema.AVAIL_TOTAL_KEY] == 2
    assert purch_data_2[ChemicalSchema.AVAIL_OPEN_KEY] == 2

    # Empty all lots
    purch_lot_1[LotSchema.EMPTY_KEY] = "2024-12-22T14:30:00-04:00"
    purch_lot_2[LotSchema.EMPTY_KEY] = "2024-12-22T14:30:00-04:00"
    purch_lot_3[LotSchema.EMPTY_KEY] = "2024-12-22T14:30:00-04:00"
    purch_lot_4[LotSchema.EMPTY_KEY] = "2024-12-22T14:30:00-04:00"
    prep_lot_1[LotSchema.EMPTY_KEY] = "2024-12-22T14:30:00-04:00"
    prep_lot_2[LotSchema.EMPTY_KEY] = "2024-12-22T14:30:00-04:00"
    prep_lot_3[LotSchema.EMPTY_KEY] = "2024-12-22T14:30:00-04:00"
    prep_lot_4[LotSchema.EMPTY_KEY] = "2024-12-22T14:30:00-04:00"

    # Verify that aggregate fields were updated
    purch_chem_1_resp = client.get(f"{chemicals_address}/{purch_chem_1_id}")
    purch_chem_2_resp = client.get(f"{chemicals_address}/{purch_chem_2_id}")
    prep_chem_1_resp = client.get(f"{chemicals_address}/{prep_chem_1_id}")
    prep_chem_2_resp = client.get(f"{chemicals_address}/{prep_chem_2_id}")

    purch_data_1 = purch_chem_1_resp.get_json()
    purch_data_2 = purch_chem_2_resp.get_json()
    prep_data_1 = prep_chem_1_resp.get_json()
    prep_data_2 = prep_chem_2_resp.get_json()

    assert purch_data_1[ChemicalSchema.AVAIL_TOTAL_KEY] == 0
    assert purch_data_1[ChemicalSchema.AVAIL_OPEN_KEY] == 0
    assert purch_data_2[ChemicalSchema.AVAIL_TOTAL_KEY] == 0
    assert purch_data_2[ChemicalSchema.AVAIL_OPEN_KEY] == 0
    assert prep_data_1[ChemicalSchema.AVAIL_TOTAL_KEY] == 0
    assert prep_data_1[ChemicalSchema.AVAIL_OPEN_KEY] == 0
    assert prep_data_2[ChemicalSchema.AVAIL_TOTAL_KEY] == 0
    assert prep_data_2[ChemicalSchema.AVAIL_OPEN_KEY] == 0

    # Remove empty date
    purch_lot_1[LotSchema.EMPTY_KEY] = None
    purch_lot_2[LotSchema.EMPTY_KEY] = None
    purch_lot_3[LotSchema.EMPTY_KEY] = None
    purch_lot_4[LotSchema.EMPTY_KEY] = None
    prep_lot_1[LotSchema.EMPTY_KEY] = None
    prep_lot_2[LotSchema.EMPTY_KEY] = None
    prep_lot_3[LotSchema.EMPTY_KEY] = None
    prep_lot_4[LotSchema.EMPTY_KEY] = None

    # Verify that aggregate fields were updated
    purch_chem_1_resp = client.get(f"{chemicals_address}/{purch_chem_1_id}")
    purch_chem_2_resp = client.get(f"{chemicals_address}/{purch_chem_2_id}")
    prep_chem_1_resp = client.get(f"{chemicals_address}/{prep_chem_1_id}")
    prep_chem_2_resp = client.get(f"{chemicals_address}/{prep_chem_2_id}")

    purch_data_1 = purch_chem_1_resp.get_json()
    purch_data_2 = purch_chem_2_resp.get_json()
    prep_data_1 = prep_chem_1_resp.get_json()
    prep_data_2 = prep_chem_2_resp.get_json()

    assert purch_data_1[ChemicalSchema.AVAIL_TOTAL_KEY] == 2
    assert purch_data_1[ChemicalSchema.AVAIL_OPEN_KEY] == 2
    assert purch_data_2[ChemicalSchema.AVAIL_TOTAL_KEY] == 2
    assert purch_data_2[ChemicalSchema.AVAIL_OPEN_KEY] == 2
    assert prep_data_1[ChemicalSchema.AVAIL_TOTAL_KEY] == 2
    assert prep_data_1[ChemicalSchema.AVAIL_OPEN_KEY] == 2
    assert prep_data_2[ChemicalSchema.AVAIL_TOTAL_KEY] == 2
    assert prep_data_2[ChemicalSchema.AVAIL_OPEN_KEY] == 2

    # Expire all lots
    purch_lot_1[LotSchema.EXPIRY_KEY] = "2024-12-22T14:30:00-04:00"
    purch_lot_2[LotSchema.EXPIRY_KEY] = "2024-12-22T14:30:00-04:00"
    purch_lot_3[LotSchema.EXPIRY_KEY] = "2024-12-22T14:30:00-04:00"
    purch_lot_4[LotSchema.EXPIRY_KEY] = "2024-12-22T14:30:00-04:00"
    prep_lot_1[LotSchema.EXPIRY_KEY] = "2024-12-22T14:30:00-04:00"
    prep_lot_2[LotSchema.EXPIRY_KEY] = "2024-12-22T14:30:00-04:00"
    prep_lot_3[LotSchema.EXPIRY_KEY] = "2024-12-22T14:30:00-04:00"
    prep_lot_4[LotSchema.EXPIRY_KEY] = "2024-12-22T14:30:00-04:00"

    # Verify that aggregate fields were updated
    purch_chem_1_resp = client.get(f"{chemicals_address}/{purch_chem_1_id}")
    purch_chem_2_resp = client.get(f"{chemicals_address}/{purch_chem_2_id}")
    prep_chem_1_resp = client.get(f"{chemicals_address}/{prep_chem_1_id}")
    prep_chem_2_resp = client.get(f"{chemicals_address}/{prep_chem_2_id}")

    purch_data_1 = purch_chem_1_resp.get_json()
    purch_data_2 = purch_chem_2_resp.get_json()
    prep_data_1 = prep_chem_1_resp.get_json()
    prep_data_2 = prep_chem_2_resp.get_json()

    assert purch_data_1[ChemicalSchema.AVAIL_TOTAL_KEY] == 0
    assert purch_data_1[ChemicalSchema.AVAIL_OPEN_KEY] == 0
    assert purch_data_2[ChemicalSchema.AVAIL_TOTAL_KEY] == 0
    assert purch_data_2[ChemicalSchema.AVAIL_OPEN_KEY] == 0
    assert prep_data_1[ChemicalSchema.AVAIL_TOTAL_KEY] == 0
    assert prep_data_1[ChemicalSchema.AVAIL_OPEN_KEY] == 0
    assert prep_data_2[ChemicalSchema.AVAIL_TOTAL_KEY] == 0
    assert prep_data_2[ChemicalSchema.AVAIL_OPEN_KEY] == 0