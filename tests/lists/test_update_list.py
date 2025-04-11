import pytest, copy

from app.utils.validation_error_codes import ValidationErrorCodes
from app.models.lists import ListsSchema

# Validated lists
classifications = {f"{ListsSchema.LIST_NAME_KEY}": ListsSchema.CLASSIF_LIST_KEY(), f"{ListsSchema.LIST_ENT_KEY}": ["Flammable solvent", "Strong acid", "Weak acid", "Strong base", "Weak base", "Mobile phase", "Reagent", "Standard", "Solid", "Dewer", "Gas cylinder", "Water", "Water Dispenser"]}
container_types = {f"{ListsSchema.LIST_NAME_KEY}": ListsSchema.CONT_TYPES_LIST_KEY(), f"{ListsSchema.LIST_ENT_KEY}": ["Ampoule", "Autosampler vial", "Bottle", "Vial", "Instrument", "N/A"]}
manufacturers = {f"{ListsSchema.LIST_NAME_KEY}": ListsSchema.MANU_LIST_KEY(), f"{ListsSchema.LIST_ENT_KEY}": ["3M", "Agilent", "Alfa Aesar", "Eppendorf", "Fisher Scientific", "Honeywell", "J.T. Baker", "Milli-Q", "Sigma-Aldrich", "Thermo Fisher Scientific", "VWR"]}
sources = {f"{ListsSchema.LIST_NAME_KEY}": ListsSchema.SOURCES_LIST_KEY(), f"{ListsSchema.LIST_ENT_KEY}": ["Purchased", "Prepared"]}
storage_conditions = {f"{ListsSchema.LIST_NAME_KEY}": ListsSchema.STOR_COND_LIST_KEY(), f"{ListsSchema.LIST_ENT_KEY}": ["-80 °C", "-20 °C", "2-8 °C", "Ambient", "Ambient, dark", "Room temperature"]}
units = {f"{ListsSchema.LIST_NAME_KEY}": ListsSchema.UNITS_LIST_KEY(), f"{ListsSchema.LIST_ENT_KEY}": ["g", "kg", "L", "mL", "µL", "N/A"]}


miss_field_name = copy.deepcopy(classifications)
miss_field_name.pop(ListsSchema.LIST_NAME_KEY)

miss_field_entries = copy.deepcopy(classifications)
miss_field_entries.pop(ListsSchema.LIST_ENT_KEY)

miss_value_name = copy.deepcopy(classifications)
miss_value_name[ListsSchema.LIST_NAME_KEY] = None

miss_value_entries = copy.deepcopy(classifications)
miss_value_entries[ListsSchema.LIST_ENT_KEY] = None

type_name = copy.deepcopy(classifications)
type_name[ListsSchema.LIST_NAME_KEY] = True

type_entries = copy.deepcopy(classifications)
type_entries[ListsSchema.LIST_ENT_KEY] = True

type_entries_values = copy.deepcopy(classifications)
type_entries_values[ListsSchema.LIST_ENT_KEY][3] = 1.68

extra_field = copy.deepcopy(classifications)
extra_field["foo"] = "bar"
extra_field["fizz"] = "buzz"

type_miss_field = copy.deepcopy(classifications)
type_miss_field[ListsSchema.LIST_NAME_KEY] = 1
type_miss_field.pop(ListsSchema.LIST_ENT_KEY)

