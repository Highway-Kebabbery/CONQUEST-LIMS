from chemical_inventory_api_v1 import ChemicalSchema, ListsSchema, ValidationErrorCodes

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

#_____________________________________________________________________________
# Permutations of valid HHTP requests with invalid data schema
# Magic numbers, types, and string literals in this section are chosen
# specifically to break schema validation without being invalid HTTP requests

# valid_purchased_chemical_1
# Name
val_purch_1_name_miss_field = valid_purchased_chemical_1
val_purch_1_name_miss_field[ChemicalSchema.NAME_KEY].pop()

val_purch_1_name_miss_value = valid_purchased_chemical_1
val_purch_1_name_miss_value[ChemicalSchema.NAME_KEY] = None

val_purch_1_name_type = valid_purchased_chemical_1
val_purch_1_name_type[ChemicalSchema.NAME_KEY] = 1

# CAS_Number
val_purch_1_cas_miss_field = valid_purchased_chemical_1
val_purch_1_cas_miss_field[ChemicalSchema.CAS_KEY].pop()

val_purch_1_cas_miss_value = valid_purchased_chemical_1
val_purch_1_cas_miss_value[ChemicalSchema.CAS_KEY] = None

val_purch_1_cas_type = valid_purchased_chemical_1
val_purch_1_cas_type[ChemicalSchema.CAS_KEY] = 1

# Classification
val_purch_1_classif_miss_field = valid_purchased_chemical_1
val_purch_1_classif_miss_field[ChemicalSchema.CLASSIF_KEY].pop()

val_purch_1_classif_miss_value = valid_purchased_chemical_1
val_purch_1_classif_miss_value[ChemicalSchema.CLASSIF_KEY] = None

val_purch_1_classif_type = valid_purchased_chemical_1
val_purch_1_classif_type[ChemicalSchema.CLASSIF_KEY] = 1

val_purch_1_classif_inval_list_entry = valid_purchased_chemical_1
val_purch_1_classif_inval_list_entry[ChemicalSchema.CLASSIF_KEY] = "Value of valid type but not in list"

# Source
val_purch_1_source_miss_field = valid_purchased_chemical_1
val_purch_1_source_miss_field[ChemicalSchema.SOURCE_KEY].pop()

val_purch_1_source_miss_value = valid_purchased_chemical_1
val_purch_1_source_miss_value[ChemicalSchema.SOURCE_KEY] = None

val_purch_1_source_type = valid_purchased_chemical_1
val_purch_1_source_type[ChemicalSchema.SOURCE_KEY] = 1

val_purch_1_source_inval_list_entry = valid_purchased_chemical_1
val_purch_1_source_inval_list_entry[ChemicalSchema.SOURCE_KEY] = "Value of valid type but not in list"

# Purchased_Fields
val_purch_1_purch_fields_miss_field = valid_purchased_chemical_1
val_purch_1_purch_fields_miss_field[ChemicalSchema.PURCH_FIELD_KEY].pop()

val_purch_1_purch_fields_miss_value = valid_purchased_chemical_1
val_purch_1_purch_fields_miss_value[ChemicalSchema.PURCH_FIELD_KEY] = None

val_purch_1_purch_fields_type = valid_purchased_chemical_1
val_purch_1_purch_fields_type[ChemicalSchema.PURCH_FIELD_KEY] = 1

# Manufacturer
val_purch_1_manu_miss_field = valid_purchased_chemical_1
val_purch_1_manu_miss_field[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.MANU_KEY].pop()

val_purch_1_manu_miss_value = valid_purchased_chemical_1
val_purch_1_manu_miss_value[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.MANU_KEY] = None

val_purch_1_manu_type = valid_purchased_chemical_1
val_purch_1_manu_type[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.MANU_KEY] = 1

val_purch_1_manu_inval_list_entry = valid_purchased_chemical_1
val_purch_1_manu_inval_list_entry[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.MANU_KEY] = "Value of valid type but not in list"

# Manufacturer_Part_Number
val_purch_1_manu_pn_miss_field = valid_purchased_chemical_1
val_purch_1_manu_pn_miss_field[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.MANU_PN_KEY].pop()

val_purch_1_manu_pn_miss_value = valid_purchased_chemical_1
val_purch_1_manu_pn_miss_value[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.MANU_PN_KEY] = None

