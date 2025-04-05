from chemical_inventory_api_v1 import ChemicalSchema, ListsSchema

# Validated lists
classifications = {f"{ListsSchema.LIST_NAME_KEY}": ListsSchema.CLASSIF_LIST_KEY, f"{ListsSchema.LIST_ENT_KEY}": ["Flammable solvent", "Strong acid", "Weak acid", "Strong base", "Weak base", "Mobile phase", "Reagent", "Standard", "Solid", "Dewer", "Gas cylinder"]}
container_types = {f"{ListsSchema.LIST_NAME_KEY}": ListsSchema.CONT_TYPES_LIST_KEY, f"{ListsSchema.LIST_ENT_KEY}": ["Ampoule", "Autosampler vial", "Bottle", "Vial"]}
manufacturers = {f"{ListsSchema.LIST_NAME_KEY}": ListsSchema.MANU_LIST_KEY, f"{ListsSchema.LIST_ENT_KEY}": ["3M", "Agilent", "Alfa Aesar", "Eppendorf", "Fisher Scientific", "Honeywell", "Sigma-Aldrich", "Thermo Fisher Scientific", "VWR"]}
sources = {f"{ListsSchema.LIST_NAME_KEY}": ListsSchema.SOURCES_LIST_KEY, f"{ListsSchema.LIST_ENT_KEY}": ["Purchased", "Prepared"]}
storage_conditions = {f"{ListsSchema.LIST_NAME_KEY}": ListsSchema.STOR_COND_LIST_KEY(), f"{ListsSchema.LIST_ENT_KEY}": ["-80 °C", "-20 °C", "2-8 °C", "Ambient", "Ambient, dark", "Room temperature"]}
units = {f"{ListsSchema.LIST_NAME_KEY}": ListsSchema.UNITS_LIST_KEY(), f"{ListsSchema.LIST_ENT_KEY}": ["g", "kg", "L", "mL", "µL"]}

# Define valid chemicals
valid_purchased_chemical_1 = {
    ChemicalSchema.NAME_KEY: "Methanol (Certified ACS), Fisher Chemical",
    ChemicalSchema.CAS_KEY: "67-56-1",
    ChemicalSchema.CLASSIF_KEY: "Flammable Solvent",
    ChemicalSchema.SOURCE_KEY: "Purchased",
    ChemicalSchema.PURCH_FIELD_KEY: {
        ChemicalSchema.MANU_KEY: "Fisher Scientific",
        ChemicalSchema.MANU_PN_KEY: "A412-4",
        ChemicalSchema.AMT_KEY: 4,
        ChemicalSchema.UNIT_KEY: "L",
        ChemicalSchema.CONT_TYPE_KEY: "Bottle"
    }
}

valid_purchased_chemical_2 = {
    ChemicalSchema.NAME_KEY: "Water, Optima LC/MS Grade, Fisher Chemical",
    ChemicalSchema.CAS_KEY: "7732-18-5",
    ChemicalSchema.CLASSIF_KEY: "Water",
    ChemicalSchema.SOURCE_KEY: "Purchased",
    ChemicalSchema.PURCH_FIELD_KEY: {
        ChemicalSchema.MANU_KEY: "Fisher Scientific",
        ChemicalSchema.MANU_PN_KEY: "W64",
        ChemicalSchema.AMT_KEY: 4,
        ChemicalSchema.UNIT_KEY: "L",
        ChemicalSchema.CONT_TYPE_KEY: "Bottle"
    }
}


# Prepared chemical using only purchased components
valid_prepared_chemical_1 = {
    ChemicalSchema.NAME_KEY: "Methanol, 40% in Water",
    ChemicalSchema.CAS_KEY: "67-56-1, 7732-18-5",
    ChemicalSchema.CLASSIF_KEY: "Mobile phase",
    ChemicalSchema.STORAGE_KEY: "Ambient",
    ChemicalSchema.SOURCE_KEY: "Prepared",
    ChemicalSchema.PREP_FIELD_KEY: {
        ChemicalSchema.METH_REF_KEY: "SOP-00123.4.3.i"
        }
}

# Prepared chemical using prepared components
# This slot reserved for testing after future upgrade
valid_prepared_chemical_2 = {}


def test_get_all_chemicals(client):
    chemicals_address = "/chemicals"

    # POST valid lists and confirm success
    post_list_response_1 = client.post(chemicals_address, json=classifications)
    post_list_response_2 = client.post(chemicals_address, json=container_types)
    post_list_response_3 = client.post(chemicals_address, json=manufacturers)
    post_list_response_4 = client.post(chemicals_address, json=sources)
    post_list_response_5 = client.post(chemicals_address, json=storage_conditions)
    post_list_response_6 = client.post(chemicals_address, json=units)

    assert post_list_response_1.status_code == 201
    assert post_list_response_2.status_code == 201
    assert post_list_response_3.status_code == 201
    assert post_list_response_4.status_code == 201
    assert post_list_response_5.status_code == 201
    assert post_list_response_6.status_code == 201
    
    # POST valid chemicals of all types and confirm success
    post_chem_response_1 = client.post(chemicals_address, json=valid_purchased_chemical_1)
    post_chem_response_2 = client.post(chemicals_address, json=valid_purchased_chemical_2)
    post_chem_response_3 = client.post(chemicals_address, json=valid_prepared_chemical_1)
    #post_chem_response_4 = client.post(chemicals_address, json=valid_prepared_chemical_2)
    
    assert post_chem_response_1.status_code == 201
    assert post_chem_response_2.status_code == 201
    assert post_chem_response_3.status_code == 201
    #assert post_chem_response_4.status_code == 201

    # GET chemicals and confirm success
    get_reponse_1 = client.get(chemicals_address)
    
    assert get_reponse_1.status_code == 200