invalid_lists = [
    (miss_field_name, "Request body missing primary key:"),
    (miss_field_entries, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (miss_value_name, "Request body primary key does not match address <list_name>:"),
    (miss_value_entries, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (type_name, "Request body primary key does not match address <list_name>:"),
    (type_entries, ValidationErrorCodes.WRONG_TYPE_MSG),
    (type_entries_values, ValidationErrorCodes.WRONG_TYPE_MSG),
    (extra_field, ValidationErrorCodes.UNEXP_FIELD_MSG)
]

lists_address = "/lists"

@pytest.fixture()
def post_valid_lists(client):
    # POST valid lists and confirm success. Returns primary keys.
    post_list_response_1 = client.post(lists_address, json=classifications)
    post_list_response_2 = client.post(lists_address, json=container_types)
    post_list_response_3 = client.post(lists_address, json=manufacturers)
    post_list_response_4 = client.post(lists_address, json=sources)
    post_list_response_5 = client.post(lists_address, json=storage_conditions)
    post_list_response_6 = client.post(lists_address, json=units)
    
    assert post_list_response_1.status_code == 201
    assert post_list_response_2.status_code == 201
    assert post_list_response_3.status_code == 201
    assert post_list_response_4.status_code == 201
    assert post_list_response_5.status_code == 201
    assert post_list_response_6.status_code == 201

    ## Retreive primary keys ("Name"; MongoDB's "_id" not used for this collection)
    ## Depends on records being returned in order of creation... which they are.
    list_names = [record["Name"] for record in client.get(lists_address).get_json()]
    return list_names

def test_update_list(client, post_valid_lists):
    # HTTP code 200 testing
    ## Swap valid lists with each other

    list_names = post_valid_lists
    
    ### Update keys in objects to match request address
    classifications[ListsSchema.LIST_NAME_KEY] = list_names[5]
    container_types[ListsSchema.LIST_NAME_KEY] = list_names[4]
    manufacturers[ListsSchema.LIST_NAME_KEY] = list_names[3]
    sources[ListsSchema.LIST_NAME_KEY] = list_names[2]
    storage_conditions[ListsSchema.LIST_NAME_KEY] = list_names[1]
    units[ListsSchema.LIST_NAME_KEY] = list_names[0]
    
    put_list_response_1 = client.put(f"{lists_address}/{list_names[5]}", json=classifications)
    put_list_response_2 = client.put(f"{lists_address}/{list_names[4]}", json=container_types)
    put_list_response_3 = client.put(f"{lists_address}/{list_names[3]}", json=manufacturers)
    put_list_response_4 = client.put(f"{lists_address}/{list_names[2]}", json=sources)
    put_list_response_5 = client.put(f"{lists_address}/{list_names[1]}", json=storage_conditions)
    put_list_response_6 = client.put(f"{lists_address}/{list_names[0]}", json=units)

    assert put_list_response_1.status_code == 200
    assert put_list_response_2.status_code == 200
    assert put_list_response_3.status_code == 200
    assert put_list_response_4.status_code == 200
    assert put_list_response_5.status_code == 200
    assert put_list_response_6.status_code == 200

    ## Reset lists for HTTP code 422 testing
    classifications[ListsSchema.LIST_NAME_KEY] = list_names[0]
    container_types[ListsSchema.LIST_NAME_KEY] = list_names[1]
    manufacturers[ListsSchema.LIST_NAME_KEY] = list_names[2]
    sources[ListsSchema.LIST_NAME_KEY] = list_names[3]
    storage_conditions[ListsSchema.LIST_NAME_KEY] = list_names[4]
    units[ListsSchema.LIST_NAME_KEY] = list_names[5]

    delete_list_response_1 = client.delete(f"{lists_address}/{list_names[5]}", json=classifications)
    delete_list_response_2 = client.delete(f"{lists_address}/{list_names[4]}", json=container_types)
    delete_list_response_3 = client.delete(f"{lists_address}/{list_names[3]}", json=manufacturers)
    delete_list_response_4 = client.delete(f"{lists_address}/{list_names[2]}", json=sources)
    delete_list_response_5 = client.delete(f"{lists_address}/{list_names[1]}", json=storage_conditions)
    delete_list_response_6 = client.delete(f"{lists_address}/{list_names[0]}", json=units)

    assert delete_list_response_1.status_code == 204
    assert delete_list_response_2.status_code == 204
    assert delete_list_response_3.status_code == 204
    assert delete_list_response_4.status_code == 204
    assert delete_list_response_5.status_code == 204
    assert delete_list_response_6.status_code == 204


    # HTTP code 404 testing

    ## Check that list exists to be updated
    put_list_response_1 = client.put(f"{lists_address}/{list_names[0]}", json=classifications)
    put_list_response_2 = client.put(f"{lists_address}/{list_names[1]}", json=container_types)
    put_list_response_3 = client.put(f"{lists_address}/{list_names[2]}", json=manufacturers)
    put_list_response_4 = client.put(f"{lists_address}/{list_names[3]}", json=sources)
    put_list_response_5 = client.put(f"{lists_address}/{list_names[4]}", json=storage_conditions)
    put_list_response_6 = client.put(f"{lists_address}/{list_names[5]}", json=units)

    data_1 = put_list_response_1.get_json()
    data_2 = put_list_response_2.get_json()
    data_3 = put_list_response_3.get_json()
    data_4 = put_list_response_4.get_json()
    data_5 = put_list_response_5.get_json()
    data_6 = put_list_response_6.get_json()

    assert put_list_response_1.status_code == 404
    assert data_1["error"].startswith(ValidationErrorCodes.LIST_NOT_FOUND_MSG)
    assert put_list_response_2.status_code == 404
    assert data_2["error"].startswith(ValidationErrorCodes.LIST_NOT_FOUND_MSG)
    assert put_list_response_3.status_code == 404
    assert data_3["error"].startswith(ValidationErrorCodes.LIST_NOT_FOUND_MSG)
    assert put_list_response_4.status_code == 404
    assert data_4["error"].startswith(ValidationErrorCodes.LIST_NOT_FOUND_MSG)
    assert put_list_response_5.status_code == 404
    assert data_5["error"].startswith(ValidationErrorCodes.LIST_NOT_FOUND_MSG)
    assert put_list_response_6.status_code == 404
    assert data_6["error"].startswith(ValidationErrorCodes.LIST_NOT_FOUND_MSG)

    # HTTP code 422 response body testing
    """
    Ensure all valid HTTP requests that fail ListSchema validation return 422
    and the appropriate error message in the request body.
    """

    ## Multiple errors should return the first-encountered error (control flow testing)
    ### This... is hard to test given that lists have two fields, one of which is the
    ### primary key "Name". Any mutation to Name should really trigger a primary key
    ### error in the end point.
    type_miss_field_response = client.put(f"{lists_address}/{type_miss_field[ListsSchema.LIST_NAME_KEY]}", json=type_miss_field)
    data = type_miss_field_response.get_json()

    assert type_miss_field_response.status_code == 422
    assert data["error"].startswith("Request body primary key does not match address <list_name>:")

    ## Invalid _id format
    ### Test that request bodies without a primary key are caught (also catches empty request bodies)
    miss_prim_key_req = copy.deepcopy(classifications)
    miss_prim_key_req.pop(ListsSchema.LIST_NAME_KEY)
    
    miss_prim_key_response = client.put(f"{lists_address}/{list_names[0]}", json=miss_prim_key_req)
    data = miss_prim_key_response.get_json()

    assert miss_prim_key_response.status_code == 422
    assert data["error"].startswith("Request body missing primary key:")

    ### Test that primary keys in address and body match each other
    mismatch_id_response_1 = client.put(f"{lists_address}/1", json=classifications)
    data = mismatch_id_response_1.get_json()

    assert mismatch_id_response_1.status_code == 422
    assert data["error"].startswith("Request body primary key does not match address <list_name>:")


# Remaining HTTP code 422 tests
## Missing required fields, missing required values, wrong types, unexpected fields.
## Lists only have one general schema, so only one list is tested against invalid data
@pytest.mark.parametrize("payload, expected_error_prefix", invalid_lists)
def test_add_invalid_lists(client, payload, expected_error_prefix, post_valid_lists):
    list_names = post_valid_lists

    response = client.put(f"{lists_address}/{list_names[0]}", json=copy.deepcopy(payload))
    data = response.get_json()

    if not data["error"].startswith(str(expected_error_prefix)):
        print(f"Payload: {payload}")
        print(f"Expected error: {expected_error_prefix}")
        print(f"Returned error: {data['error']}")
    assert data["error"].startswith(str(expected_error_prefix))
    assert response.status_code == 422