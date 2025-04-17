#!/bin/bash
API_URL="$1"

set -e

# Helper Functions
# Note that these functions assume MongoDB's "_id" is the primary key
post_list() {
    local list_json="$1"
    curl -s -X POST "$API_URL/lists" \
        -H "Content-Type: application/json" \
        -d "$list_json" > /dev/null
}

post_chemical() {
    local chemical_json="$1"
    local response
    response=$(curl -s -X POST "$API_URL/chemicals" \
        -H "Content-Type: application/json" \
        -d "$chemical_json")
    echo "$response" | jq -r '.inserted_id'
}

post_lot() {
    local lot_json="$1"
    local response
    response=$(curl -s -X POST "$API_URL/lots" \
        -H "Content-Type: application/json" \
        -d "$lot_json")
    echo "$response" | jq -r '.inserted_id'
}

########## Minimal object set needed to show entire lot logging functionality ##########

# Objects to be loaded
classification_list='{
    "Name": "Classification",
    "List_entries": [
        "Flammable solvent",
        "Strong acid",
        "Super acid",
        "Weak acid",
        "Strong base",
        "Weak base",
        "Mobile phase",
        "Reagent",
        "Standard",
        "Solid",
        "Dewer",
        "Gas cylinder",
        "Water",
        "Water Dispenser"
    ]
}'

container_type_list='{
    "Name": "Container_Type",
    "List_entries": [
        "Ampoule",
        "Autosampler vial",
        "Bottle",
        "Vial",
        "Instrument",
        "N/A"
    ]
}'

manufacturer_list='{
    "Name": "Manufacturer",
    "List_entries": [
        "3M",
        "Agilent",
        "Alfa Aesar",
        "Eppendorf",
        "Fisher Scientific",
        "Honeywell",
        "J.T. Baker",
        "Milli-Q",
        "Sigma-Aldrich",
        "Thermo Fisher Scientific",
        "VWR"
    ]
}'

source_list='{
    "Name": "Source",
    "List_entries": [
        "Purchased",
        "Prepared"
    ]
}'

storage_condition_list='{
    "Name": "Storage_Condition",
    "List_entries": [
        "-80 °C",
        "-20 °C",
        "2-8 °C",
        "Ambient",
        "Ambient, dark",
        "Room temperature"
    ]
}'

units_list='{
    "Name": "Units",
    "List_entries": [
        "g",
        "kg",
        "L",
        "mL",
        "µL",
        "N/A"
    ]
}'

purch_chem_1='{
    "Name": "Methanol (Certified ACS), Fisher Chemical",
    "CAS_Number": "67-56-1",
    "Classification": "Flammable solvent",
    "Storage_Condition": "Ambient",
    "Source": "Purchased",
    "Purchased_Fields": {
        "Manufacturer": "Fisher Scientific",
        "Manufacturer_Part_Number": "A412-4",
        "Amount": 4,
        "Units": "L",
        "Container_Type": "Bottle"
    }
}'

purch_chem_2='{
    "Name": "Water, Optima LC/MS Grade, Fisher Chemical",
    "CAS_Number": "7732-18-5",
    "Classification": "Water",
    "Storage_Condition": "Ambient",
    "Source": "Purchased",
    "Purchased_Fields": {
        "Manufacturer": "Fisher Scientific",
        "Manufacturer_Part_Number": "W64",
        "Amount": 4,
        "Units": "L",
        "Container_Type": "Bottle"
    }
}'

purch_chem_3='{
    "Name": "Phosphoric acid, J.T. Baker",
    "CAS_Number": "7664-38-2",
    "Classification": "Weak acid",
    "Storage_Condition": "Ambient",
    "Source": "Purchased",
    "Purchased_Fields": {
        "Manufacturer": "Fisher Scientific",
        "Manufacturer_Part_Number": "02-003-602",
        "Amount": 500,
        "Units": "mL",
        "Container_Type": "Bottle"
    }
}'