val_purch_1_manu_pn_type = valid_purchased_chemical_1
val_purch_1_manu_pn_type[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.MANU_PN_KEY] = 1

# Amount
val_purch_1_amount_miss_field = valid_purchased_chemical_1
val_purch_1_amount_miss_field[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.AMT_KEY].pop()

val_purch_1_amount_miss_value = valid_purchased_chemical_1
val_purch_1_amount_miss_value[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.AMT_KEY] = None

val_purch_1_amount_type = valid_purchased_chemical_1
val_purch_1_amount_type[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.AMT_KEY] = "wrong type"

# Units
val_purch_1_units_miss_field = valid_purchased_chemical_1
val_purch_1_units_miss_field[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.UNIT_KEY].pop()

val_purch_1_units_miss_value = valid_purchased_chemical_1
val_purch_1_units_miss_value[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.UNIT_KEY] = None

val_purch_1_units_type = valid_purchased_chemical_1
val_purch_1_units_type[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.UNIT_KEY] = 1

val_purch_1_units_inval_list_entry = valid_purchased_chemical_1
val_purch_1_units_inval_list_entry[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.UNIT_KEY] = "Value of valid type but not in list"

# Container_Type
val_purch_1_container_miss_field = valid_purchased_chemical_1
val_purch_1_container_miss_field[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.CONT_TYPE_KEY].pop()

val_purch_1_container_miss_value = valid_purchased_chemical_1
val_purch_1_container_miss_value[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.CONT_TYPE_KEY] = None

val_purch_1_container_type = valid_purchased_chemical_1
val_purch_1_container_type[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.CONT_TYPE_KEY] = 1

val_purch_1_container_inval_list_entry = valid_purchased_chemical_1
val_purch_1_container_inval_list_entry[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.CONT_TYPE_KEY] = "Value of valid type but not in list"

# Unexpected Field
val_purch_1_container_extra_field = valid_purchased_chemical_1
val_purch_1_container_extra_field["foo"] = "bar"
val_purch_1_container_extra_field["fizz"] = "buzz"

# Do two error return the first-encountered error as expected?
val_purch_1_miss_field_type = valid_purchased_chemical_1
val_purch_1_miss_field_type[ChemicalSchema.NAME_KEY].pop()
val_purch_1_miss_field_type[ChemicalSchema.CAS_KEY] = True




# valid_purchased_chemical_2
# Name
val_purch_2_name_miss_field = valid_purchased_chemical_2
val_purch_2_name_miss_field[ChemicalSchema.NAME_KEY].pop()

val_purch_2_name_miss_value = valid_purchased_chemical_2
val_purch_2_name_miss_value[ChemicalSchema.NAME_KEY] = None

val_purch_2_name_type = valid_purchased_chemical_2
val_purch_2_name_type[ChemicalSchema.NAME_KEY] = 1

# CAS_Number
val_purch_2_cas_miss_field = valid_purchased_chemical_2
val_purch_2_cas_miss_field[ChemicalSchema.CAS_KEY].pop()

val_purch_2_cas_miss_value = valid_purchased_chemical_2
val_purch_2_cas_miss_value[ChemicalSchema.CAS_KEY] = None

val_purch_2_cas_type = valid_purchased_chemical_2
val_purch_2_cas_type[ChemicalSchema.CAS_KEY] = 1

# Classification
val_purch_2_classif_miss_field = valid_purchased_chemical_2
val_purch_2_classif_miss_field[ChemicalSchema.CLASSIF_KEY].pop()

val_purch_2_classif_miss_value = valid_purchased_chemical_2
val_purch_2_classif_miss_value[ChemicalSchema.CLASSIF_KEY] = None

val_purch_2_classif_type = valid_purchased_chemical_2
val_purch_2_classif_type[ChemicalSchema.CLASSIF_KEY] = 1

val_purch_2_classif_inval_list_entry = valid_purchased_chemical_2
val_purch_2_classif_inval_list_entry[ChemicalSchema.CLASSIF_KEY] = "Value of valid type but not in list"

# Source
val_purch_2_source_miss_field = valid_purchased_chemical_2
val_purch_2_source_miss_field[ChemicalSchema.SOURCE_KEY].pop()

val_purch_2_source_miss_value = valid_purchased_chemical_2
val_purch_2_source_miss_value[ChemicalSchema.SOURCE_KEY] = None

val_purch_2_source_type = valid_purchased_chemical_2
val_purch_2_source_type[ChemicalSchema.SOURCE_KEY] = 1

