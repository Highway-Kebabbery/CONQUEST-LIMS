from chemical_inventory_api_v1 import ChemicalSchema, ListsSchema

chemicals_address = "/chemicals"

def test_get_chemical(
        client,
        post_all_lists,
        valid_purchased_chemical_1,
        valid_purchased_chemical_2,
        valid_prepared_chemical_1,
        valid_prepared_chemical_2
        ):

    # POST valid chemicals of all types and confirm success
    post_chem_response_1 = client.post(chemical_address, json=valid_purchased_chemical_1)
    post_chem_response_2 = client.post(chemical_address, json=valid_purchased_chemical_2)
    post_chem_response_3 = client.post(chemical_address, json=valid_prepared_chemical_1)
    post_chem_response_4 = client.post(chemical_address, json=valid_prepared_chemical_2)

    assert post_chem_response_1.status_code == 201
    assert post_chem_response_2.status_code == 201
    assert post_chem_response_3.status_code == 201
    assert post_chem_response_4.status_code == 201

    purchased_chem_id_1 = post_chem_response_1.json["inserted_id"]
    purchased_chem_id_2 = post_chem_response_2.json["inserted_id"]
    prepared_chem_id_1 = post_chem_response_3.json["inserted_id"]
    prepared_chem_id_2 = post_chem_response_4.json["inserted_id"]

    # GET chemicals and confirm success
    get_reponse_1 = client.get(f"{chemical_address}/{purchased_chem_id_1}")
    get_reponse_2 = client.get(f"{chemical_address}/{purchased_chem_id_2}")
    get_reponse_3 = client.get(f"{chemical_address}/{prepared_chem_id_1}")
    get_reponse_4 = client.get(f"{chemical_address}/{prepared_chem_id_2}")
    
    assert get_reponse_1.status_code == 200
    assert get_reponse_2.status_code == 200
    assert get_reponse_3.status_code == 200
    assert get_reponse_4.status_code == 200

    # Remove chemicals and confirm GET requests for removed chemicals return 404
    delete_reponse_1 = client.delete(f"{chemical_address}/{purchased_chem_id_1}")
    delete_reponse_2 = client.delete(f"{chemical_address}/{purchased_chem_id_2}")
    delete_reponse_3 = client.delete(f"{chemical_address}/{prepared_chem_id_1}")
    delete_reponse_4 = client.delete(f"{chemical_address}/{prepared_chem_id_2}")

    assert delete_reponse_1.status_code == 204
    assert delete_reponse_2.status_code == 204
    assert delete_reponse_3.status_code == 204
    assert delete_reponse_4.status_code == 204

    bad_get_reponse_1 = client.get(f"{chemical_address}/{purchased_chem_id_1}")
    bad_get_reponse_2 = client.get(f"{chemical_address}/{purchased_chem_id_2}")
    bad_get_reponse_3 = client.get(f"{chemical_address}/{prepared_chem_id_1}")
    bad_get_reponse_4 = client.get(f"{chemical_address}/{prepared_chem_id_2}")
    
    assert bad_get_reponse_1.status_code == 404
    assert bad_get_reponse_2.status_code == 404
    assert bad_get_reponse_3.status_code == 404
    assert bad_get_reponse_4.status_code == 404

    # Confirm that GET requests with malformed ObjectId return 400
    invalid_id_response_1 = client.get(f"{chemicals_address}/1")

    assert invalid_id_response_1.status_code == 400