purch_chem_4='{
    "Name": "Milli-Q IQ 7000 Ultrapure Water Purification System",
    "CAS_Number": "7732-18-5",
    "Classification": "Water Dispenser",
    "Storage_Condition": "Ambient",
    "Source": "Purchased",
    "Purchased_Fields": {
        "Manufacturer": "Milli-Q",
        "Manufacturer_Part_Number": "ZIQ7000T0C",
        "Amount": 99999,
        "Units": "N/A",
        "Container_Type": "Instrument"
    }
}'

prep_chem_1='{
    "Name": "Mobile Phase A: Water, 0.1 % Phosphoric Acid",
    "CAS_Number": "7732-18-5, 7664-38-2",
    "Classification": "Mobile phase",
    "Storage_Condition": "Ambient",
    "Source": "Prepared",
    "Prepared_Fields": {
        "Method_Step_Reference": "SOP-00123.4.3.i"
    }
}'

prep_chem_2='{
    "Name": "Mobile Phase B: 40% Methanol in Water, 0.1 % Phosphoric Acid",
    "CAS_Number": "67-56-1, 7732-18-5",
    "Classification": "Mobile phase",
    "Storage_Condition": "Ambient",
    "Source": "Prepared",
    "Prepared_Fields": {
        "Method_Step_Reference": "SOP-00123.4.3.ii"
    }
}'

prep_chem_3='{
    "Name": "Water, in-house",
    "CAS_Number": "7732-18-5",
    "Classification": "Water",
    "Storage_Condition": "Ambient",
    "Source": "Prepared",
    "Prepared_Fields": {
        "Method_Step_Reference": "N/A"
    }
}'

# Post lists and chemicals to get primary keys needed in lot objects
post_list "$classification_list"
post_list "$container_type_list"
post_list "$manufacturer_list"
post_list "$source_list"
post_list "$storage_condition_list"
post_list "$units_list"

purch_chem_1_id=$(post_chemical "$purch_chem_1")
purch_chem_2_id=$(post_chemical "$purch_chem_2")
purch_chem_3_id=$(post_chemical "$purch_chem_3")
purch_chem_4_id=$(post_chemical "$purch_chem_4")
prep_chem_1_id=$(post_chemical "$prep_chem_1")
prep_chem_2_id=$(post_chemical "$prep_chem_2")
prep_chem_3_id=$(post_chemical "$prep_chem_3")

purch_lot_1='{
    "chemical_id": "'"$purch_chem_1_id"'",
    "Manufacturer_Lot_Batch_Number": "124078GSJDLKGH98245-1254",
    "Open_Date": "2024-12-21T14:30:00-04:00",
    "Expiry_Date": "2552-08-30T23:59:59-04:00",
    "Empty_Date": null
}'

purch_lot_2='{
    "chemical_id": "'"$purch_chem_2_id"'",
    "Manufacturer_Lot_Batch_Number": "00142J678F",
    "Open_Date": "2025-04-06T14:30:00-04:00",
    "Expiry_Date": "2552-08-30T23:59:59-04:00",
    "Empty_Date": null
}'

purch_lot_3='{
    "chemical_id": "'"$purch_chem_3_id"'",
    "Manufacturer_Lot_Batch_Number": "16668JT485F",
    "Open_Date": "2025-03-04T14:30:00-04:00",
    "Expiry_Date": "2552-08-30T23:59:59-04:00",
    "Empty_Date": null
}'

purch_lot_4='{
    "chemical_id": "'"$purch_chem_4_id"'",
    "Manufacturer_Lot_Batch_Number": "5499-0954-1382-942 J2",
    "Open_Date": "2025-04-06T14:30:00-04:00",
    "Expiry_Date": "2552-08-30T23:59:59-04:00",
    "Empty_Date": null
}'

# Log purchased lots because prepared lots depend on their existence
purch_lot_1_id=$(post_lot "$purch_lot_1")
purch_lot_2_id=$(post_lot "$purch_lot_2")
purch_lot_3_id=$(post_lot "$purch_lot_3")
purch_lot_4_id=$(post_lot "$purch_lot_4")

