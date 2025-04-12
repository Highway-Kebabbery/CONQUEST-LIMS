"""
See tests/chemicals/conftest.py for a detailed overview of the chemicals 
testing strategy. See docs/specification.md for a comprehensive view of system 
integration testing.
"""
import copy
from app.utils.validation_error_codes import ValidationErrorCodes

chemicals_address = "/chemicals"

def test_add_chemical(
        client,
        post_all_lists,
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

    # HTTP code 201 testing

    post_chem_response_1 = client.post(chemicals_address, json=valid_purchased_chemical_1)
    post_chem_response_2 = client.post(chemicals_address, json=valid_purchased_chemical_2)
    post_chem_response_3 = client.post(chemicals_address, json=valid_prepared_chemical_1)
    post_chem_response_4 = client.post(chemicals_address, json=valid_prepared_chemical_2)

    assert post_chem_response_1.status_code == 201
    assert post_chem_response_2.status_code == 201
    assert post_chem_response_3.status_code == 201
    assert post_chem_response_4.status_code == 201

    
    # HTTP Code 400 response body testing

    ## Confirm POST requests with empty body return 400
    empty_request_body = {}
    empty_body_reponse = client.post(chemicals_address, json=empty_request_body)

    assert empty_body_reponse.status_code == 400



    # HTTP code 422 response body Testing
    """
    Ensure all valid HTTP requests that fail ChemicalSchema validation return 422
    and the appropriate error message in the request body. Missing field, missing
    value, wrong type, and invalid list entry are handled in test_invalid_chemicals().
    """

    ## Chemical duplicate
    post_chem_dup_response_purch_1 = client.post(chemicals_address, json=valid_purchased_chemical_1)
    post_chem_dup_response_purch_2 = client.post(chemicals_address, json=valid_purchased_chemical_2)
    post_chem_dup_response_prep_1 = client.post(chemicals_address, json=valid_prepared_chemical_1)
    post_chem_dup_response_prep_2 = client.post(chemicals_address, json=valid_prepared_chemical_2)

    data_1 = post_chem_dup_response_purch_1.get_json()
    data_2 = post_chem_dup_response_purch_2.get_json()
    data_3 = post_chem_dup_response_prep_1.get_json()
    data_4 = post_chem_dup_response_prep_2.get_json()

    assert post_chem_dup_response_purch_1.status_code == 422
    assert data_1["error"].startswith(ValidationErrorCodes.CHEM_DUPLICATE_MSG)
    assert post_chem_dup_response_purch_2.status_code == 422
    assert data_2["error"].startswith(ValidationErrorCodes.CHEM_DUPLICATE_MSG)
    assert post_chem_dup_response_prep_1.status_code == 422
    assert data_3["error"].startswith(ValidationErrorCodes.CHEM_DUPLICATE_MSG)
    assert post_chem_dup_response_prep_2.status_code == 422
    assert data_4["error"].startswith(ValidationErrorCodes.CHEM_DUPLICATE_MSG)

    ## Unexpected fields
    extra_field_chem_response_1 = client.post(chemicals_address, json=purch_chem_1_extra_field)
    extra_field_chem_response_2 = client.post(chemicals_address, json=purch_chem_2_extra_field)
    extra_field_chem_response_3= client.post(chemicals_address, json=prep_chem_1_extra_field)
    extra_field_chem_response_4= client.post(chemicals_address, json=prep_chem_2_extra_field)

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
    miss_field_type_response_1 = client.post(chemicals_address, json=purch_chem_1_miss_field_type)
    miss_field_type_response_2 = client.post(chemicals_address, json=purch_chem_2_miss_field_type)
    miss_field_type_response_3 = client.post(chemicals_address, json=prep_chem_1_miss_field_type)
    miss_field_type_response_4 = client.post(chemicals_address, json=prep_chem_2_miss_field_type)

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
    

# Remaining 422 status code testing:
def test_add_invalid_chemicals(
    client,
    post_all_lists,
    invalid_chemicals
):
    ## Missing fields, missing values, wrong types, and invalid list entries
    for payload, expected_error_prefix in invalid_chemicals:    
        response = client.post(chemicals_address, json=copy.deepcopy(payload))
        data = response.get_json()

        if not data["error"].startswith(str(expected_error_prefix)):
            print(f"Payload: {payload}")
            print(f"Expected error: {expected_error_prefix}")
            print(f"Returned error: {data['error']}")
        assert data["error"].startswith(str(expected_error_prefix))
        assert response.status_code == 422
