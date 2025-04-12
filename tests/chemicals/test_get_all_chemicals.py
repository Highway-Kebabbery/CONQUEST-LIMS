"""
See tests/chemicals/conftest.py for a detailed overview of the chemicals 
testing schstrategyema. See docs/specification.md for a comprehensive view of system 
integration testing.
"""
chemicals_address = "/chemicals"

def test_get_all_chemicals(
        client,
        post_all_lists,
        valid_purchased_chemical_1,
        valid_purchased_chemical_2,
        valid_prepared_chemical_1,
        valid_prepared_chemical_2
        ):

    # POST valid chemicals of all types and confirm success
    post_chem_response_1 = client.post(chemicals_address, json=valid_purchased_chemical_1)
    post_chem_response_2 = client.post(chemicals_address, json=valid_purchased_chemical_2)
    post_chem_response_3 = client.post(chemicals_address, json=valid_prepared_chemical_1)
    post_chem_response_4 = client.post(chemicals_address, json=valid_prepared_chemical_2)
    
    assert post_chem_response_1.status_code == 201
    assert post_chem_response_2.status_code == 201
    assert post_chem_response_3.status_code == 201
    assert post_chem_response_4.status_code == 201

    # GET chemicals and confirm success
    get_reponse_1 = client.get(chemicals_address)
    
    assert get_reponse_1.status_code == 200