prep_lot_2='{
    "chemical_id": "'"$prep_chem_2_id"'",
    "Amount": 4,
    "Units": "L",
    "Container_Type": "Bottle",
    "Preparation_Date": "2025-04-08T14:25:00-04:00",
    "Expiry_Date": "2552-08-30T23:59:59-04:00",
    "Empty_Date": null,
    "Components": [
        {
            "lot_id": "'"$purch_lot_1_id"'",
            "Amount": 1600,
            "Units": "mL"
        },
        {
            "lot_id": "'"$purch_lot_2_id"'",
            "Amount": 2400,
            "Units": "mL"
        },
        {
            "lot_id": "'"$purch_lot_3_id"'",
            "Amount": 4,
            "Units": "mL"
        }
    ]
}'

prep_lot_3='{
        "chemical_id": "'"$prep_chem_3_id"'",
        "Amount": 999999,
        "Units": "N/A",
        "Container_Type": "Instrument",
        "Preparation_Date": "2025-04-08T14:30:00-04:00",
        "Expiry_Date": "2552-08-30T23:59:59-04:00",
        "Empty_Date": null,
        "Components": [
            {
                "lot_id": "'"$purch_lot_4_id"'",
                "Amount": 999999,
                "Units": "N/A"
            }
        ]
    }'

# Log prepared lots 2 and 3 because prep_lot_1 depends on the existence of 
# prep_lot_3 as a component.
prep_lot_2_id=$(post_lot "$prep_lot_2")
prep_lot_3_id=$(post_lot "$prep_lot_3")


# Post final lot; a prepared lot with a prepared lot as a component
prep_lot_1='{
    "chemical_id": "'"$prep_chem_1_id"'",
    "Amount": 4,
    "Units": "L",
    "Container_Type": "Bottle",
    "Preparation_Date": "2025-04-08T14:15:00-04:00",
    "Expiry_Date": "2552-08-30T23:59:59-04:00",
    "Empty_Date": null,
    "Components": [
        {
            "lot_id": "'"$prep_lot_3_id"'",
            "Amount": 4000,
            "Units": "mL"
        },
        {
            "lot_id": "'"$purch_lot_3_id"'",
            "Amount": 4,
            "Units": "mL"
        }
    ]
}'

prep_lot_1_id=$(post_lot "$prep_lot_1")

########## End of minimal object set needed to show entire lot logging functionality ##########


########## Additional object set needed to show ElasticSearch functionality ##########

# Log a few lots that are expired but not empty; lots awaiting disposal

exp_purch_lot_3='{
    "chemical_id": "'"$purch_chem_3_id"'",
    "Manufacturer_Lot_Batch_Number": "16668JT485F",
    "Open_Date": "2025-03-04T14:30:00-04:00",
    "Expiry_Date": "2018-03-17T14:00:00-04:00",
    "Empty_Date": null
}'

# Log a bunch of additional lots so aggregate functions have something 
# interesting to look at
post_lot "$prep_lot_1" > /dev/null
post_lot "$prep_lot_2" > /dev/null
post_lot "$prep_lot_1" > /dev/null
post_lot "$prep_lot_2" > /dev/null
post_lot "$prep_lot_1" > /dev/null
post_lot "$prep_lot_2" > /dev/null
post_lot "$purch_lot_1" > /dev/null
post_lot "$purch_lot_1" > /dev/null
post_lot "$purch_lot_1" > /dev/null
post_lot "$purch_lot_1" > /dev/null
post_lot "$purch_lot_1" > /dev/null
post_lot "$purch_lot_1" > /dev/null
post_lot "$purch_lot_1" > /dev/null
post_lot "$purch_lot_1" > /dev/null
post_lot "$purch_lot_1" > /dev/null
post_lot "$purch_lot_1" > /dev/null
post_lot "$purch_lot_2" > /dev/null
post_lot "$purch_lot_2" > /dev/null
post_lot "$purch_lot_2" > /dev/null
post_lot "$purch_lot_2" > /dev/null
post_lot "$purch_lot_2" > /dev/null
post_lot "$purch_lot_2" > /dev/null
post_lot "$purch_lot_2" > /dev/null
post_lot "$purch_lot_2" > /dev/null

post_lot "$exp_purch_lot_3" > /dev/null
post_lot "$exp_purch_lot_3" > /dev/null
post_lot "$exp_purch_lot_3" > /dev/null

echo "Database successfully loaded with lists, lots, and chemicals."