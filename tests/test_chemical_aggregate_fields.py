import copy, time
from datetime import datetime, timezone, timedelta
from tests.conftest import post_all_lots, flask_app
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
    
    purch_lot_1 = val_lots["val_purch_lot_1"]
    purch_lot_2 = val_lots["val_purch_lot_2"]
    prep_lot_1 = val_lots["val_prep_lot_1"]
    prep_lot_2 = val_lots["val_prep_lot_2"]

    purch_lot_1[LotSchema.OPEN_KEY] = None
    purch_lot_2[LotSchema.OPEN_KEY] = None

    unopen_resp_1 = client.put(f"{lots_address}/{purch_lot_1[LotSchema.LOT_ID_KEY]}", json=purch_lot_1)
    unopen_resp_2 = client.put(f"{lots_address}/{purch_lot_2[LotSchema.LOT_ID_KEY]}", json=purch_lot_2)

    assert unopen_resp_1.status_code == 200
    assert unopen_resp_2.status_code == 200

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
    
    purch_lot_3 = val_lots["val_purch_lot_1"]
    purch_lot_4 = val_lots["val_purch_lot_2"]
    prep_lot_3 = val_lots["val_prep_lot_1"]
    prep_lot_4 = val_lots["val_prep_lot_2"]

    purch_lot_3[LotSchema.OPEN_KEY] = None
    purch_lot_4[LotSchema.OPEN_KEY] = None

    unopen_resp_3 = client.put(f"{lots_address}/{purch_lot_3[LotSchema.LOT_ID_KEY]}", json=purch_lot_3)
    unopen_resp_4 = client.put(f"{lots_address}/{purch_lot_4[LotSchema.LOT_ID_KEY]}", json=purch_lot_4)

    assert unopen_resp_3.status_code == 200
    assert unopen_resp_4.status_code == 200
    
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

    open_resp_1 = client.put(f"{lots_address}/{purch_lot_1[LotSchema.LOT_ID_KEY]}", json=purch_lot_1)
    open_resp_2 = client.put(f"{lots_address}/{purch_lot_2[LotSchema.LOT_ID_KEY]}", json=purch_lot_2)
    open_resp_3 = client.put(f"{lots_address}/{purch_lot_3[LotSchema.LOT_ID_KEY]}", json=purch_lot_3)
    open_resp_4 = client.put(f"{lots_address}/{purch_lot_4[LotSchema.LOT_ID_KEY]}", json=purch_lot_4)

    assert open_resp_1.status_code == 200
    assert open_resp_2.status_code == 200
    assert open_resp_3.status_code == 200
    assert open_resp_4.status_code == 200
    
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

    empty_resp_1 = client.put(f"{lots_address}/{purch_lot_1[LotSchema.LOT_ID_KEY]}", json=purch_lot_1)
    empty_resp_2 = client.put(f"{lots_address}/{purch_lot_2[LotSchema.LOT_ID_KEY]}", json=purch_lot_2)
    empty_resp_3 = client.put(f"{lots_address}/{purch_lot_3[LotSchema.LOT_ID_KEY]}", json=purch_lot_3)
    empty_resp_4 = client.put(f"{lots_address}/{purch_lot_4[LotSchema.LOT_ID_KEY]}", json=purch_lot_4)
    empty_resp_5 = client.put(f"{lots_address}/{prep_lot_1[LotSchema.LOT_ID_KEY]}", json=prep_lot_1)
    empty_resp_6 = client.put(f"{lots_address}/{prep_lot_2[LotSchema.LOT_ID_KEY]}", json=prep_lot_2)
    empty_resp_7 = client.put(f"{lots_address}/{prep_lot_3[LotSchema.LOT_ID_KEY]}", json=prep_lot_3)
    empty_resp_8 = client.put(f"{lots_address}/{prep_lot_4[LotSchema.LOT_ID_KEY]}", json=prep_lot_4)

    assert empty_resp_1.status_code == 200
    assert empty_resp_2.status_code == 200
    assert empty_resp_3.status_code == 200
    assert empty_resp_4.status_code == 200
    assert empty_resp_5.status_code == 200
    assert empty_resp_6.status_code == 200
    assert empty_resp_7.status_code == 200
    assert empty_resp_8.status_code == 200

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

    unempty_resp_1 = client.put(f"{lots_address}/{purch_lot_1[LotSchema.LOT_ID_KEY]}", json=purch_lot_1)
    unempty_resp_2 = client.put(f"{lots_address}/{purch_lot_2[LotSchema.LOT_ID_KEY]}", json=purch_lot_2)
    unempty_resp_3 = client.put(f"{lots_address}/{purch_lot_3[LotSchema.LOT_ID_KEY]}", json=purch_lot_3)
    unempty_resp_4 = client.put(f"{lots_address}/{purch_lot_4[LotSchema.LOT_ID_KEY]}", json=purch_lot_4)
    unempty_resp_5 = client.put(f"{lots_address}/{prep_lot_1[LotSchema.LOT_ID_KEY]}", json=prep_lot_1)
    unempty_resp_6 = client.put(f"{lots_address}/{prep_lot_2[LotSchema.LOT_ID_KEY]}", json=prep_lot_2)
    unempty_resp_7 = client.put(f"{lots_address}/{prep_lot_3[LotSchema.LOT_ID_KEY]}", json=prep_lot_3)
    unempty_resp_8 = client.put(f"{lots_address}/{prep_lot_4[LotSchema.LOT_ID_KEY]}", json=prep_lot_4)

    assert unempty_resp_1.status_code == 200
    assert unempty_resp_2.status_code == 200
    assert unempty_resp_3.status_code == 200
    assert unempty_resp_4.status_code == 200
    assert unempty_resp_5.status_code == 200
    assert unempty_resp_6.status_code == 200
    assert unempty_resp_7.status_code == 200
    assert unempty_resp_8.status_code == 200

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

    expire_resp_1 = client.put(f"{lots_address}/{purch_lot_1[LotSchema.LOT_ID_KEY]}", json=purch_lot_1)
    expire_resp_2 = client.put(f"{lots_address}/{purch_lot_2[LotSchema.LOT_ID_KEY]}", json=purch_lot_2)
    expire_resp_3 = client.put(f"{lots_address}/{purch_lot_3[LotSchema.LOT_ID_KEY]}", json=purch_lot_3)
    expire_resp_4 = client.put(f"{lots_address}/{purch_lot_4[LotSchema.LOT_ID_KEY]}", json=purch_lot_4)
    expire_resp_5 = client.put(f"{lots_address}/{prep_lot_1[LotSchema.LOT_ID_KEY]}", json=prep_lot_1)
    expire_resp_6 = client.put(f"{lots_address}/{prep_lot_2[LotSchema.LOT_ID_KEY]}", json=prep_lot_2)
    expire_resp_7 = client.put(f"{lots_address}/{prep_lot_3[LotSchema.LOT_ID_KEY]}", json=prep_lot_3)
    expire_resp_8 = client.put(f"{lots_address}/{prep_lot_4[LotSchema.LOT_ID_KEY]}", json=prep_lot_4)

    assert expire_resp_1.status_code == 200
    assert expire_resp_2.status_code == 200
    assert expire_resp_3.status_code == 200
    assert expire_resp_4.status_code == 200
    assert expire_resp_5.status_code == 200
    assert expire_resp_6.status_code == 200
    assert expire_resp_7.status_code == 200
    assert expire_resp_8.status_code == 200

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


