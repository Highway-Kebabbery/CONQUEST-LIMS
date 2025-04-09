import pytest, copy
from chemical_inventory_api_v1 import LotSchema, ValidationErrorCodes, ChemicalSchema

# Variable names for Water, In-House are verbose to avoid potential future conflict
# with purchased water reagents used in other tests.

chemicals_address = "/chemicals"
lots_address = "/lots"

# HTTP code 201 testing
def test_add_lot(
    client,
    post_all_lists,
    val_purch_chems,
    val_prep_chems,
    val_purch_lots,
    val_prep_lots,
    gen_lot_extra_fields,
    gen_lots_bad_dates,
    gen_lots_miss_comp,
    gen_multiple_errors
):

    milliq_lot = copy.deepcopy(val_purch_lots["val_purch_lot_1"])
    h3po4_lot = copy.deepcopy(val_purch_lots["val_purch_lot_2"])
    house_water_lot = copy.deepcopy(val_prep_lots["val_prep_lot_1"])
    mpa_lot = copy.deepcopy(val_prep_lots["val_prep_lot_2"])

    ## POST val_purch_lots in order to retrieve primary keys needed for components in val_prep_lots
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

    ## Add primary key for MilliQ to Water, In-House, POST Water, In-House, and
    ## return primary key from Water, In-House to use in Mobile Phase A
    component = house_water_lot[LotSchema.COMPONENTS_KEY][0]
    component[LotSchema.COMP_LOT_KEY] = milliq_data[LotSchema.LOT_ID_KEY]

    house_water_resp = client.post(lots_address, json=house_water_lot)
    house_water_id = house_water_resp.json["inserted_id"]

    assert house_water_resp.status_code == 201

    get_house_water_resp = client.get(f"{lots_address}/{house_water_id}")

    house_water_data = get_house_water_resp.get_json()

    ## Add component primary keys in Mobile Phase A and POST Mobile Phase A
    house_water_component = mpa_lot[LotSchema.COMPONENTS_KEY][0]
    house_water_component[LotSchema.COMP_LOT_KEY] = house_water_data[LotSchema.LOT_ID_KEY]
    h3po4_component = mpa_lot[LotSchema.COMPONENTS_KEY][1]
    h3po4_component[LotSchema.COMP_LOT_KEY] = h3po4_data[LotSchema.LOT_ID_KEY]

    ## POST Mobile Phase A and confirm success
    mpa_resp = client.post(lots_address, json=mpa_lot)

    mpa_id = mpa_resp.get_json()["inserted_id"]

    assert mpa_resp.status_code == 201
    
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
    * No unexpected keys arrive in a lot request or its components.
    * Confirm the existence of the lot's parent chemical in the database.
    * Confirm that date strings are in ISO 8601 format.
    * Confirm the presence of >= 1 components on prepared lots.
    * Confirm the existence lot records for lots used as components in prepared lots.
    * Confirm that primary keys are not malformed.
    * Confirm that primary keys match in the request body and address.
    """
    
    ## Unexpected fields
    purch_lot_1_extra_field = copy.deepcopy(gen_lot_extra_fields[0])
    purch_lot_2_extra_field = copy.deepcopy(gen_lot_extra_fields[1])
    prep_lot_1_extra_field = copy.deepcopy(gen_lot_extra_fields[2])
    prep_lot_2_extra_field = copy.deepcopy(gen_lot_extra_fields[3])
    prep_lot_1_extra_comp_field = copy.deepcopy(gen_lot_extra_fields[4])
    prep_lot_2_extra_comp_field = copy.deepcopy(gen_lot_extra_fields[5])

    ext_field_resp_1 = client.post(lots_address, json=purch_lot_1_extra_field)
    ext_field_resp_2 = client.post(lots_address, json=purch_lot_2_extra_field)
    ext_field_resp_3 = client.post(lots_address, json=prep_lot_1_extra_field)
    ext_field_resp_4 = client.post(lots_address, json=prep_lot_2_extra_field)
    ext_field_resp_5 = client.post(lots_address, json=prep_lot_1_extra_comp_field)
    ext_field_resp_6 = client.post(lots_address, json=prep_lot_2_extra_comp_field)

    data_1 = ext_field_resp_1.get_json()
    data_2 = ext_field_resp_2.get_json()
    data_3 = ext_field_resp_3.get_json()
    data_4 = ext_field_resp_4.get_json()
    data_5 = ext_field_resp_5.get_json()
    data_6 = ext_field_resp_6.get_json()
    
    assert data_1["error"].startswith(ValidationErrorCodes.UNEXP_FIELD_MSG)
    assert ext_field_resp_1.status_code == 422
    assert data_2["error"].startswith(ValidationErrorCodes.UNEXP_FIELD_MSG)
    assert ext_field_resp_2.status_code == 422
    assert data_3["error"].startswith(ValidationErrorCodes.UNEXP_FIELD_MSG)
    assert ext_field_resp_3.status_code == 422
    assert data_4["error"].startswith(ValidationErrorCodes.UNEXP_FIELD_MSG)
    assert ext_field_resp_4.status_code == 422
    assert data_5["error"].startswith(ValidationErrorCodes.UNEXP_FIELD_MSG)
    assert ext_field_resp_5.status_code == 422
    assert data_6["error"].startswith(ValidationErrorCodes.UNEXP_FIELD_MSG)
    assert ext_field_resp_6.status_code == 422
    

    ## Date string in ISO 8601 format
    purch_lot_1_open = copy.deepcopy(gen_lots_bad_dates[0])
    purch_lot_1_expiry = copy.deepcopy(gen_lots_bad_dates[1])
    purch_lot_1_empty = copy.deepcopy(gen_lots_bad_dates[2])
    purch_lot_2_open = copy.deepcopy(gen_lots_bad_dates[3])
    purch_lot_2_expiry = copy.deepcopy(gen_lots_bad_dates[4])
    purch_lot_2_empty = copy.deepcopy(gen_lots_bad_dates[5])
    prep_lot_1_prep = copy.deepcopy(gen_lots_bad_dates[6])
    prep_lot_1_expiry = copy.deepcopy(gen_lots_bad_dates[7])
    prep_lot_1_empty = copy.deepcopy(gen_lots_bad_dates[8])
    prep_lot_2_prep = copy.deepcopy(gen_lots_bad_dates[9])
    prep_lot_2_expiry = copy.deepcopy(gen_lots_bad_dates[10])
    prep_lot_2_empty = copy.deepcopy(gen_lots_bad_dates[11])

    purch_lot_1_open_offset = copy.deepcopy(gen_lots_bad_dates[12])
    purch_lot_1_expiry_offset = copy.deepcopy(gen_lots_bad_dates[13])
    purch_lot_1_empty_offset = copy.deepcopy(gen_lots_bad_dates[14])
    purch_lot_2_open_offset = copy.deepcopy(gen_lots_bad_dates[15])
    purch_lot_2_expiry_offset = copy.deepcopy(gen_lots_bad_dates[16])
    purch_lot_2_empty_offset = copy.deepcopy(gen_lots_bad_dates[17])
    prep_lot_1_prep_offset = copy.deepcopy(gen_lots_bad_dates[18])
    prep_lot_1_expiry_offset = copy.deepcopy(gen_lots_bad_dates[19])
    prep_lot_1_empty_offset = copy.deepcopy(gen_lots_bad_dates[20])
    prep_lot_2_prep_offset = copy.deepcopy(gen_lots_bad_dates[21])
    prep_lot_2_expiry_offset = copy.deepcopy(gen_lots_bad_dates[22])
    prep_lot_2_empty_offset = copy.deepcopy(gen_lots_bad_dates[23])

    bad_date_resp_1 = client.post(lots_address, json=purch_lot_1_open)
    bad_date_resp_2 = client.post(lots_address, json=purch_lot_1_expiry)
    bad_date_resp_3 = client.post(lots_address, json=purch_lot_1_empty)
    bad_date_resp_4 = client.post(lots_address, json=purch_lot_2_open)
    bad_date_resp_5 = client.post(lots_address, json=purch_lot_2_expiry)
    bad_date_resp_6 = client.post(lots_address, json=purch_lot_2_empty)
    bad_date_resp_7 = client.post(lots_address, json=prep_lot_1_prep)
    bad_date_resp_8 = client.post(lots_address, json=prep_lot_1_expiry)
    bad_date_resp_9 = client.post(lots_address, json=prep_lot_1_empty)
    bad_date_resp_10 = client.post(lots_address, json=prep_lot_2_prep)
    bad_date_resp_11 = client.post(lots_address, json=prep_lot_2_expiry)
    bad_date_resp_12 = client.post(lots_address, json=prep_lot_2_empty)

    bad_date_resp_13 = client.post(lots_address, json=purch_lot_1_open_offset)
    bad_date_resp_14 = client.post(lots_address, json=purch_lot_1_expiry_offset)
    bad_date_resp_15 = client.post(lots_address, json=purch_lot_1_empty_offset)
    bad_date_resp_16 = client.post(lots_address, json=purch_lot_2_open_offset)
    bad_date_resp_17 = client.post(lots_address, json=purch_lot_2_expiry_offset)
    bad_date_resp_18 = client.post(lots_address, json=purch_lot_2_empty_offset)
    bad_date_resp_19 = client.post(lots_address, json=prep_lot_1_prep_offset)
    bad_date_resp_20 = client.post(lots_address, json=prep_lot_1_expiry_offset)
    bad_date_resp_21 = client.post(lots_address, json=prep_lot_1_empty_offset)
    bad_date_resp_22 = client.post(lots_address, json=prep_lot_2_prep_offset)
    bad_date_resp_23 = client.post(lots_address, json=prep_lot_2_expiry_offset)
    bad_date_resp_24 = client.post(lots_address, json=prep_lot_2_empty_offset)

    data_1 = bad_date_resp_1.get_json()
    data_2 = bad_date_resp_2.get_json()
    data_3 = bad_date_resp_3.get_json()
    data_4 = bad_date_resp_4.get_json()
    data_5 = bad_date_resp_5.get_json()
    data_6 = bad_date_resp_6.get_json()
    data_7 = bad_date_resp_7.get_json()
    data_8 = bad_date_resp_8.get_json()
    data_9 = bad_date_resp_9.get_json()
    data_10 = bad_date_resp_10.get_json()
    data_11 = bad_date_resp_11.get_json()
    data_12 = bad_date_resp_12.get_json()

    data_13 = bad_date_resp_13.get_json()
    data_14 = bad_date_resp_14.get_json()
    data_15 = bad_date_resp_15.get_json()
    data_16 = bad_date_resp_16.get_json()
    data_17 = bad_date_resp_17.get_json()
    data_18 = bad_date_resp_18.get_json()
    data_19 = bad_date_resp_19.get_json()
    data_20 = bad_date_resp_20.get_json()
    data_21 = bad_date_resp_21.get_json()
    data_22 = bad_date_resp_22.get_json()
    data_23 = bad_date_resp_23.get_json()
    data_24 = bad_date_resp_24.get_json()

    assert data_1["error"].startswith(ValidationErrorCodes.WRONG_DATE_FORMAT_MSG)
    assert bad_date_resp_1.status_code == 422
    assert data_2["error"].startswith(ValidationErrorCodes.WRONG_DATE_FORMAT_MSG)
    assert bad_date_resp_2.status_code == 422
    assert data_3["error"].startswith(ValidationErrorCodes.WRONG_DATE_FORMAT_MSG)
    assert bad_date_resp_3.status_code == 422
    assert data_4["error"].startswith(ValidationErrorCodes.WRONG_DATE_FORMAT_MSG)
    assert bad_date_resp_4.status_code == 422
    assert data_5["error"].startswith(ValidationErrorCodes.WRONG_DATE_FORMAT_MSG)
    assert bad_date_resp_5.status_code == 422
    assert data_6["error"].startswith(ValidationErrorCodes.WRONG_DATE_FORMAT_MSG)
    assert bad_date_resp_6.status_code == 422
    assert data_7["error"].startswith(ValidationErrorCodes.WRONG_DATE_FORMAT_MSG)
    assert bad_date_resp_7.status_code == 422
    assert data_8["error"].startswith(ValidationErrorCodes.WRONG_DATE_FORMAT_MSG)
    assert bad_date_resp_8.status_code == 422
    assert data_9["error"].startswith(ValidationErrorCodes.WRONG_DATE_FORMAT_MSG)
    assert bad_date_resp_9.status_code == 422
    assert data_10["error"].startswith(ValidationErrorCodes.WRONG_DATE_FORMAT_MSG)
    assert bad_date_resp_10.status_code == 422
    assert data_11["error"].startswith(ValidationErrorCodes.WRONG_DATE_FORMAT_MSG)
    assert bad_date_resp_11.status_code == 422
    assert data_12["error"].startswith(ValidationErrorCodes.WRONG_DATE_FORMAT_MSG)
    assert bad_date_resp_12.status_code == 422

    assert data_13["error"].startswith(ValidationErrorCodes.WRONG_DATE_FORMAT_MSG)
    assert bad_date_resp_13.status_code == 422
    assert data_14["error"].startswith(ValidationErrorCodes.WRONG_DATE_FORMAT_MSG)
    assert bad_date_resp_14.status_code == 422
    assert data_15["error"].startswith(ValidationErrorCodes.WRONG_DATE_FORMAT_MSG)
    assert bad_date_resp_15.status_code == 422
    assert data_16["error"].startswith(ValidationErrorCodes.WRONG_DATE_FORMAT_MSG)
    assert bad_date_resp_16.status_code == 422
    assert data_17["error"].startswith(ValidationErrorCodes.WRONG_DATE_FORMAT_MSG)
    assert bad_date_resp_17.status_code == 422
    assert data_18["error"].startswith(ValidationErrorCodes.WRONG_DATE_FORMAT_MSG)
    assert bad_date_resp_18.status_code == 422
    assert data_19["error"].startswith(ValidationErrorCodes.WRONG_DATE_FORMAT_MSG)
    assert bad_date_resp_19.status_code == 422
    assert data_20["error"].startswith(ValidationErrorCodes.WRONG_DATE_FORMAT_MSG)
    assert bad_date_resp_20.status_code == 422
    assert data_21["error"].startswith(ValidationErrorCodes.WRONG_DATE_FORMAT_MSG)
    assert bad_date_resp_21.status_code == 422
    assert data_22["error"].startswith(ValidationErrorCodes.WRONG_DATE_FORMAT_MSG)
    assert bad_date_resp_22.status_code == 422
    assert data_23["error"].startswith(ValidationErrorCodes.WRONG_DATE_FORMAT_MSG)
    assert bad_date_resp_23.status_code == 422
    assert data_24["error"].startswith(ValidationErrorCodes.WRONG_DATE_FORMAT_MSG)
    assert bad_date_resp_24.status_code == 422

    
    ## Prepared lots contain at least one component
    prep_lot_1_miss_comp = copy.deepcopy(gen_lots_miss_comp[0])
    prep_lot_2_miss_comp = copy.deepcopy(gen_lots_miss_comp[1])

    miss_comp_resp_1 = client.post(lots_address, json=prep_lot_1_miss_comp)
    miss_comp_resp_2 = client.post(lots_address, json=prep_lot_2_miss_comp)

    data_1 = miss_comp_resp_1.get_json()
    data_2 = miss_comp_resp_2.get_json()

    assert data_1["error"].startswith(ValidationErrorCodes.MISSING_COMP_MSG)
    assert miss_comp_resp_1.status_code == 422
    assert data_2["error"].startswith(ValidationErrorCodes.MISSING_COMP_MSG)
    assert miss_comp_resp_2.status_code == 422


    ## Multiple error should return the first-encountered error
    purch_lot_1_extra_field_type = copy.deepcopy(gen_multiple_errors[0])
    purch_lot_2_extra_field_type = copy.deepcopy(gen_multiple_errors[1])
    prep_lot_1_extra_field_type = copy.deepcopy(gen_multiple_errors[2])
    prep_lot_2_extra_field_type = copy.deepcopy(gen_multiple_errors[3])

    extra_field_type_resp_1 = client.post(lots_address, json=purch_lot_1_extra_field_type)
    extra_field_type_resp_2 = client.post(lots_address, json=purch_lot_2_extra_field_type)
    extra_field_type_resp_3 = client.post(lots_address, json=prep_lot_1_extra_field_type)
    extra_field_type_resp_4 = client.post(lots_address, json=prep_lot_2_extra_field_type)
    
    data_1 = extra_field_type_resp_1.get_json()
    data_2 = extra_field_type_resp_2.get_json()
    data_3 = extra_field_type_resp_3.get_json()
    data_4 = extra_field_type_resp_4.get_json()

    assert data_1["error"].startswith(ValidationErrorCodes.UNEXP_FIELD_MSG)
    assert extra_field_type_resp_1.status_code == 422
    assert data_2["error"].startswith(ValidationErrorCodes.UNEXP_FIELD_MSG)
    assert extra_field_type_resp_2.status_code == 422
    assert data_3["error"].startswith(ValidationErrorCodes.UNEXP_FIELD_MSG)
    assert extra_field_type_resp_3.status_code == 422
    assert data_4["error"].startswith(ValidationErrorCodes.UNEXP_FIELD_MSG)
    assert extra_field_type_resp_4.status_code == 422

    # HTTP code 404 testing
    ## 422 testing resumes below because these tests interrupt fixture availability

    ## Lot record not found for prepared lot component
    ### Remove lots for Water, In-House and then try to use its valid, non-existant 
    ### primary keys to log a lot of Mobile Phase A
    delete_response = client.delete(f"{lots_address}/{house_water_id}")

    assert delete_response.status_code == 204

    post_resp = client.post(lots_address, json=mpa_lot)
    post_data = post_resp.get_json()

    assert post_data["error"].startswith(ValidationErrorCodes.LOT_NOT_FOUND_MSG)
    assert post_resp.status_code == 404


    ## Parent chemical not found
    ### Save for last because this requires the removal of a chemical template fixture
    ### Remove chemical for Mobile Phase A then try to log lot of Mobile Phase A
    #### This has multiple errors, but parent chem record existence is validated first
    
    ### Remove parent record
    mpa_chem_id = val_prep_chems["val_prep_chem_2"][ChemicalSchema.CHEM_ID_KEY]
    del_resp = client.delete(f"{chemicals_address}/{mpa_chem_id}")

    assert del_resp.status_code == 204

    ### Attempt to add lot with missing parent chemical record
    miss_chem_post_resp = client.post(lots_address, json=mpa_lot)
    data = miss_chem_post_resp.get_json()

    assert data["error"].startswith(ValidationErrorCodes.CHEM_NOT_FOUND_MSG)
    assert miss_chem_post_resp.status_code == 404



# Remaining 422 status code testing:
## Missing fields, missing values, wrong types, and invalid list entries
def test_invalid_lots(
    client,
    post_all_lists,
    val_purch_chems,
    val_prep_chems,
    val_purch_lots,
    val_prep_lots,
    invalid_lots
):
    # I opted to skip using parametrize so that I could actually use the giant list of
    # invalid lots as a fixture. It got too complicated with the need to dynamically generate
    # lot primary keys after testing began.
    for payload, expected_error_prefix in invalid_lots:
        print(f"Payload #{invalid_lots.index((payload, expected_error_prefix))} before POST: {payload}")
        response = client.post(lots_address, json=copy.deepcopy(payload))
        data = response.get_json()

        if not "error" in data \
            or not data["error"].startswith(str(expected_error_prefix)):
            print(f"Payload #{invalid_lots.index((payload, expected_error_prefix))}")
            print(f"Payload after POST: {payload}")
            print(f"Expected error: {expected_error_prefix}")
            print(f"Returned error: {data['error']}")
        assert data["error"].startswith(str(expected_error_prefix))
        assert response.status_code == 422
