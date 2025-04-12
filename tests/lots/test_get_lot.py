from app.models.lots import LotSchema
from tests.lots.conftest import post_all_lots

# Variable names for Water, In-House are verbose to avoid potential future conflict
# with purchased water reagents used in other tests.

lots_address = "/lots"

def test_get_lot(
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

    # GET lots created in post_all_lots fixture
    get_resp_1 = client.get(f"{lots_address}/{milliq_id}")
    get_resp_2 = client.get(f"{lots_address}/{h3po4_id}")
    get_resp_3 = client.get(f"{lots_address}/{house_water_id}")
    get_resp_4 = client.get(f"{lots_address}/{mpa_id}")

    assert get_resp_1.status_code == 200
    assert get_resp_2.status_code == 200
    assert get_resp_3.status_code == 200
    assert get_resp_4.status_code == 200

    # Remove lots and confirm success
    del_resp_1 = client.delete(f"{lots_address}/{milliq_id}")
    del_resp_2 = client.delete(f"{lots_address}/{h3po4_id}")
    del_resp_3 = client.delete(f"{lots_address}/{house_water_id}")
    del_resp_4 = client.delete(f"{lots_address}/{mpa_id}")

    assert del_resp_1.status_code == 204
    assert del_resp_2.status_code == 204
    assert del_resp_3.status_code == 204
    assert del_resp_4.status_code == 204

    # Confirm GET requests for missing lots return 404

    get_resp_1 = client.get(f"{lots_address}/{milliq_id}")
    get_resp_2 = client.get(f"{lots_address}/{h3po4_id}")
    get_resp_3 = client.get(f"{lots_address}/{house_water_id}")
    get_resp_4 = client.get(f"{lots_address}/{mpa_id}")

    assert get_resp_1.status_code == 404
    assert get_resp_2.status_code == 404
    assert get_resp_3.status_code == 404
    assert get_resp_4.status_code == 404

    # Confirm that GET requests with malformed ObjectId return 400
    invalid_id_response_1 = client.get(f"{lots_address}/1")

    assert invalid_id_response_1.status_code == 400