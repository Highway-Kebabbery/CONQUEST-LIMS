"""
See tests/lots/conftest.py for a detailed overview of the lots 
testing strategy. See docs/specification.md for a comprehensive view of system 
integration testing.
"""
import copy

from app.utils.validation_error_codes import ValidationErrorCodes
from app.models.chemicals import ChemicalSchema
from app.models.lots import LotSchema

from tests.lots.conftest import post_all_lots

# Variable names for Water, In-House are verbose to avoid potential future conflict
# with purchased water reagents used in other tests.

chemicals_address = "/chemicals"
lots_address = "/lots"

# HTTP code 201 testing
def test_update_lot(
        client,
    post_all_lists,
    val_purch_lots,
    val_prep_lots,
    gen_lot_extra_fields,
    gen_lots_bad_dates,
    gen_lots_good_optional_dates,
    gen_lots_miss_comp,
    gen_multiple_errors,
    val_prep_chems
):
    # Initialize lots
    val_lots = post_all_lots(client, post_all_lists, val_purch_lots, val_prep_lots)

    milliq_lot = val_lots["val_purch_lot_1"]
    h3po4_lot = val_lots["val_purch_lot_2"]
    house_water_lot = val_lots["val_prep_lot_1"]
    mpa_lot = val_lots["val_prep_lot_2"]

    milliq_id = milliq_lot[LotSchema.LOT_ID_KEY]
    h3po4_id = h3po4_lot[LotSchema.LOT_ID_KEY]
    house_water_id = house_water_lot[LotSchema.LOT_ID_KEY]
    mpa_id = mpa_lot[LotSchema.LOT_ID_KEY]

    # HTTP code 200 testing
    ## Check valid PUT requests
    put_resp_1 = client.put(f"{lots_address}/{milliq_id}", json=milliq_lot)
    put_resp_2 = client.put(f"{lots_address}/{h3po4_id}", json=h3po4_lot)
    put_resp_3 = client.put(f"{lots_address}/{house_water_id}", json=house_water_lot)
    put_resp_4 = client.put(f"{lots_address}/{mpa_id}", json=mpa_lot)

    assert put_resp_1.status_code == 200
    assert put_resp_2.status_code == 200
    assert put_resp_3.status_code == 200
    assert put_resp_4.status_code == 200


    ## Valid date strings work in optional fields
    ## (Optional date fields left blank in the rest of the happy-path testing)
    purch_lot_1_valid_open = gen_lots_good_optional_dates[0]
    purch_lot_1_valid_empty = gen_lots_good_optional_dates[1]
    purch_lot_2_valid_open = gen_lots_good_optional_dates[2]
    purch_lot_2_valid_empty = gen_lots_good_optional_dates[3]
    prep_lot_1_valid_empty = gen_lots_good_optional_dates[4]
    prep_lot_2_valid_empty = gen_lots_good_optional_dates[5]

    purch_lot_1_valid_open[LotSchema.LOT_ID_KEY] = milliq_id
    purch_lot_1_valid_empty[LotSchema.LOT_ID_KEY] = milliq_id
    purch_lot_2_valid_open[LotSchema.LOT_ID_KEY] = h3po4_id
    purch_lot_2_valid_empty[LotSchema.LOT_ID_KEY] = h3po4_id
    prep_lot_1_valid_empty[LotSchema.LOT_ID_KEY] = house_water_id
    prep_lot_2_valid_empty[LotSchema.LOT_ID_KEY] = mpa_id

    good_opt_date_resp_1 = client.put(f"{lots_address}/{milliq_id}", json=purch_lot_1_valid_open)
    good_opt_date_resp_2 = client.put(f"{lots_address}/{milliq_id}", json=purch_lot_1_valid_empty)
    good_opt_date_resp_3 = client.put(f"{lots_address}/{h3po4_id}", json=purch_lot_2_valid_open)
    good_opt_date_resp_4 = client.put(f"{lots_address}/{h3po4_id}", json=purch_lot_2_valid_empty)
    good_opt_date_resp_5 = client.put(f"{lots_address}/{house_water_id}", json=prep_lot_1_valid_empty)
    good_opt_date_resp_6 = client.put(f"{lots_address}/{mpa_id}", json=prep_lot_2_valid_empty)

    assert good_opt_date_resp_1.status_code == 200
    assert good_opt_date_resp_2.status_code == 200
    assert good_opt_date_resp_3.status_code == 200
    assert good_opt_date_resp_4.status_code == 200
    assert good_opt_date_resp_5.status_code == 200
    assert good_opt_date_resp_6.status_code == 200


    # HTTP code 422 response body Testing
    """
    Ensure all valid HTTP requests that fail LotSchema validation return 422
    and the appropriate error message in the request body. Missing field, missing
    value, wrong type, invalid list entry, and malformed primary keys are handled 
    in further tests below.
    """
    
    ## Unexpected fields
    purch_lot_1_extra_field = copy.deepcopy(gen_lot_extra_fields[0])
    purch_lot_2_extra_field = copy.deepcopy(gen_lot_extra_fields[1])
    prep_lot_1_extra_field = copy.deepcopy(gen_lot_extra_fields[2])
    prep_lot_2_extra_field = copy.deepcopy(gen_lot_extra_fields[3])
    prep_lot_1_extra_comp_field = copy.deepcopy(gen_lot_extra_fields[4])
    prep_lot_2_extra_comp_field = copy.deepcopy(gen_lot_extra_fields[5])

    purch_lot_1_extra_field[LotSchema.LOT_ID_KEY] = milliq_id
    purch_lot_2_extra_field[LotSchema.LOT_ID_KEY] = h3po4_id
    prep_lot_1_extra_field[LotSchema.LOT_ID_KEY] = house_water_id
    prep_lot_2_extra_field[LotSchema.LOT_ID_KEY] = mpa_id
    prep_lot_1_extra_comp_field[LotSchema.LOT_ID_KEY] = house_water_id
    prep_lot_2_extra_comp_field[LotSchema.LOT_ID_KEY] = mpa_id

    ext_field_resp_1 = client.put(f"{lots_address}/{milliq_id}", json=purch_lot_1_extra_field)
    ext_field_resp_2 = client.put(f"{lots_address}/{h3po4_id}", json=purch_lot_2_extra_field)
    ext_field_resp_3 = client.put(f"{lots_address}/{house_water_id}", json=prep_lot_1_extra_field)
    ext_field_resp_4 = client.put(f"{lots_address}/{mpa_id}", json=prep_lot_2_extra_field)
    ext_field_resp_5 = client.put(f"{lots_address}/{house_water_id}", json=prep_lot_1_extra_comp_field)
    ext_field_resp_6 = client.put(f"{lots_address}/{mpa_id}", json=prep_lot_2_extra_comp_field)

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

    purch_lot_1_open[LotSchema.LOT_ID_KEY] = milliq_id
    purch_lot_1_expiry[LotSchema.LOT_ID_KEY] = milliq_id
    purch_lot_1_empty[LotSchema.LOT_ID_KEY] = milliq_id
    purch_lot_2_open[LotSchema.LOT_ID_KEY] = h3po4_id
    purch_lot_2_expiry[LotSchema.LOT_ID_KEY] = h3po4_id
    purch_lot_2_empty[LotSchema.LOT_ID_KEY] = h3po4_id
    prep_lot_1_prep[LotSchema.LOT_ID_KEY] = house_water_id
    prep_lot_1_expiry[LotSchema.LOT_ID_KEY] = house_water_id
    prep_lot_1_empty[LotSchema.LOT_ID_KEY] = house_water_id
    prep_lot_2_prep[LotSchema.LOT_ID_KEY] = mpa_id
    prep_lot_2_expiry[LotSchema.LOT_ID_KEY] = mpa_id
    prep_lot_2_empty[LotSchema.LOT_ID_KEY] = mpa_id

    purch_lot_1_open_offset[LotSchema.LOT_ID_KEY] = milliq_id
    purch_lot_1_expiry_offset[LotSchema.LOT_ID_KEY] = milliq_id
    purch_lot_1_empty_offset[LotSchema.LOT_ID_KEY] = milliq_id
    purch_lot_2_open_offset[LotSchema.LOT_ID_KEY] = h3po4_id
    purch_lot_2_expiry_offset[LotSchema.LOT_ID_KEY] = h3po4_id
    purch_lot_2_empty_offset[LotSchema.LOT_ID_KEY] = h3po4_id
    prep_lot_1_prep_offset[LotSchema.LOT_ID_KEY] = house_water_id
    prep_lot_1_expiry_offset[LotSchema.LOT_ID_KEY] = house_water_id
    prep_lot_1_empty_offset[LotSchema.LOT_ID_KEY] = house_water_id
    prep_lot_2_prep_offset[LotSchema.LOT_ID_KEY] = mpa_id
    prep_lot_2_expiry_offset[LotSchema.LOT_ID_KEY] = mpa_id
    prep_lot_2_empty_offset[LotSchema.LOT_ID_KEY] = mpa_id

    bad_date_resp_1 = client.put(f"{lots_address}/{milliq_id}", json=purch_lot_1_open)
    bad_date_resp_2 = client.put(f"{lots_address}/{milliq_id}", json=purch_lot_1_expiry)
    bad_date_resp_3 = client.put(f"{lots_address}/{milliq_id}", json=purch_lot_1_empty)
    bad_date_resp_4 = client.put(f"{lots_address}/{h3po4_id}", json=purch_lot_2_open)
    bad_date_resp_5 = client.put(f"{lots_address}/{h3po4_id}", json=purch_lot_2_expiry)
    bad_date_resp_6 = client.put(f"{lots_address}/{h3po4_id}", json=purch_lot_2_empty)
    bad_date_resp_7 = client.put(f"{lots_address}/{house_water_id}", json=prep_lot_1_prep)
    bad_date_resp_8 = client.put(f"{lots_address}/{house_water_id}", json=prep_lot_1_expiry)
    bad_date_resp_9 = client.put(f"{lots_address}/{house_water_id}", json=prep_lot_1_empty)
    bad_date_resp_10 = client.put(f"{lots_address}/{mpa_id}", json=prep_lot_2_prep)
    bad_date_resp_11 = client.put(f"{lots_address}/{mpa_id}", json=prep_lot_2_expiry)
    bad_date_resp_12 = client.put(f"{lots_address}/{mpa_id}", json=prep_lot_2_empty)

    bad_date_resp_13 = client.put(f"{lots_address}/{milliq_id}", json=purch_lot_1_open_offset)
    bad_date_resp_14 = client.put(f"{lots_address}/{milliq_id}", json=purch_lot_1_expiry_offset)
    bad_date_resp_15 = client.put(f"{lots_address}/{milliq_id}", json=purch_lot_1_empty_offset)
    bad_date_resp_16 = client.put(f"{lots_address}/{h3po4_id}", json=purch_lot_2_open_offset)
    bad_date_resp_17 = client.put(f"{lots_address}/{h3po4_id}", json=purch_lot_2_expiry_offset)
    bad_date_resp_18 = client.put(f"{lots_address}/{h3po4_id}", json=purch_lot_2_empty_offset)
    bad_date_resp_19 = client.put(f"{lots_address}/{house_water_id}", json=prep_lot_1_prep_offset)
    bad_date_resp_20 = client.put(f"{lots_address}/{house_water_id}", json=prep_lot_1_expiry_offset)
    bad_date_resp_21 = client.put(f"{lots_address}/{house_water_id}", json=prep_lot_1_empty_offset)
    bad_date_resp_22 = client.put(f"{lots_address}/{mpa_id}", json=prep_lot_2_prep_offset)
    bad_date_resp_23 = client.put(f"{lots_address}/{mpa_id}", json=prep_lot_2_expiry_offset)
    bad_date_resp_24 = client.put(f"{lots_address}/{mpa_id}", json=prep_lot_2_empty_offset)

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

    prep_lot_1_miss_comp[LotSchema.LOT_ID_KEY] = house_water_id
    prep_lot_2_miss_comp[LotSchema.LOT_ID_KEY] = mpa_id

    miss_comp_resp_1 = client.put(f"{lots_address}/{house_water_id}", json=prep_lot_1_miss_comp)
    miss_comp_resp_2 = client.put(f"{lots_address}/{mpa_id}", json=prep_lot_2_miss_comp)

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

    purch_lot_1_extra_field_type[LotSchema.LOT_ID_KEY] = milliq_id
    purch_lot_2_extra_field_type[LotSchema.LOT_ID_KEY] = h3po4_id
    prep_lot_1_extra_field_type[LotSchema.LOT_ID_KEY] = house_water_id
    prep_lot_2_extra_field_type[LotSchema.LOT_ID_KEY] = mpa_id

    extra_field_type_resp_1 = client.put(f"{lots_address}/{milliq_id}", json=purch_lot_1_extra_field_type)
    extra_field_type_resp_2 = client.put(f"{lots_address}/{h3po4_id}", json=purch_lot_2_extra_field_type)
    extra_field_type_resp_3 = client.put(f"{lots_address}/{house_water_id}", json=prep_lot_1_extra_field_type)
    extra_field_type_resp_4 = client.put(f"{lots_address}/{mpa_id}", json=prep_lot_2_extra_field_type)
    
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
    
    mpa_lot[LotSchema.LOT_ID_KEY] = mpa_id

    post_resp = client.put(f"{lots_address}/{mpa_id}", json=mpa_lot)
    post_data = post_resp.get_json()

    assert post_data["error"].startswith(ValidationErrorCodes.LOT_NOT_FOUND_MSG)
    assert post_resp.status_code == 404


    ## PUT request for missing lot
    ### Depends on the test above removing the lot of Water, In-House
    post_resp = client.put(f"{lots_address}/{house_water_id}", json=house_water_lot)
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
    miss_chem_post_resp = client.put(f"{lots_address}/{mpa_id}", json=mpa_lot)
    data = miss_chem_post_resp.get_json()

    assert data["error"].startswith(ValidationErrorCodes.CHEM_NOT_FOUND_MSG)
    assert miss_chem_post_resp.status_code == 404


