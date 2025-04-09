import copy
from chemical_inventory_api_v1 import LotSchema
from tests.lots.conftest import post_all_lots

# Variable names for Water, In-House are verbose to avoid potential future conflict
# with purchased water reagents used in other tests.

lots_address = "/lots"

def test_get_all_lots(
    client,
    post_all_lists,
    val_purch_lots,
    val_prep_lots
):
    post_all_lots(client, post_all_lists, val_purch_lots, val_prep_lots)

    get_resp_1 = client.get(lots_address)

    assert get_resp_1.status_code == 200