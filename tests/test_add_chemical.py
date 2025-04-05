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
    "CAS_Number": "67-56-1",
    "Classification": "Flammable Solvent",
    "Source": "Purchased"
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
    "CAS_Number": "7732-18-5",
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

empty_request_body = {}

#_____________________________________________________________________________
# Permutations of valid HHTP requests with invalid data schema


# Don't test EVERY permutation, but at least give one test with two errors per chemical
# to ensure the first detected error is returned (after all single error validated)

# valid_purchased_chemical_1
# Name
val_purch_1_name_miss_field = valid_purchased_chemical_1
del val_purch_1_name_miss_field["Name"]

val_purch_1_name_miss_value = valid_purchased_chemical_1
val_purch_1_name_miss_field["Name"] = None

val_purch_1_name_type = valid_purchased_chemical_1
val_purch_1_name_miss_field["Name"] = 1

# CAS_Number
val_purch_1_cas_miss_field = valid_purchased_chemical_1
del val_purch_1_name_miss_field["CAS_Number"]

val_purch_1_cas_miss_value = valid_purchased_chemical_1
val_purch_1_name_miss_field["CAS_Number"] = None

val_purch_1_cas_type = valid_purchased_chemical_1
val_purch_1_name_miss_field["CAS_Number"] = 1

# Classification
val_purch_1_classif_miss_field = valid_purchased_chemical_1
del val_purch_1_name_miss_field["Classification"]

val_purch_1_classif_miss_value = valid_purchased_chemical_1
val_purch_1_name_miss_field["Classification"] = None

val_purch_1_classif_type = valid_purchased_chemical_1
val_purch_1_name_miss_field["Classification"] = 1

val_purch_1_classif_inval_list_entry = valid_purchased_chemical_1
val_purch_1_name_miss_field["Classification"] = "Value of valid type but not in list"

# Templates not yet written for error codes 4, 5, or 9. 

#_____________________________________________________________________________


def test_add_chemicals(client):
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




    # Confirm POST requests with empty body return 400
    empty_body_reponse = client.post("/chemicals", json=empty_request_body)

    assert empty_body_reponse.status_code == 400




    # Ensure all valid HTTP requests that fail ChemicalSchema validation return 422
    # and the appropriate error message in the request body
