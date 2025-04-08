from chemical_inventory_api_v1 import ListsSchema, ValidationErrorCodes
import pytest, copy

# Validated lists
classifications = {f"{ListsSchema.LIST_NAME_KEY}": ListsSchema.CLASSIF_LIST_KEY(), f"{ListsSchema.LIST_ENT_KEY}": ["Flammable solvent", "Strong acid", "Weak acid", "Strong base", "Weak base", "Mobile phase", "Reagent", "Standard", "Solid", "Dewer", "Gas cylinder", "Water", "Water Dispenser"]}
container_types = {f"{ListsSchema.LIST_NAME_KEY}": ListsSchema.CONT_TYPES_LIST_KEY(), f"{ListsSchema.LIST_ENT_KEY}": ["Ampoule", "Autosampler vial", "Bottle", "Vial", "N/A"]}
manufacturers = {f"{ListsSchema.LIST_NAME_KEY}": ListsSchema.MANU_LIST_KEY(), f"{ListsSchema.LIST_ENT_KEY}": ["3M", "Agilent", "Alfa Aesar", "Eppendorf", "Fisher Scientific", "Honeywell", "J.T. Baker", "Milli-Q", "Sigma-Aldrich", "Thermo Fisher Scientific", "VWR"]}
sources = {f"{ListsSchema.LIST_NAME_KEY}": ListsSchema.SOURCES_LIST_KEY(), f"{ListsSchema.LIST_ENT_KEY}": ["Purchased", "Prepared"]}
storage_conditions = {f"{ListsSchema.LIST_NAME_KEY}": ListsSchema.STOR_COND_LIST_KEY(), f"{ListsSchema.LIST_ENT_KEY}": ["-80 °C", "-20 °C", "2-8 °C", "Ambient", "Ambient, dark", "Room temperature"]}
units = {f"{ListsSchema.LIST_NAME_KEY}": ListsSchema.UNITS_LIST_KEY(), f"{ListsSchema.LIST_ENT_KEY}": ["g", "kg", "L", "mL", "µL", "N/A"]}


miss_field_name = copy.deepcopy(classifications)
miss_field_name.pop(ListsSchema.LIST_NAME_KEY)

miss_field_entries = copy.deepcopy(classifications)
miss_field_entries.pop(ListsSchema.LIST_NAME_KEY)

miss_value_name = copy.deepcopy(classifications)
miss_value_name[ListsSchema.LIST_ENT_KEY] = None

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

miss_field_type = copy.deepcopy(classifications)
miss_field_type.pop(ListsSchema.LIST_NAME_KEY)
miss_field_type[ListsSchema.LIST_ENT_KEY][3] = 1

invalid_lists = [
    (miss_field_name, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (miss_field_entries, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (miss_value_name, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (miss_value_entries, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (type_name, ValidationErrorCodes.WRONG_TYPE_MSG),
    (type_entries, ValidationErrorCodes.WRONG_TYPE_MSG),
    (type_entries_values, ValidationErrorCodes.WRONG_TYPE_MSG),
    (extra_field, ValidationErrorCodes.UNEXP_FIELD_MSG)
]

lists_address = "/lists"

def test_add_list(client):
    # POST valid lists and confirm success
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


    # HTTP Code 400 response body testing
    ## Confirm POST requests with empty body return 400
    empty_request_body = {}
    empty_body_reponse = client.post(lists_address, json=empty_request_body)

    assert empty_body_reponse.status_code == 400


    # HTTP code 422 response body testing
    """
    Ensure all valid HTTP requests that fail ListSchema validation return 422
    and the appropriate error message in the request body.
    """

    ## Check that duplicate list names aren't allowed
    post_list_response_1 = client.post(f"{lists_address}", json=classifications)
    data = post_list_response_1.get_json()

    assert post_list_response_1.status_code == 422
    assert data["error"].startswith(ValidationErrorCodes.LIST_DUPLICATE_MSG)

    ## Multiple errors should return the first-encountered error (control flow testing)
    miss_field_type_response = client.post(f"{lists_address}", json=miss_field_type)
    data = miss_field_type_response.get_json()

    assert miss_field_type_response.status_code == 422
    assert data["error"].startswith(ValidationErrorCodes.MISS_REQ_FIELD_MSG)


# Remaining HTTP code 422 tests
## Missing required fields, missing required values, wrong types, unexpected fields
@pytest.mark.parametrize("payload, expected_error_prefix", invalid_lists)
def test_add_invalid_lists(client, payload, expected_error_prefix):
    response = client.post(lists_address, json=copy.deepcopy(payload))
    data = response.get_json()

    assert response.status_code == 422
    if not data["error"].startswith(str(expected_error_prefix)):
        print(f"Payload: {payload}")
        print(f"Expected error: {expected_error_prefix}")
        print(f"Returned error: {data['error']}")
    assert data["error"].startswith(str(expected_error_prefix))