# HTTP code 422 testing continued
def test_update_bad_primary_keys(
        client,
        post_all_lists,
        val_purch_lots,
        val_prep_lots
):
    # Initialize lots
    val_lots = post_all_lots(client, post_all_lists, val_purch_lots, val_prep_lots)

    milliq_lot = val_lots["val_purch_lot_1"]
    h3po4_lot = val_lots["val_purch_lot_2"]
    house_water_lot = val_lots["val_prep_lot_1"]
    mpa_lot = val_lots["val_prep_lot_2"]

    milliq_id = milliq_lot[LotSchema.LOT_ID_KEY]
    h3po4_id = h3po4_lot[LotSchema.LOT_ID_KEY]
    house_water_id = house_water_lot[LotSchema.LOT_ID_KEY]
    mpa_id = mpa_lot[LotSchema.LOT_ID_KEY]

    # Send request with malformed primary key to address with matching malformed primary key
    bad_matching_key_1 = copy.deepcopy(milliq_lot)
    bad_matching_key_2 = copy.deepcopy(h3po4_lot)
    bad_matching_key_3 = copy.deepcopy(house_water_lot)
    bad_matching_key_4 = copy.deepcopy(mpa_lot)

    bad_matching_key_1[LotSchema.LOT_ID_KEY] = "1"
    bad_matching_key_2[LotSchema.LOT_ID_KEY] = "1"
    bad_matching_key_3[LotSchema.LOT_ID_KEY] = "1"
    bad_matching_key_4[LotSchema.LOT_ID_KEY] = "1"

    bad_matching_key_resp_1 = client.put(f"{lots_address}/1", json=bad_matching_key_1)
    bad_matching_key_resp_2 = client.put(f"{lots_address}/1", json=bad_matching_key_2)
    bad_matching_key_resp_3 = client.put(f"{lots_address}/1", json=bad_matching_key_3)
    bad_matching_key_resp_4 = client.put(f"{lots_address}/1", json=bad_matching_key_4)

    data_1 = bad_matching_key_resp_1.get_json()
    data_2 = bad_matching_key_resp_1.get_json()
    data_3 = bad_matching_key_resp_1.get_json()
    data_4 = bad_matching_key_resp_1.get_json()

    assert bad_matching_key_resp_1.status_code == 422
    assert data_1["error"].startswith(ValidationErrorCodes.INVALID_ID_MSG)
    assert bad_matching_key_resp_2.status_code == 422
    assert data_2["error"].startswith(ValidationErrorCodes.INVALID_ID_MSG)
    assert bad_matching_key_resp_3.status_code == 422
    assert data_3["error"].startswith(ValidationErrorCodes.INVALID_ID_MSG)
    assert bad_matching_key_resp_4.status_code == 422
    assert data_4["error"].startswith(ValidationErrorCodes.INVALID_ID_MSG)
    

    # Swap primary keys and PUT to trigger primary key mismatch error
    milliq_lot[LotSchema.LOT_ID_KEY] = mpa_id
    h3po4_lot[LotSchema.LOT_ID_KEY] = house_water_id
    house_water_lot[LotSchema.LOT_ID_KEY] = h3po4_id
    mpa_lot[LotSchema.LOT_ID_KEY] = milliq_id

    put_resp_1 = client.put(f"{lots_address}/{milliq_id}", json=milliq_lot)
    put_resp_2 = client.put(f"{lots_address}/{h3po4_id}", json=h3po4_lot)
    put_resp_3 = client.put(f"{lots_address}/{house_water_id}", json=house_water_lot)
    put_resp_4 = client.put(f"{lots_address}/{mpa_id}", json=mpa_lot)

    data_1 = put_resp_1.get_json()
    data_2 = put_resp_2.get_json()
    data_3 = put_resp_3.get_json()
    data_4 = put_resp_4.get_json()

    assert put_resp_1.status_code == 422
    assert data_1["error"].startswith("Request body primary key does not match address <lot_id>:")
    assert put_resp_2.status_code == 422
    assert data_2["error"].startswith("Request body primary key does not match address <lot_id>:")
    assert put_resp_3.status_code == 422
    assert data_3["error"].startswith("Request body primary key does not match address <lot_id>:")
    assert put_resp_4.status_code == 422
    assert data_4["error"].startswith("Request body primary key does not match address <lot_id>:")

    # Remove primary keys from request bodies and PUT to trigger missing primary key error
    del milliq_lot[LotSchema.LOT_ID_KEY]
    del h3po4_lot[LotSchema.LOT_ID_KEY]
    del house_water_lot[LotSchema.LOT_ID_KEY]
    del mpa_lot[LotSchema.LOT_ID_KEY]

    put_resp_1 = client.put(f"{lots_address}/{milliq_id}", json=milliq_lot)
    put_resp_2 = client.put(f"{lots_address}/{h3po4_id}", json=h3po4_lot)
    put_resp_3 = client.put(f"{lots_address}/{house_water_id}", json=house_water_lot)
    put_resp_4 = client.put(f"{lots_address}/{mpa_id}", json=mpa_lot)

    data_1 = put_resp_1.get_json()
    data_2 = put_resp_2.get_json()
    data_3 = put_resp_3.get_json()
    data_4 = put_resp_4.get_json()

    assert put_resp_1.status_code == 422
    assert data_1["error"].startswith("Request body missing primary key:")
    assert put_resp_2.status_code == 422
    assert data_2["error"].startswith("Request body missing primary key:")
    assert put_resp_3.status_code == 422
    assert data_3["error"].startswith("Request body missing primary key:")
    assert put_resp_4.status_code == 422
    assert data_4["error"].startswith("Request body missing primary key:")


