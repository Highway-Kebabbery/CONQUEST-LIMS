# Validated lists
classifications = {"Name": "Classifications", "List_entries": ["Flammable solvent", "Strong acid", "Weak acid", "Strong base", "Weak base", "Mobile phase", "Reagent", "Standard", "Solid", "Dewer", "Gas cylinder"]}
container_types = {"Name": "Container_types", "List_entries": ["Ampoule", "Autosampler vial", "Bottle", "Vial"]}
manufacturers = {"Name": "Manufacturers", "List_entries": ["3M", "Agilent", "Alfa Aesar", "Eppendorf", "Fisher Scientific", "Honeywell", "Sigma-Aldrich", "Thermo Fisher Scientific", "VWR"]}
sources = {"Name": "Sources", "List_entries": ["Purchased", "Prepared"]}
storage_conditions = {"Name": "Storage_conditions", "List_entries": ["-80 °C", "-20 °C", "2-8 °C", "Ambient", "Ambient, dark", "Room temperature"]}
units = {"Name": "Units", "List_entries": ["g", "kg", "L", "mL", "µL"]}

# Define valid chemicals
valid_purchased_chemical_1 = {
    "Name": "Methanol (Certified ACS), Fisher Chemical",
    "CAS Number": "67-56-1",
    "Classification": "Flammable Solvent",
    "Source": "Purchased",
    "Purchased_Fields": {
        "Manufacturer": "Fisher Scientific",
        "Manufacturer_Part_Number": "A412-4",
        "Amount": 4,
        "Units": "L",
        "Container_Type": "Bottle"
        }
}

valid_purchased_chemical_2 = {
    "Name": "Water, Optima LC/MS Grade, Fisher Chemical",
    "CAS Number": "7732-18-5",
    "Classification": "Water",
    "Source": "Purchased",
    "Purchased_Fields": {
        "Manufacturer": "Fisher Scientific",
        "Manufacturer_Part_Number": "W64",
        "Amount": 4,
        "Units": "L",
        "Container_Type": "Bottle"
    }
}

# Prepared chemical using only purchased components
valid_prepared_chemical_1 = {
    "Name": "Methanol, 40% in Water",
    "CAS_Number": "67-56-1, 7732-18-5",
    "Classification": "Mobile phase",
    "Storage_Condition": "Ambient",
    "Source": "Prepared",
    "Prepared_Fields": {
        "Method_Step_Reference": "SOP-00123.4.3.i"
        }
}

# Prepared chemical using prepared components
# This slot reserved for testing after future upgrade
valid_prepared_chemical_2 = {}


def test_get_chemical(client):
    # POST valid lists and confirm success
    post_list_response_1 = client.post("/chemicals", json=classifications)
    post_list_response_2 = client.post("/chemicals", json=container_types)
    post_list_response_3 = client.post("/chemicals", json=manufacturers)
    post_list_response_4 = client.post("/chemicals", json=sources)
    post_list_response_5 = client.post("/chemicals", json=storage_conditions)
    post_list_response_6 = client.post("/chemicals", json=units)

    assert post_list_response_1.status_code == 201
    assert post_list_response_2.status_code == 201
    assert post_list_response_3.status_code == 201
    assert post_list_response_4.status_code == 201
    assert post_list_response_5.status_code == 201
    assert post_list_response_6.status_code == 201
    
    # POST valid chemicals of all types and confirm success
    post_chem_response_1 = client.post("/chemicals", json=valid_purchased_chemical_1)
    post_chem_response_2 = client.post("/chemicals", json=valid_purchased_chemical_2)
    post_chem_response_3 = client.post("/chemicals", json=valid_prepared_chemical_1)
    #post_chem_response_4 = client.post("/chemicals", json=valid_prepared_chemical_2)

    assert post_chem_response_1.status_code == 201
    assert post_chem_response_2.status_code == 201
    assert post_chem_response_3.status_code == 201
    #assert post_chem_response_4.status_code == 201

    purchased_chem_id_1 = post_chem_response_1.json["inserted_id"]
    purchased_chem_id_2 = post_chem_response_2.json["inserted_id"]
    prepared_chem_id_1 = post_chem_response_3.json["inserted_id"]
    #prepared_chem_id_2 = post_chem_response_4.json["inserted_id"]




    # Remove chemicals and confirm success
    delete_reponse_1 = client.delete(f"chemicals/{purchased_chem_id_1}")
    delete_reponse_2 = client.delete(f"chemicals/{purchased_chem_id_2}")
    delete_reponse_3 = client.delete(f"chemicals/{prepared_chem_id_1}")
    #delete_reponse_4 = client.delete(f"chemicals/{prepared_chem_id_2}")

    assert delete_reponse_1.status_code == 204
    assert delete_reponse_2.status_code == 204
    assert delete_reponse_3.status_code == 204
    #assert delete_reponse_4.status_code == 204




    # Confirm DELETE requests for missing chemicals return 404
    delete_reponse_1 = client.delete(f"chemicals/{purchased_chem_id_1}")
    delete_reponse_2 = client.delete(f"chemicals/{purchased_chem_id_2}")
    delete_reponse_3 = client.delete(f"chemicals/{prepared_chem_id_1}")
    #delete_reponse_4 = client.delete(f"chemicals/{prepared_chem_id_2}")

    assert delete_reponse_1.status_code == 404
    assert delete_reponse_2.status_code == 404
    assert delete_reponse_3.status_code == 404
    #assert delete_reponse_4.status_code == 404




    # Confirm that GET requests with malformed ObjectId return 400
    invalid_id_response_1 = client.get(f"chemicals/1")

    assert invalid_id_response_1 == 400