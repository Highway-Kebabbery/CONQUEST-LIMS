import pytest, copy

from app.utils.validation_error_codes import ValidationErrorCodes
from app.models.chemicals import ChemicalSchema

chemicals_address = "/chemicals"

@pytest.fixture()
def post_valid_chemicals(
    client,
    post_all_lists,
    valid_purchased_chemical_1,
    valid_purchased_chemical_2,
    valid_prepared_chemical_1,
    valid_prepared_chemical_2
    ):
    # POST chemicals to set up testing
    post_chem_response_1 = client.post(chemicals_address, json=valid_purchased_chemical_1)
    post_chem_response_2 = client.post(chemicals_address, json=valid_purchased_chemical_2)
    post_chem_response_3 = client.post(chemicals_address, json=valid_prepared_chemical_1)
    post_chem_response_4 = client.post(chemicals_address, json=valid_prepared_chemical_2)

    val_purch_chem_id_1 = post_chem_response_1.json["inserted_id"]
    val_purch_chem_id_2 = post_chem_response_2.json["inserted_id"]
    val_prep_chem_id_1 = post_chem_response_3.json["inserted_id"]
    val_prep_chem_id_2 = post_chem_response_4.json["inserted_id"]

    assert post_chem_response_1.status_code == 201
    assert post_chem_response_2.status_code == 201
    assert post_chem_response_3.status_code == 201
    assert post_chem_response_4.status_code == 201

    return val_purch_chem_id_1, val_purch_chem_id_2, val_prep_chem_id_1, val_prep_chem_id_2

