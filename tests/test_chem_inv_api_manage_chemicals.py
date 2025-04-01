def test_manage_general_chemicals(client):
    test_good_chemical = {
        "Name": "Methanol (Certified ACS), Fisher Chemical",
        "CAS Number": "67-56-1",
        "Classification": "Flammable Solvent",
        "Source": "Purchased"
    }
    test_bad_name = {}
    test_bad_cas = {}
    test_bad_classification_type = {}
    test_bad_classification_value = {}
    test_bad_source_type = {}
    test_bad_source_value = {}

    # Create
    response = client.post("/chemicals", json=test_good_chemical)
    assert response.status_code == 201
    chemical_id = response.json["inserted_id"]
    
    # Get chemicals
    get = client.get(f"/chemicals")
    assert get.status_code == 200

    # Delete chemical
    delete = client.delete(f"/chemicals/{chemical_id}")
    assert delete.status_code == 204