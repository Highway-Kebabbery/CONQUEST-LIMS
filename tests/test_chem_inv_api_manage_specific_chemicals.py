from bson import ObjectId


"""
Need to update to reflect database structure of chemicals and lots collections
"""

def test_manage_specific_chemicals(client):
    test_chemical = {
        "Name": "Acetone-d6, SPEX CertiPrep",
        "CAS Number": "67-64-1",
        "Amount": 1,
        "Units": "mL",
        "Container Type": "Ampoule",
        "Storage Condition": "2-8 °C",
        "Classification": "Standard",
        "Source": "Purchased",
        "Manufacturer": "Fisher Scientific",
        "Manufacturer Part Number": "S-141",
        "Lot/Batch Number": "458GD65B-001"
    }

    updated_test_chemical = {
        "Name": "Mobile Phase B, Methanol, 40 % v/v in Water",
        "CAS Number": "67-56-1, 7732-18-5",
        "Amount": 1,
        "Units": "L",
        "Container Type": "Bottle",
        "Storage Condition": "Ambient",
        "Classification": "Mobile Phase",
        "Source": "Prepared",
        "Date Prepared": "29-Mar-2025",
        "Internal Lot Number": "30Mar2025-NRW-001",
        "Components": {
            "Comopnent 1": {
                "Name": "Water, In-House",
                "Amount": 900,
                "Units": "µL",
                "Lot Number": "In-House"
            },
            "Component 2": {
                "Name": "Methanol",
                "Amount": 600,
                "Units": "µL",
                "Lot Number": "465FD23GJ"
            }
        }
    }

    # Create chemical and check for success
    response = client.post("/chemicals", json=test_chemical)
    assert response.status_code == 201
    chemical_id = response.json["inserted_id"]
    
    # Update chemical

    # Delete chemical
    delete = client.delete(f"chemicals/{chemical_id}")
    assert delete.status_code == 204

    # Confirm deletion of chemical
    get = client.get(f"chemicals/{chemical_id}")
    assert get.status_code == 404
