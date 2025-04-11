from app.models.lists import ListsSchema

lists_address = "/lists"

def test_delete_list(client):
    # Validated lists
    classifications = {f"{ListsSchema.LIST_NAME_KEY}": ListsSchema.CLASSIF_LIST_KEY(), f"{ListsSchema.LIST_ENT_KEY}": ["Flammable solvent", "Strong acid", "Weak acid", "Strong base", "Weak base", "Mobile phase", "Reagent", "Standard", "Solid", "Dewer", "Gas cylinder", "Water", "Water Dispenser"]}
    container_types = {f"{ListsSchema.LIST_NAME_KEY}": ListsSchema.CONT_TYPES_LIST_KEY(), f"{ListsSchema.LIST_ENT_KEY}": ["Ampoule", "Autosampler vial", "Bottle", "Vial", "Instrument", "N/A"]}
    manufacturers = {f"{ListsSchema.LIST_NAME_KEY}": ListsSchema.MANU_LIST_KEY(), f"{ListsSchema.LIST_ENT_KEY}": ["3M", "Agilent", "Alfa Aesar", "Eppendorf", "Fisher Scientific", "Honeywell", "J.T. Baker", "Milli-Q", "Sigma-Aldrich", "Thermo Fisher Scientific", "VWR"]}
    sources = {f"{ListsSchema.LIST_NAME_KEY}": ListsSchema.SOURCES_LIST_KEY(), f"{ListsSchema.LIST_ENT_KEY}": ["Purchased", "Prepared"]}
    storage_conditions = {f"{ListsSchema.LIST_NAME_KEY}": ListsSchema.STOR_COND_LIST_KEY(), f"{ListsSchema.LIST_ENT_KEY}": ["-80 °C", "-20 °C", "2-8 °C", "Ambient", "Ambient, dark", "Room temperature"]}
    units = {f"{ListsSchema.LIST_NAME_KEY}": ListsSchema.UNITS_LIST_KEY(), f"{ListsSchema.LIST_ENT_KEY}": ["g", "kg", "L", "mL", "µL", "N/A"]}

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

    # Retreive primary keys ("Name"; MongoDB's "_id" not used for this collection)
    list_names = [record["Name"] for record in client.get(lists_address).get_json()]

    # Remove lists and confirm success
    delete_reponse_1 = client.delete(f"{lists_address}/{list_names[0]}")
    delete_reponse_2 = client.delete(f"{lists_address}/{list_names[1]}")
    delete_reponse_3 = client.delete(f"{lists_address}/{list_names[2]}")
    delete_reponse_4 = client.delete(f"{lists_address}/{list_names[3]}")
    delete_reponse_5 = client.delete(f"{lists_address}/{list_names[4]}")
    delete_reponse_6 = client.delete(f"{lists_address}/{list_names[5]}")

    assert delete_reponse_1.status_code == 204
    assert delete_reponse_2.status_code == 204
    assert delete_reponse_3.status_code == 204
    assert delete_reponse_4.status_code == 204
    assert delete_reponse_5.status_code == 204
    assert delete_reponse_6.status_code == 204

    # Confirm DELETE requests for missing lists return 404
    bad_delete_reponse_1 = client.delete(f"{lists_address}/{list_names[0]}")
    bad_delete_reponse_2 = client.delete(f"{lists_address}/{list_names[1]}")
    bad_delete_reponse_3 = client.delete(f"{lists_address}/{list_names[2]}")
    bad_delete_reponse_4 = client.delete(f"{lists_address}/{list_names[3]}")
    bad_delete_reponse_5 = client.delete(f"{lists_address}/{list_names[4]}")
    bad_delete_reponse_6 = client.delete(f"{lists_address}/{list_names[5]}")
    
    assert bad_delete_reponse_1.status_code == 404
    assert bad_delete_reponse_2.status_code == 404
    assert bad_delete_reponse_3.status_code == 404
    assert bad_delete_reponse_4.status_code == 404
    assert bad_delete_reponse_5.status_code == 404
    assert bad_delete_reponse_6.status_code == 404