# Remaining 422 status code testing:
## Missing fields, missing values, wrong types, and invalid list entries
def test_update_invalid_purch_lots(
    client,
    post_all_lists,
    val_purch_chems,
    val_prep_chems,
    val_purch_lots,
    val_prep_lots,
    invalid_lots
):
    ## Add primary keys to lot objects
    val_lots = post_all_lots(client, post_all_lists, val_purch_lots, val_prep_lots)

    milliq_id = val_lots["val_purch_lot_1"][LotSchema.LOT_ID_KEY]
    h3po4_id = val_lots["val_purch_lot_2"][LotSchema.LOT_ID_KEY]
    
    for payload, expected_error_prefix in invalid_lots["invalid_prep_lots"]:
        id_append_val_purch_lot_1 = copy.deepcopy(payload)
        id_append_val_purch_lot_2 = copy.deepcopy(payload)
        id_append_val_purch_lot_1[LotSchema.LOT_ID_KEY] = milliq_id
        id_append_val_purch_lot_2[LotSchema.LOT_ID_KEY] = h3po4_id
        
        response_1 = client.put(f"{lots_address}/{milliq_id}", json=copy.deepcopy(id_append_val_purch_lot_1))
        response_2 = client.put(f"{lots_address}/{h3po4_id}", json=copy.deepcopy(id_append_val_purch_lot_2))
        
        data_1 = response_1.get_json()
        data_2 = response_2.get_json()

        assert data_1["error"].startswith(str(expected_error_prefix))
        assert response_1.status_code == 422
        assert data_2["error"].startswith(str(expected_error_prefix))
        assert response_2.status_code == 422


