#!/bin/bash
minikube_ip="$1"

set -e

BASE_URL="http://$minikube_ip:30007"
HEADERS=(-H "Content-Type: application/json")

# ----- Lists -----
echo "Testing /lists endpoints..."

curl -sf -X POST "${BASE_URL}/lists" "${HEADERS[@]}" \
  -d '{"Name": "SmokeList", "List_entries": ["a", "b"]}' > /dev/null || {
  echo "POST /lists failed."
  exit 1
}

curl -sf "${BASE_URL}/lists" > /dev/null || {
  echo "GET /lists failed."
  exit 1
}

curl -sf "${BASE_URL}/lists/SmokeList" > /dev/null
curl -sf "${BASE_URL}/lists" > /dev/null || {
  echo "GET /lists/<list_name> failed."
  exit 1
}

curl -sf -X PUT "${BASE_URL}/lists/SmokeList" "${HEADERS[@]}" \
  -d '{"Name": "SmokeList", "List_entries": ["b", "c"]}' > /dev/null || {
  echo "PUT /lists/<list_name> failed."
  exit 1
}

curl -sf -X DELETE "${BASE_URL}/lists/SmokeList" > /dev/null || {
  echo "DELETE /lists/<list_name> failed."
  exit 1
}

# ----- Chemicals -----
echo "Testing /chemicals endpoints..."

# Create a chemical
chemical_id=$(curl -sf -X POST "${BASE_URL}/chemicals" "${HEADERS[@]}" \
  -d '{
    "Name": "SmokeChemical",
    "CAS_Number": "123-45-6",
    "Classification": "Reagent",
    "Storage_Condition": "Ambient",
    "Source": "Purchased",
    "Purchased_Fields": {
        "Manufacturer": "Sigma-Aldrich",
        "Manufacturer_Part_Number": "SC-001",
        "Amount": 5,
        "Units": "g",
        "Container_Type": "Bottle"
    }
  }' | jq -r '.inserted_id'
) || {
  echo "POST /chemicals failed."
  exit 1
}

curl -sf "${BASE_URL}/chemicals" > /dev/null || {
  echo "GET /chemicals failed."
  exit 1
}

curl -sf "${BASE_URL}/chemicals/${chemical_id}" > /dev/null || {
  echo "GET /chemicals/<chemical_id> failed."
  exit 1
}

curl -sf -X PUT "${BASE_URL}/chemicals/${chemical_id}" "${HEADERS[@]}" \
  -d '{
    "_id": "'"$chemical_id"'",
    "Name": "UpdatedSmokeChemical",
    "CAS_Number": "123-45-6",
    "Classification": "Reagent",
    "Storage_Condition": "Ambient",
    "Source": "Purchased",
    "Purchased_Fields": {
        "Manufacturer": "Sigma-Aldrich",
        "Manufacturer_Part_Number": "SC-001",
        "Amount": 10,
        "Units": "g",
        "Container_Type": "Bottle"
    }
  }' > /dev/null || {
  echo "PUT /chemicals/<chemical_id> failed."
  exit 1
}

curl -sf -X DELETE "${BASE_URL}/chemicals/${chemical_id}" > /dev/null || {
  echo "DELETE /chemicals/<temp_chem_id> failed."
  exit 1
}

# ----- Lots -----
echo "Testing /lots endpoints..."

# Create chemical to attach to the lot
temp_chem_id=$(
  curl -sf -X POST "${BASE_URL}/chemicals" "${HEADERS[@]}" \
  -d '{
    "Name": "LotTestChemical",
    "CAS_Number": "654-32-1",
    "Classification": "Reagent",
    "Storage_Condition": "Ambient",
    "Source": "Purchased",
    "Purchased_Fields": {
        "Manufacturer": "VWR",
        "Manufacturer_Part_Number": "LT-001",
        "Amount": 100,
        "Units": "mL",
        "Container_Type": "Vial"
    }
  }' | jq -r '.inserted_id'
) || {
  echo "POST /chemicals failed in lot testing."
  exit 1
}

lot_id=$(
  curl -sf -X POST "${BASE_URL}/lots" "${HEADERS[@]}" \
    -d '{
      "chemical_id": "'"$temp_chem_id"'",
      "Manufacturer_Lot_Batch_Number": "SMK123456",
      "Open_Date": "2025-04-01T00:00:00-04:00",
      "Expiry_Date": "2025-12-31T23:59:59-04:00",
      "Empty_Date": null
    }' | jq -r '.inserted_id'
) || {
echo "POST /lots failed."
exit 1
}

curl -sf "${BASE_URL}/lots" > /dev/null || {
  echo "GET /lots failed."
  exit 1
}

curl -sf "${BASE_URL}/lots/${lot_id}" > /dev/null || {
  echo "GET /lots/<lot_id> failed."
  exit 1
}

curl -sf -X PUT "${BASE_URL}/lots/${lot_id}" "${HEADERS[@]}" \
  -d '{
    "_id": "'"$lot_id"'",
    "chemical_id": "'"$temp_chem_id"'",
    "Manufacturer_Lot_Batch_Number": "SMK123456-UPDATED",
    "Open_Date": "2025-04-01T00:00:00-04:00",
    "Expiry_Date": "2026-12-31T23:59:59-04:00",
    "Empty_Date": null
  }' > /dev/null || {
  echo "PUT /lots/<lot_id> failed."
  exit 1
}

curl -sf -X DELETE "${BASE_URL}/lots/${lot_id}" > /dev/null || {
  echo "DELETE /lots/<lot_id> failed."
  exit 1
}
curl -sf -X DELETE "${BASE_URL}/chemicals/${temp_chem_id}" > /dev/null || {
  echo "DELETE /chemicals/<temp_chem_id> failed in lots testing."
  exit 1
}

echo "All endpoints passed smoke tests."