def test_update_chemical(
        client,
        post_all_lists,
        post_valid_chemicals,
        valid_purchased_chemical_1,
        valid_purchased_chemical_2,
        valid_prepared_chemical_1,
        valid_prepared_chemical_2,
        purch_chem_1_extra_field,
        purch_chem_2_extra_field,
        prep_chem_1_extra_field,
        prep_chem_2_extra_field,
        purch_chem_1_miss_field_type,
        purch_chem_2_miss_field_type,
        prep_chem_1_miss_field_type,
        prep_chem_2_miss_field_type
    ):

    (val_purch_chem_id_1,
     val_purch_chem_id_2,
     val_prep_chem_id_1,
     val_prep_chem_id_2
     ) = post_valid_chemicals
    
    # Add primary keys and aggregate fields to objects
    # No value sent with aggregate fields should matter as they should be popped off
    valid_purchased_chemical_1[ChemicalSchema.CHEM_ID_KEY] = val_purch_chem_id_1
    valid_purchased_chemical_2[ChemicalSchema.CHEM_ID_KEY] = val_purch_chem_id_2
    valid_prepared_chemical_1[ChemicalSchema.CHEM_ID_KEY] = val_prep_chem_id_1
    valid_prepared_chemical_2[ChemicalSchema.CHEM_ID_KEY] = val_prep_chem_id_2
    valid_purchased_chemical_1[ChemicalSchema.AVAIL_TOTAL_KEY] = 12
    valid_purchased_chemical_2[ChemicalSchema.AVAIL_TOTAL_KEY] = "Huzzah"
    valid_prepared_chemical_1[ChemicalSchema.AVAIL_TOTAL_KEY] = True
    valid_prepared_chemical_2[ChemicalSchema.AVAIL_TOTAL_KEY] = None
    valid_purchased_chemical_1[ChemicalSchema.AVAIL_OPEN_KEY] = 5.56
    valid_purchased_chemical_2[ChemicalSchema.AVAIL_OPEN_KEY] = ("break", "me")
    valid_prepared_chemical_1[ChemicalSchema.AVAIL_OPEN_KEY] = ["if", "you"]
    valid_prepared_chemical_2[ChemicalSchema.AVAIL_OPEN_KEY] = {"dare": 8934868}
    
    # HTTP code 200 testing
    ## Swap valid purchased chemicals with each other and swap valid prepared chemicals with each other.
    
    ### Update keys in objects to match request addresses
    valid_purchased_chemical_1[ChemicalSchema.CHEM_ID_KEY] = val_purch_chem_id_2
    valid_purchased_chemical_2[ChemicalSchema.CHEM_ID_KEY] = val_purch_chem_id_1
    valid_prepared_chemical_1[ChemicalSchema.CHEM_ID_KEY] = val_prep_chem_id_2
    valid_prepared_chemical_2[ChemicalSchema.CHEM_ID_KEY] = val_prep_chem_id_1
    
    put_chem_response_1 = client.put(f"{chemicals_address}/{val_purch_chem_id_1}", json=valid_purchased_chemical_2)
    put_chem_response_2 = client.put(f"{chemicals_address}/{val_purch_chem_id_2}", json=valid_purchased_chemical_1)
    put_chem_response_3 = client.put(f"{chemicals_address}/{val_prep_chem_id_1}", json=valid_prepared_chemical_2)
    put_chem_response_4 = client.put(f"{chemicals_address}/{val_prep_chem_id_2}", json=valid_prepared_chemical_1)
    
    assert put_chem_response_1.status_code == 200
    assert put_chem_response_2.status_code == 200
    assert put_chem_response_3.status_code == 200
    assert put_chem_response_4.status_code == 200

    ## Swap valid purchased chemicals with valid prepared chemicals and vice versa.
    
    ### Updates keys in objects to match request addresses
    valid_purchased_chemical_1[ChemicalSchema.CHEM_ID_KEY] = val_prep_chem_id_2
    valid_purchased_chemical_2[ChemicalSchema.CHEM_ID_KEY] = val_prep_chem_id_1
    valid_prepared_chemical_1[ChemicalSchema.CHEM_ID_KEY] = val_purch_chem_id_2
    valid_prepared_chemical_2[ChemicalSchema.CHEM_ID_KEY] = val_purch_chem_id_1

    put_chem_response_1 = client.put(f"{chemicals_address}/{val_purch_chem_id_1}", json=valid_prepared_chemical_2)
    put_chem_response_2 = client.put(f"{chemicals_address}/{val_purch_chem_id_2}", json=valid_prepared_chemical_1)
    put_chem_response_3 = client.put(f"{chemicals_address}/{val_prep_chem_id_1}", json=valid_purchased_chemical_2)
    put_chem_response_4 = client.put(f"{chemicals_address}/{val_prep_chem_id_2}", json=valid_purchased_chemical_1)

    assert put_chem_response_1.status_code == 200
    assert put_chem_response_2.status_code == 200
    assert put_chem_response_3.status_code == 200
    assert put_chem_response_4.status_code == 200

    ## Reset chemicals for HTTP code 422 testing
    valid_purchased_chemical_1[ChemicalSchema.CHEM_ID_KEY] = val_purch_chem_id_1
    valid_purchased_chemical_2[ChemicalSchema.CHEM_ID_KEY] = val_purch_chem_id_2
    valid_prepared_chemical_1[ChemicalSchema.CHEM_ID_KEY] = val_prep_chem_id_1
    valid_prepared_chemical_2[ChemicalSchema.CHEM_ID_KEY] = val_prep_chem_id_2

    delete_chem_response_1 = client.delete(f"{chemicals_address}/{val_purch_chem_id_1}")
    delete_chem_response_2 = client.delete(f"{chemicals_address}/{val_purch_chem_id_2}")
    delete_chem_response_3 = client.delete(f"{chemicals_address}/{val_prep_chem_id_1}")
    delete_chem_response_4 = client.delete(f"{chemicals_address}/{val_prep_chem_id_2}")

    assert delete_chem_response_1.status_code == 204
    assert delete_chem_response_2.status_code == 204
    assert delete_chem_response_3.status_code == 204
    assert delete_chem_response_4.status_code == 204


    # HTTP Code 400 response body Testing

    ### Test for a request body and address that have matching, invalid primary keys
    #### The end point code is a fail-safe: This case is handled in schema validations and
    #### will return HTTP code 422.


    # HTTP code 404 testing

    ## Test for chemical record existence
    put_chem_response_1 = client.put(f"{chemicals_address}/{val_purch_chem_id_1}", json=valid_purchased_chemical_1)
    put_chem_response_2 = client.put(f"{chemicals_address}/{val_purch_chem_id_2}", json=valid_purchased_chemical_2)
    put_chem_response_3 = client.put(f"{chemicals_address}/{val_prep_chem_id_1}", json=valid_prepared_chemical_1)
    put_chem_response_4 = client.put(f"{chemicals_address}/{val_prep_chem_id_2}", json=valid_prepared_chemical_2)

    data_1 = put_chem_response_1.get_json()
    data_2 = put_chem_response_2.get_json()
    data_3 = put_chem_response_3.get_json()
    data_4 = put_chem_response_4.get_json()

    assert put_chem_response_1.status_code == 404
    assert data_1["error"].startswith(ValidationErrorCodes.CHEM_NOT_FOUND_MSG)
    assert put_chem_response_2.status_code == 404
    assert data_2["error"].startswith(ValidationErrorCodes.CHEM_NOT_FOUND_MSG)
    assert put_chem_response_3.status_code == 404
    assert data_3["error"].startswith(ValidationErrorCodes.CHEM_NOT_FOUND_MSG)
    assert put_chem_response_4.status_code == 404
    assert data_4["error"].startswith(ValidationErrorCodes.CHEM_NOT_FOUND_MSG)

    # HTTP Code 422 response body Testing
    """
    Ensure all valid HTTP requests that fail ChemicalSchema validation return 422
    and the appropriate error message in the request body. Missing field, missing
    value, wrong type, and invalid list entry are handled in test_invalid_chemicals().
    """

    ## Add chemicals back to database
    post_chem_response_1 = client.post(chemicals_address, json=valid_purchased_chemical_1)
    post_chem_response_2 = client.post(chemicals_address, json=valid_purchased_chemical_2)
    post_chem_response_3 = client.post(chemicals_address, json=valid_prepared_chemical_1)
    post_chem_response_4 = client.post(chemicals_address, json=valid_prepared_chemical_2)

    assert post_chem_response_1.status_code == 201
    assert post_chem_response_2.status_code == 201
    assert post_chem_response_3.status_code == 201
    assert post_chem_response_4.status_code == 201

    ## Unexpected fields
    purch_chem_1_extra_field[ChemicalSchema.CHEM_ID_KEY] = val_purch_chem_id_1
    purch_chem_2_extra_field[ChemicalSchema.CHEM_ID_KEY] = val_purch_chem_id_2
    prep_chem_1_extra_field[ChemicalSchema.CHEM_ID_KEY] = val_prep_chem_id_1
    prep_chem_2_extra_field[ChemicalSchema.CHEM_ID_KEY] = val_prep_chem_id_2


    extra_field_chem_response_1 = client.put(f"{chemicals_address}/{val_purch_chem_id_1}", json=purch_chem_1_extra_field)
    extra_field_chem_response_2 = client.put(f"{chemicals_address}/{val_purch_chem_id_2}", json=purch_chem_2_extra_field)
    extra_field_chem_response_3 = client.put(f"{chemicals_address}/{val_prep_chem_id_1}", json=prep_chem_1_extra_field)
    extra_field_chem_response_4 = client.put(f"{chemicals_address}/{val_prep_chem_id_2}", json=prep_chem_2_extra_field)

    data_1 = extra_field_chem_response_1.get_json()
    data_2 = extra_field_chem_response_2.get_json()
    data_3 = extra_field_chem_response_3.get_json()
    data_4 = extra_field_chem_response_4.get_json()

    assert extra_field_chem_response_1.status_code == 422
    assert data_1["error"].startswith(ValidationErrorCodes.UNEXP_FIELD_MSG)
    assert extra_field_chem_response_2.status_code == 422
    assert data_2["error"].startswith(ValidationErrorCodes.UNEXP_FIELD_MSG)
    assert extra_field_chem_response_3.status_code == 422
    assert data_3["error"].startswith(ValidationErrorCodes.UNEXP_FIELD_MSG)
    assert extra_field_chem_response_4.status_code == 422
    assert data_4["error"].startswith(ValidationErrorCodes.UNEXP_FIELD_MSG)

    ## Multiple errors should return the first-encountered error (control flow testing)
    purch_chem_1_miss_field_type[ChemicalSchema.CHEM_ID_KEY] = val_purch_chem_id_1
    purch_chem_2_miss_field_type[ChemicalSchema.CHEM_ID_KEY] = val_purch_chem_id_2
    prep_chem_1_miss_field_type[ChemicalSchema.CHEM_ID_KEY] = val_prep_chem_id_1
    prep_chem_2_miss_field_type[ChemicalSchema.CHEM_ID_KEY] = val_prep_chem_id_2

    miss_field_type_response_1 = client.put(f"{chemicals_address}/{val_purch_chem_id_1}", json=purch_chem_1_miss_field_type)
    miss_field_type_response_2 = client.put(f"{chemicals_address}/{val_purch_chem_id_2}", json=purch_chem_2_miss_field_type)
    miss_field_type_response_3 = client.put(f"{chemicals_address}/{val_prep_chem_id_1}", json=prep_chem_1_miss_field_type)
    miss_field_type_response_4 = client.put(f"{chemicals_address}/{val_prep_chem_id_2}", json=prep_chem_2_miss_field_type)

    data_1 = miss_field_type_response_1.get_json()
    data_2 = miss_field_type_response_2.get_json()
    data_3 = miss_field_type_response_3.get_json()
    data_4 = miss_field_type_response_4.get_json()

    assert miss_field_type_response_1.status_code == 422
    assert data_1["error"].startswith(ValidationErrorCodes.MISS_REQ_FIELD_MSG)
    assert miss_field_type_response_2.status_code == 422
    assert data_2["error"].startswith(ValidationErrorCodes.MISS_REQ_FIELD_MSG)
    assert miss_field_type_response_3.status_code == 422
    assert data_3["error"].startswith(ValidationErrorCodes.MISS_REQ_FIELD_MSG)
    assert miss_field_type_response_4.status_code == 422
    assert data_4["error"].startswith(ValidationErrorCodes.MISS_REQ_FIELD_MSG)

    ## Invalid _id format
    ### Test that request bodies without a primary key are caught (also catches empty request bodies)
    miss_prim_key_req = copy.deepcopy(valid_purchased_chemical_1)
    miss_prim_key_req.pop(ChemicalSchema.CHEM_ID_KEY)
    
    miss_prim_key_response = client.put(f"{chemicals_address}/{val_purch_chem_id_1}", json=miss_prim_key_req)
    data = miss_prim_key_response.get_json()

    assert miss_prim_key_response.status_code == 422
    assert data["error"].startswith("Request body missing primary key:")

    ### Test that primary keys in address and body match each other
    mismatch_id_response_1 = client.put(f"{chemicals_address}/1", json=valid_purchased_chemical_1)
    data = mismatch_id_response_1.get_json()

    assert mismatch_id_response_1.status_code == 422
    assert data["error"].startswith("Request body primary key does not match address <chemical_id>:")

    ### Test for a request body and address that have matching, invalid primary keys
    malformed_prim_key_req = copy.deepcopy(valid_purchased_chemical_1)
    malformed_prim_key_req[ChemicalSchema.CHEM_ID_KEY] = "1"
    
    malformed_prim_key_response = client.put(f"{chemicals_address}/1", json=malformed_prim_key_req)
    data = malformed_prim_key_response.get_json()

    assert malformed_prim_key_response.status_code == 422
    assert data["error"].startswith(ValidationErrorCodes.INVALID_ID_MSG)


