import pytest, copy
from chemical_inventory_api_v1 import LotSchema
from tests.lots.conftest import post_all_lots

# Variable names for Water, In-House are verbose to avoid potential future conflict
# with purchased water reagents used in other tests.

lots_address = "/lots"

def test_delete_lot(
    client,
    post_all_lists,
    val_purch_lots,
    val_prep_lots
):
    val_lots = post_all_lots(client, post_all_lists, val_purch_lots, val_prep_lots)

    milliq_id = val_lots["val_purch_lot_1"][LotSchema.LOT_ID_KEY]
    h3po4_id = val_lots["val_purch_lot_2"][LotSchema.LOT_ID_KEY]
    house_water_id = val_lots["val_prep_lot_1"][LotSchema.LOT_ID_KEY]
    mpa_id = val_lots["val_prep_lot_2"][LotSchema.LOT_ID_KEY]

    # Remove lots and confirm success
    del_resp_1 = client.delete(f"{lots_address}/{milliq_id}")
    del_resp_2 = client.delete(f"{lots_address}/{h3po4_id}")
    del_resp_3 = client.delete(f"{lots_address}/{house_water_id}")
    del_resp_4 = client.delete(f"{lots_address}/{mpa_id}")

    assert del_resp_1.status_code == 204
    assert del_resp_2.status_code == 204
    assert del_resp_3.status_code == 204
    assert del_resp_4.status_code == 204

    # Confirm DELETE requests for missing lots return 404

    delete_resp_1 = client.delete(f"{lots_address}/{milliq_id}")
    delete_resp_2 = client.delete(f"{lots_address}/{h3po4_id}")
    delete_resp_3 = client.delete(f"{lots_address}/{house_water_id}")
    delete_resp_4 = client.delete(f"{lots_address}/{mpa_id}")

    assert delete_resp_1.status_code == 404
    assert delete_resp_2.status_code == 404
    assert delete_resp_3.status_code == 404
    assert delete_resp_4.status_code == 404

    # Confirm that GET requests with malformed ObjectId return 400
    invalid_id_response_1 = client.delete(f"{lots_address}/1")

    assert invalid_id_response_1.status_code == 400