from bson import ObjectId

def test_manage_general_chemicals(client):
    test_chemical = {
        "name": "Methanol",
        "CAS Number": "67-56-1",
        "Amount": 4,
        "Units": "L",
        "Container Type": "Bottle",
        "Storage Condition": "Ambient",
        "Source": "Purchased",
        "Manufacturer": "Fisher Scientific",
        "Lot/Batch Number": "16J289F"
    }

    # Create
    response = client.post("/chemicals", json=test_chemical)
    assert response.status_code == 201
    chemical_id = response.json["inserted_id"]
    
    # Get chemicals
    get = client.get(f"/chemicals")
    assert get.status_code == 200

    # Delete chemical
    delete = client.delete(f"/chemicals/{chemical_id}")
    assert delete.status_code == 204