# The test can be killed from here down for use as a start-up check to avoid the wait time.
# This is technically redundant given the manual expiration of ltos above, but I wanted to see
# it happen in real-time organically during testing.
#***********************************************************************************************# 
#"""

    # Un-expire all lots
    now_local = datetime.now(timezone.utc).astimezone()
    now_local_plus_10_sec = now_local + timedelta(seconds=10)
    now_local_plus_10_sec_iso = now_local_plus_10_sec.isoformat()
    purch_lot_1[LotSchema.EXPIRY_KEY] = str(now_local_plus_10_sec_iso)
    purch_lot_2[LotSchema.EXPIRY_KEY] = str(now_local_plus_10_sec_iso)
    purch_lot_3[LotSchema.EXPIRY_KEY] = str(now_local_plus_10_sec_iso)
    purch_lot_4[LotSchema.EXPIRY_KEY] = str(now_local_plus_10_sec_iso)
    prep_lot_1[LotSchema.EXPIRY_KEY] = str(now_local_plus_10_sec_iso)
    prep_lot_2[LotSchema.EXPIRY_KEY] = str(now_local_plus_10_sec_iso)
    prep_lot_3[LotSchema.EXPIRY_KEY] = str(now_local_plus_10_sec_iso)
    prep_lot_4[LotSchema.EXPIRY_KEY] = str(now_local_plus_10_sec_iso)

    unexpire_resp_1 = client.put(f"{lots_address}/{purch_lot_1[LotSchema.LOT_ID_KEY]}", json=purch_lot_1)
    unexpire_resp_2 = client.put(f"{lots_address}/{purch_lot_2[LotSchema.LOT_ID_KEY]}", json=purch_lot_2)
    unexpire_resp_3 = client.put(f"{lots_address}/{purch_lot_3[LotSchema.LOT_ID_KEY]}", json=purch_lot_3)
    unexpire_resp_4 = client.put(f"{lots_address}/{purch_lot_4[LotSchema.LOT_ID_KEY]}", json=purch_lot_4)
    unexpire_resp_5 = client.put(f"{lots_address}/{prep_lot_1[LotSchema.LOT_ID_KEY]}", json=prep_lot_1)
    unexpire_resp_6 = client.put(f"{lots_address}/{prep_lot_2[LotSchema.LOT_ID_KEY]}", json=prep_lot_2)
    unexpire_resp_7 = client.put(f"{lots_address}/{prep_lot_3[LotSchema.LOT_ID_KEY]}", json=prep_lot_3)
    unexpire_resp_8 = client.put(f"{lots_address}/{prep_lot_4[LotSchema.LOT_ID_KEY]}", json=prep_lot_4)
    
    assert unexpire_resp_1.status_code == 200
    assert unexpire_resp_2.status_code == 200
    assert unexpire_resp_3.status_code == 200
    assert unexpire_resp_4.status_code == 200
    assert unexpire_resp_5.status_code == 200
    assert unexpire_resp_6.status_code == 200
    assert unexpire_resp_7.status_code == 200
    assert unexpire_resp_8.status_code == 200

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

    # Wait a few seconds to verify that expiry datetimes have passed
    time.sleep(11)

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

#"""