val_purch_2_source_inval_list_entry = valid_purchased_chemical_2
val_purch_2_source_inval_list_entry[ChemicalSchema.SOURCE_KEY] = "Value of valid type but not in list"

# Purchased_Fields
val_purch_2_purch_fields_miss_field = valid_purchased_chemical_2
val_purch_2_purch_fields_miss_field[ChemicalSchema.PURCH_FIELD_KEY].pop()

val_purch_2_purch_fields_miss_value = valid_purchased_chemical_2
val_purch_2_purch_fields_miss_value[ChemicalSchema.PURCH_FIELD_KEY] = None

val_purch_2_purch_fields_type = valid_purchased_chemical_2
val_purch_2_purch_fields_type[ChemicalSchema.PURCH_FIELD_KEY] = 1

# Manufacturer
val_purch_2_manu_miss_field = valid_purchased_chemical_2
val_purch_2_manu_miss_field[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.MANU_KEY].pop()

val_purch_2_manu_miss_value = valid_purchased_chemical_2
val_purch_2_manu_miss_value[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.MANU_KEY] = None

val_purch_2_manu_type = valid_purchased_chemical_2
val_purch_2_manu_type[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.MANU_KEY] = 1

val_purch_2_manu_inval_list_entry = valid_purchased_chemical_2
val_purch_2_manu_inval_list_entry[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.MANU_KEY] = "Value of valid type but not in list"

# Manufacturer_Part_Number
val_purch_2_manu_pn_miss_field = valid_purchased_chemical_2
val_purch_2_manu_pn_miss_field[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.MANU_PN_KEY].pop()

val_purch_2_manu_pn_miss_value = valid_purchased_chemical_2
val_purch_2_manu_pn_miss_value[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.MANU_PN_KEY] = None

val_purch_2_manu_pn_type = valid_purchased_chemical_2
val_purch_2_manu_pn_type[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.MANU_PN_KEY] = 1

# Amount
val_purch_2_amount_miss_field = valid_purchased_chemical_2
val_purch_2_amount_miss_field[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.AMT_KEY].pop()

val_purch_2_amount_miss_value = valid_purchased_chemical_2
val_purch_2_amount_miss_value[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.AMT_KEY] = None

val_purch_2_amount_type = valid_purchased_chemical_2
val_purch_2_amount_type[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.AMT_KEY] = "wrong type"

# Units
val_purch_2_units_miss_field = valid_purchased_chemical_2
val_purch_2_units_miss_field[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.UNIT_KEY].pop()

val_purch_2_units_miss_value = valid_purchased_chemical_2
val_purch_2_units_miss_value[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.UNIT_KEY] = None

val_purch_2_units_type = valid_purchased_chemical_2
val_purch_2_units_type[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.UNIT_KEY] = 1

val_purch_2_units_inval_list_entry = valid_purchased_chemical_2
val_purch_2_units_inval_list_entry[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.UNIT_KEY] = "Value of valid type but not in list"

# Container_Type
val_purch_2_container_miss_field = valid_purchased_chemical_2
val_purch_2_container_miss_field[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.CONT_TYPE_KEY].pop()

val_purch_2_container_miss_value = valid_purchased_chemical_2
val_purch_2_container_miss_value[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.CONT_TYPE_KEY] = None

val_purch_2_container_type = valid_purchased_chemical_2
val_purch_2_container_type[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.CONT_TYPE_KEY] = 1

val_purch_2_container_inval_list_entry = valid_purchased_chemical_2
val_purch_2_container_inval_list_entry[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.CONT_TYPE_KEY] = "Value of valid type but not in list"

# Unexpected Field
val_purch_2_container_extra_field = valid_purchased_chemical_2
val_purch_2_container_extra_field["foo"] = "bar"
val_purch_2_container_extra_field["fizz"] = "buzz"

# Do two error return the first-encountered error as expected?
val_purch_2_miss_field_type = valid_purchased_chemical_2
val_purch_2_miss_field_type[ChemicalSchema.NAME_KEY].pop()
val_purch_2_miss_field_type[ChemicalSchema.CAS_KEY] = True




# valid_prepared_chemical_1
# Name
val_prep_1_name_miss_field = valid_prepared_chemical_1
val_prep_1_name_miss_field[ChemicalSchema.NAME_KEY].pop()