def test_update_invalid_prep_lots(
    client,
    post_all_lists,
    val_purch_chems,
    val_prep_chems,
    val_purch_lots,
    val_prep_lots,
    invalid_lots
):
    ## Add primary keys to lot objects
    val_lots = post_all_lots(client, post_all_lists, val_purch_lots, val_prep_lots)

    house_water_id = val_lots["val_prep_lot_1"][LotSchema.LOT_ID_KEY]
    mpa_id = val_lots["val_prep_lot_2"][LotSchema.LOT_ID_KEY]
    
    for payload, expected_error_prefix in invalid_lots["invalid_prep_lots"]:
        id_append_val_prep_lot_1 = copy.deepcopy(payload)
        id_append_val_prep_lot_2 = copy.deepcopy(payload)
        id_append_val_prep_lot_1[LotSchema.LOT_ID_KEY] = house_water_id
        id_append_val_prep_lot_2[LotSchema.LOT_ID_KEY] = mpa_id
        
        response_1 = client.put(f"{lots_address}/{house_water_id}", json=copy.deepcopy(id_append_val_prep_lot_1))
        response_2 = client.put(f"{lots_address}/{mpa_id}", json=copy.deepcopy(id_append_val_prep_lot_2))
        
        data_1 = response_1.get_json()
        data_2 = response_2.get_json()

        assert data_1["error"].startswith(str(expected_error_prefix))
        assert response_1.status_code == 422
        assert data_2["error"].startswith(str(expected_error_prefix))
        assert response_2.status_code == 422