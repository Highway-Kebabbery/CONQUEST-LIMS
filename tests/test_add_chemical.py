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

def test_add_chemicals(client):
    # Create chemical and check for success
    response_1 = client.post("/chemicals", json=valid_purchased_chemical_1)
    response_2 = client.post("/chemicals", json=valid_purchased_chemical_2)
    response_3 = client.post("/chemicals", json=valid_prepared_chemical_1)
    
    assert response_1.status_code == 201
    assert response_2.status_code == 201
    assert response_3.status_code == 201

# Test all possible failures