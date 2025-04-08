import pytest, copy
from chemical_inventory_api_v1 import LotSchema

# Variable names for Water, In-House are verbose to avoid potential future conflict
# with purchased water reagents used in other tests.

#_____________________________________________________________________________________


#_____________________________________________________________________________________


lots_address = "/lots"

####REEEEEEEE Pick up here. Make sure code for post all lots reposted here.

# HTTP code 201 testing
def post_all_lots(
    client,
    post_all_lists,
    val_purch_chems,
    val_prep_chems,
    val_purch_lots,
    val_prep_lots
):

    milliq_lot = copy.deepcopy(val_purch_lots["val_purch_lot_1"])
    h3po4_lot = copy.deepcopy(val_purch_lots["val_purch_lot_2"])
    house_water_lot = copy.deepcopy(val_prep_lots["val_prep_lot_1"])
    mpa_lot = copy.deepcopy(val_prep_lots["val_prep_lot_2"])

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

    house_water_resp = client.post(lots_address, json=house_water_lot)
    house_water_id = house_water_resp.json["inserted_id"]

    assert house_water_resp.status_code == 201

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

    return milliq_id, h3po4_id, house_water_id, mpa_id

def test_add_lot(
    client,
    post_all_lots
):
    val_purch_lot_1 = copy.deepcopy(post_all_lots[0])
    val_purch_lot_1 = copy.deepcopy(post_all_lots[1])
    val_prep_lot_1 = copy.deepcopy(post_all_lots[2])
    val_prep_lot_1 = copy.deepcopy(post_all_lots[3])

    # HTTP Code 400 response body testing

    ## Confirm POST requests with empty body return 400
    empty_request_body = {}
    empty_body_reponse = client.post(lots_address, json=empty_request_body)

    assert empty_body_reponse.status_code == 400


    # HTTP code 422 response body Testing
    """
    Ensure all valid HTTP requests that fail LotSchema validation return 422
    and the appropriate error message in the request body. Missing field, missing
    value, wrong type, and invalid list entry are handled in test_invalid_lots().
    
#REEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE Remove below list from section after completion    
    * No unexpected keys arrive in a lot request.
    * Confirm the existence of the lot's parent chemical in the database.
    * Confirm that date strings are in ISO 8601 format.
    * Confirm the presence of >= 1 components on prepared lots.
    * Confirm the existence lot records for lots used as components in prepared lots.
    * Confirm that primary keys are not malformed.
    * Confirm that primary keys match in the request body and address.
    """

    ## Unexpected fields


    ## Date string in ISO 8601 format


    ## Prepared lots contain at least one component


    ## Primary keys
    ### Malformed primary keys


    ### mismatching primary keys in request and address


    ## Lot record not found for prepared component


    ## Parent chemical not found
    ### Save for last because this requires the removal of a chemical template dependency





'''
# Remaining 422 status code testing:
## Missing fields, missing values, wrong types, and invalid list entries
@pytest.mark.parametrize()
def test_invalid_lots(
    client,
    post_all_lists,
    val_purch_chems,
    val_prep_chems,
    val_purch_lots,
    val_prep_lots
):
    pass
'''