# Remaining 422 status code testing
def test_invalid_chemicals(
    client,
    post_all_lists,
    post_valid_chemicals,
    invalid_chemicals
):
    ## Missing fields, missing values, wrong types, and invalid list entries
    ## Testing all internal schema validation failures against all combinations of
    ## update between purchased and prepared reagents.
    (val_purch_chem_id_1,
     val_purch_chem_id_2,
     val_prep_chem_id_1,
     val_prep_chem_id_2
     ) = post_valid_chemicals
    
    for payload, expected_error_prefix in invalid_chemicals:
        # Add primary keys and aggregate fields to objects
        ## No value sent with aggregate fields should matter as they should be popped off
        id_append_val_purch_chem_1 = copy.deepcopy(payload)
        id_append_val_purch_chem_2 = copy.deepcopy(payload)
        id_append_val_prep_chem_1 = copy.deepcopy(payload)
        id_append_val_prep_chem_2 = copy.deepcopy(payload)
        id_append_val_purch_chem_1[ChemicalSchema.CHEM_ID_KEY] = val_purch_chem_id_1
        id_append_val_purch_chem_2[ChemicalSchema.CHEM_ID_KEY] = val_purch_chem_id_2
        id_append_val_prep_chem_1[ChemicalSchema.CHEM_ID_KEY] = val_prep_chem_id_1
        id_append_val_prep_chem_2[ChemicalSchema.CHEM_ID_KEY] = val_prep_chem_id_2
        id_append_val_purch_chem_1[ChemicalSchema.AVAIL_TOTAL_KEY] = 12
        id_append_val_purch_chem_2[ChemicalSchema.AVAIL_TOTAL_KEY] = "Huzzah"
        id_append_val_prep_chem_1[ChemicalSchema.AVAIL_TOTAL_KEY] = True
        id_append_val_prep_chem_2[ChemicalSchema.AVAIL_TOTAL_KEY] = None
        id_append_val_purch_chem_1[ChemicalSchema.AVAIL_OPEN_KEY] = 5.56
        id_append_val_purch_chem_2[ChemicalSchema.AVAIL_OPEN_KEY] = ("break", "me")
        id_append_val_prep_chem_1[ChemicalSchema.AVAIL_OPEN_KEY] = ["if", "you"]
        id_append_val_prep_chem_2[ChemicalSchema.AVAIL_OPEN_KEY] = {"dare": 8934868}

        # Test payloads
        val_purch_chem_1_response = client.put(f"{chemicals_address}/{val_purch_chem_id_1}", json=copy.deepcopy(id_append_val_purch_chem_1))
        val_purch_chem_2_response = client.put(f"{chemicals_address}/{val_purch_chem_id_2}", json=copy.deepcopy(id_append_val_purch_chem_2))
        val_prep_chem_1_response = client.put(f"{chemicals_address}/{val_prep_chem_id_1}", json=copy.deepcopy(id_append_val_prep_chem_1))
        val_prep_chem_2_response = client.put(f"{chemicals_address}/{val_prep_chem_id_2}", json=copy.deepcopy(id_append_val_prep_chem_2))

        val_purch_chem_1_data = val_purch_chem_1_response.get_json()
        val_purch_chem_2_data = val_purch_chem_2_response.get_json()
        val_prep_chem_1_data = val_prep_chem_1_response.get_json()
        val_prep_chem_2_data = val_prep_chem_2_response.get_json()

        if not val_purch_chem_1_data["error"].startswith(str(expected_error_prefix)):
            print(f"Payload: {payload}")
            print(f"Expected error: {expected_error_prefix}")
            print(f"Returned error: {val_purch_chem_1_data['error']}")
        assert val_purch_chem_1_data["error"].startswith(str(expected_error_prefix))
        assert val_purch_chem_1_response.status_code == 422

        if not val_purch_chem_2_data["error"].startswith(str(expected_error_prefix)):
            print(f"Payload: {payload}")
            print(f"Expected error: {expected_error_prefix}")
            print(f"Returned error: {val_purch_chem_2_data['error']}")
        assert val_purch_chem_2_data["error"].startswith(str(expected_error_prefix))
        assert val_purch_chem_2_response.status_code == 422

        if not val_prep_chem_1_data["error"].startswith(str(expected_error_prefix)):
            print(f"Payload: {payload}")
            print(f"Expected error: {expected_error_prefix}")
            print(f"Returned error: {val_prep_chem_1_data['error']}")
        assert val_prep_chem_1_data["error"].startswith(str(expected_error_prefix))
        assert val_prep_chem_1_response.status_code == 422

        if not val_prep_chem_2_data["error"].startswith(str(expected_error_prefix)):
            print(f"Payload: {payload}")
            print(f"Expected error: {expected_error_prefix}")
            print(f"Returned error: {val_prep_chem_2_data['error']}")
        assert val_prep_chem_2_data["error"].startswith(str(expected_error_prefix))
        assert val_prep_chem_2_response.status_code == 422