val_prep_1_name_miss_value = valid_prepared_chemical_1
val_prep_1_name_miss_value[ChemicalSchema.NAME_KEY] = None

val_prep_1_name_type = valid_prepared_chemical_1
val_prep_1_name_type[ChemicalSchema.NAME_KEY] = 1

# CAS_Number
val_prep_1_cas_miss_field = valid_prepared_chemical_1
val_prep_1_cas_miss_field[ChemicalSchema.CAS_KEY].pop()

val_prep_1_cas_miss_value = valid_prepared_chemical_1
val_prep_1_cas_miss_value[ChemicalSchema.CAS_KEY] = None

val_prep_1_cas_type = valid_prepared_chemical_1
val_prep_1_cas_type[ChemicalSchema.CAS_KEY] = 1

# Classification
val_prep_1_classif_miss_field = valid_prepared_chemical_1
val_prep_1_classif_miss_field[ChemicalSchema.CLASSIF_KEY].pop()

val_prep_1_classif_miss_value = valid_prepared_chemical_1
val_prep_1_classif_miss_value[ChemicalSchema.CLASSIF_KEY] = None

val_prep_1_classif_type = valid_prepared_chemical_1
val_prep_1_classif_type[ChemicalSchema.CLASSIF_KEY] = 1

val_prep_1_classif_inval_list_entry = valid_prepared_chemical_1
val_prep_1_classif_inval_list_entry[ChemicalSchema.CLASSIF_KEY] = "Value of valid type but not in list"

# Storage_Condition
val_prep_1_stor_cond_miss_field = valid_prepared_chemical_1
val_prep_1_stor_cond_miss_field[ChemicalSchema.STORAGE_KEY].pop()

val_prep_1_stor_cond_miss_value = valid_prepared_chemical_1
val_prep_1_stor_cond_miss_value[ChemicalSchema.STORAGE_KEY] = None

val_prep_1_stor_cond_type = valid_prepared_chemical_1
val_prep_1_stor_cond_type[ChemicalSchema.STORAGE_KEY] = 1

val_prep_1_stor_cond_inval_list_entry = valid_prepared_chemical_1
val_prep_1_stor_cond_inval_list_entry[ChemicalSchema.STORAGE_KEY] = "Value of valid type but not in list"

# Source
val_prep_1_source_miss_field = valid_prepared_chemical_1
val_prep_1_source_miss_field[ChemicalSchema.SOURCE_KEY].pop()

val_prep_1_source_miss_value = valid_prepared_chemical_1
val_prep_1_source_miss_value[ChemicalSchema.SOURCE_KEY] = None

val_prep_1_source_type = valid_prepared_chemical_1
val_prep_1_source_type[ChemicalSchema.SOURCE_KEY] = 1

val_prep_1_source_inval_list_entry = valid_prepared_chemical_1
val_prep_1_source_inval_list_entry[ChemicalSchema.SOURCE_KEY] = "Value of valid type but not in list"

# Prepared_Fields
val_prep_1_prep_fields_miss_field = valid_prepared_chemical_1
val_prep_1_prep_fields_miss_field[ChemicalSchema.PREP_FIELD_KEY].pop()

val_prep_1_prep_fields_miss_value = valid_prepared_chemical_1
val_prep_1_prep_fields_miss_value[ChemicalSchema.PREP_FIELD_KEY] = None

val_prep_1_prep_fields_type = valid_prepared_chemical_1
val_prep_1_prep_fields_type[ChemicalSchema.PREP_FIELD_KEY] = 1

# Manufacturer
val_prep_1_manu_miss_field = valid_prepared_chemical_1
val_prep_1_manu_miss_field[ChemicalSchema.PREP_FIELD_KEY][ChemicalSchema.METH_REF_KEY].pop()

val_prep_1_manu_miss_value = valid_prepared_chemical_1
val_prep_1_manu_miss_value[ChemicalSchema.PREP_FIELD_KEY][ChemicalSchema.METH_REF_KEY] = None

val_prep_1_manu_type = valid_prepared_chemical_1
val_prep_1_manu_type[ChemicalSchema.PREP_FIELD_KEY][ChemicalSchema.METH_REF_KEY] = 1

val_prep_1_manu_inval_list_entry = valid_prepared_chemical_1
val_prep_1_manu_inval_list_entry[ChemicalSchema.PREP_FIELD_KEY][ChemicalSchema.METH_REF_KEY] = "Value of valid type but not in list"

# Unexpected Field
val_prep_1_container_extra_field = valid_prepared_chemical_1
val_prep_1_container_extra_field["foo"] = "bar"
val_prep_1_container_extra_field["fizz"] = "buzz"

# Do two error return the first-encountered error as expected?
val_prep_1_miss_field_type = valid_prepared_chemical_1
val_prep_1_miss_field_type[ChemicalSchema.NAME_KEY].pop()
val_prep_1_miss_field_type[ChemicalSchema.CAS_KEY] = True



# When I return: This set of tuples can be copied/pasted ad nauseum to reduce
# work to copy/pasting right object with right error code and occassionally
# removing the error code tuples that don't fit
invalid_chemicals = [
    (, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (, ValidationErrorCodes.WRONG_TYPE_MSG),
    (, ValidationErrorCodes.INVAL_LIST_ENTRY_MSG)
]
#_____________________________________________________________________________


def test_add_chemicals(client):
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




    # Confirm POST requests with empty body return 400
    empty_request_body = {}
    empty_body_reponse = client.post(chemicals_address, json=empty_request_body)

    assert empty_body_reponse.status_code == 400




    # Ensure all valid HTTP requests that fail ChemicalSchema validation return 422
    # and the appropriate error message in the request body
    err_msg_miss_field = ValidationErrorCodes.MISS_REQ_FIELD_MSG  # 23 chars
    err_msg_miss_value = ValidationErrorCodes.MISS_REQ_VALUE_MSG  # 29 chars
    err_msg_type = ValidationErrorCodes.WRONG_TYPE_MSG  # 30 chars
    err_msg_inval_list_entry = ValidationErrorCodes.INVAL_LIST_ENTRY_MSG  # 45 chars
    err_msg_extra_field = ValidationErrorCodes.UNEXP_FIELD_MSG  # 18 chars
    err_msg_chem_dup = ValidationErrorCodes.CHEM_DUPLICATE_MSG  # 36 chars

    # Missing fields, missing values, wrong types, and invalid list entries


    # Unexpected fields
    extra_field_chem_response_1 = client.post(chemicals_address, json=val_purch_1_container_extra_field)
    extra_field_chem_response_2 = client.post(chemicals_address, json=val_purch_2_container_extra_field)
    extra_field_chem_response_3= client.post(chemicals_address, json=val_prep_1_container_extra_field)

    data_1 = extra_field_chem_response_1.get_json()
    data_2 = extra_field_chem_response_2.get_json()
    data_3 = extra_field_chem_response_3.get_json()

    assert data_1["error"].startwith(ValidationErrorCodes.UNEXP_FIELD_MSG)
    assert extra_field_chem_response_1.status_code == 422
    assert data_2["error"].startwith(ValidationErrorCodes.UNEXP_FIELD_MSG)
    assert extra_field_chem_response_2.status_code == 422
    assert data_3["error"].startwith(ValidationErrorCodes.UNEXP_FIELD_MSG)
    assert extra_field_chem_response_3.status_code == 422

    # Chemical duplicate
    post_chem_dup_response = client.post(chemicals_address, json=valid_purchased_chemical_1)
    data_1 = post_chem_dup_response.getjson()

    assert data_1["error"].startwith(ValidationErrorCodes.CHEM_DUPLICATE_MSG)
    assert post_chem_dup_response.status_code == 422

    # Two errors should return the first-encountered error
    miss_field_type_response_1 = client.post(chemicals_address, json=val_purch_1_miss_field_type)
    miss_field_type_response_2 = client.post(chemicals_address, json=val_purch_2_miss_field_type)
    miss_field_type_response_3 = client.post(chemicals_address, json=val_prep_1_miss_field_type)

    data_1 = miss_field_type_response_1
    data_2 = miss_field_type_response_2
    data_3 = miss_field_type_response_3

    assert data_1["error"].startswith(ValidationErrorCodes.MISS_REQ_FIELD_MSG)
    assert miss_field_type_response_1.status_code == 422
    assert data_2["error"].startswith(ValidationErrorCodes.MISS_REQ_FIELD_MSG)
    assert miss_field_type_response_2.status_code == 422
    assert data_3["error"].startswith(ValidationErrorCodes.MISS_REQ_FIELD_MSG)
    assert miss_field_type_response_3.status_code == 422