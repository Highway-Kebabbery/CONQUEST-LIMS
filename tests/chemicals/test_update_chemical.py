import pytest, copy
from chemical_inventory_api_v1 import ValidationErrorCodes, ChemicalSchema

#____________________________________________________________________________________
# This is absolutely hideous and I HATE it, but I couldn't figure out how to get the
# dynamically-generated list of tuples from the fixture in conftest.py inside here as a 
# parameter for @pytest.mark.parametrize(). Ultimately I had to cut my losses on time 
# spent and just repeat my code. The point is the app and that it works; not that the 
# test modules are gorgeous. I still hate this, but I need to have the app done.
#
# IF YOU NEED TO TOUCH THIS: CLOSE ALL OTHER FILES THAT USE THE SAME CODE, WORK FROM
# ONE FILE, THEN IMMEDIATELY TRANSFER TO OTHER IMPACTED FILES. ONLY THE ADD AND UPDATE
# TESTS CURRENTLY USE THIS COPY/PASTE LIST; THE OTHERS USE THE FIXTURES IN conftest.py.
# USE THE CHEMICAL FIXTURES IN conftest.py AS THE DEFAULT OBJECTS AND ASSUME WE'LL FIX
# THIS ONE DAY.

valid_purchased_chemical_1 = {
    ChemicalSchema.NAME_KEY: "Methanol (Certified ACS), Fisher Chemical",
    ChemicalSchema.CAS_KEY: "67-56-1",
    ChemicalSchema.CLASSIF_KEY: "Flammable solvent",
    ChemicalSchema.STORAGE_KEY: "Ambient",
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
    ChemicalSchema.STORAGE_KEY: "Ambient",
    ChemicalSchema.SOURCE_KEY: "Purchased",
    ChemicalSchema.PURCH_FIELD_KEY: {
        ChemicalSchema.MANU_KEY: "Fisher Scientific",
        ChemicalSchema.MANU_PN_KEY: "W64",
        ChemicalSchema.AMT_KEY: 4,
        ChemicalSchema.UNIT_KEY: "L",
        ChemicalSchema.CONT_TYPE_KEY: "Bottle"
    }
}

valid_prepared_chemical_1 = {
    ChemicalSchema.NAME_KEY: "Mobile Phase A: Water, 0.1 % Phosphoric Acid",
    ChemicalSchema.CAS_KEY: "7732-18-5, 7664-38-2",
    ChemicalSchema.CLASSIF_KEY: "Mobile phase",
    ChemicalSchema.STORAGE_KEY: "Ambient",
    ChemicalSchema.SOURCE_KEY: "Prepared",
    ChemicalSchema.PREP_FIELD_KEY: {
        ChemicalSchema.METH_REF_KEY: "SOP-00123.4.3.i"
        }
}

# Prepared chemical using only purchased components
valid_prepared_chemical_2 = {
    ChemicalSchema.NAME_KEY: "Mobile Phase B: 40% Methanol in Water, 0.1 % Phosphoric Acid",
    ChemicalSchema.CAS_KEY: "67-56-1, 7732-18-5",
    ChemicalSchema.CLASSIF_KEY: "Mobile phase",
    ChemicalSchema.STORAGE_KEY: "Ambient",
    ChemicalSchema.SOURCE_KEY: "Prepared",
    ChemicalSchema.PREP_FIELD_KEY: {
        ChemicalSchema.METH_REF_KEY: "SOP-00123.4.3.ii"
        }
}

# Unexpected Field
val_purch_1_container_extra_field = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_container_extra_field["foo"] = "bar"
val_purch_1_container_extra_field["fizz"] = "buzz"

# Unexpected Field
val_purch_2_container_extra_field = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_container_extra_field["foo"] = "bar"
val_purch_2_container_extra_field["fizz"] = "buzz"

# Unexpected Field
val_prep_1_container_extra_field = copy.deepcopy(valid_prepared_chemical_1)
val_prep_1_container_extra_field["foo"] = "bar"
val_prep_1_container_extra_field["fizz"] = "buzz"

# Unexpected Field
val_prep_2_container_extra_field = copy.deepcopy(valid_prepared_chemical_2)
val_prep_2_container_extra_field["foo"] = "bar"
val_prep_2_container_extra_field["fizz"] = "buzz"

# Do two error return the first-encountered error as expected?
val_purch_1_miss_field_type = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_miss_field_type.pop(ChemicalSchema.NAME_KEY)
val_purch_1_miss_field_type[ChemicalSchema.CAS_KEY] = True

# Do two error return the first-encountered error as expected?
val_purch_2_miss_field_type = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_miss_field_type.pop(ChemicalSchema.NAME_KEY)
val_purch_2_miss_field_type[ChemicalSchema.CAS_KEY] = True

# Do two error return the first-encountered error as expected?
val_prep_1_miss_field_type = copy.deepcopy(valid_prepared_chemical_1)
val_prep_1_miss_field_type.pop(ChemicalSchema.NAME_KEY)
val_prep_1_miss_field_type[ChemicalSchema.CAS_KEY] = True

# Do two error return the first-encountered error as expected?
val_prep_2_miss_field_type = copy.deepcopy(valid_prepared_chemical_2)
val_prep_2_miss_field_type.pop(ChemicalSchema.NAME_KEY)
val_prep_2_miss_field_type[ChemicalSchema.CAS_KEY] = True




# valid_purchased_chemical_1
# Name
val_purch_1_name_miss_field = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_name_miss_field.pop(ChemicalSchema.NAME_KEY)

val_purch_1_name_miss_value = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_name_miss_value[ChemicalSchema.NAME_KEY] = None

val_purch_1_name_type = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_name_type[ChemicalSchema.NAME_KEY] = 1

# CAS_Number
val_purch_1_cas_miss_field = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_cas_miss_field.pop(ChemicalSchema.CAS_KEY)

val_purch_1_cas_miss_value = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_cas_miss_value[ChemicalSchema.CAS_KEY] = None

val_purch_1_cas_type = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_cas_type[ChemicalSchema.CAS_KEY] = 1

# Classification
val_purch_1_classif_miss_field = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_classif_miss_field.pop(ChemicalSchema.CLASSIF_KEY)

val_purch_1_classif_miss_value = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_classif_miss_value[ChemicalSchema.CLASSIF_KEY] = None

val_purch_1_classif_type = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_classif_type[ChemicalSchema.CLASSIF_KEY] = 1

val_purch_1_classif_inval_list_entry = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_classif_inval_list_entry[ChemicalSchema.CLASSIF_KEY] = "Value of valid type but not in list"

# Source
val_purch_1_source_miss_field = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_source_miss_field.pop(ChemicalSchema.SOURCE_KEY)

val_purch_1_source_miss_value = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_source_miss_value[ChemicalSchema.SOURCE_KEY] = None

val_purch_1_source_type = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_source_type[ChemicalSchema.SOURCE_KEY] = 1

val_purch_1_source_inval_list_entry = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_source_inval_list_entry[ChemicalSchema.SOURCE_KEY] = "Value of valid type but not in list"

# Purchased_Fields
val_purch_1_purch_fields_miss_field = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_purch_fields_miss_field.pop(ChemicalSchema.PURCH_FIELD_KEY)

val_purch_1_purch_fields_miss_value = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_purch_fields_miss_value[ChemicalSchema.PURCH_FIELD_KEY] = None

val_purch_1_purch_fields_type = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_purch_fields_type[ChemicalSchema.PURCH_FIELD_KEY] = 1

# Manufacturer
val_purch_1_manu_miss_field = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_manu_miss_field[ChemicalSchema.PURCH_FIELD_KEY].pop(ChemicalSchema.MANU_KEY)

val_purch_1_manu_miss_value = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_manu_miss_value[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.MANU_KEY] = None

val_purch_1_manu_type = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_manu_type[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.MANU_KEY] = 1

val_purch_1_manu_inval_list_entry = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_manu_inval_list_entry[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.MANU_KEY] = "Value of valid type but not in list"

# Manufacturer_Part_Number
val_purch_1_manu_pn_miss_field = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_manu_pn_miss_field[ChemicalSchema.PURCH_FIELD_KEY].pop(ChemicalSchema.MANU_PN_KEY)

val_purch_1_manu_pn_miss_value = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_manu_pn_miss_value[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.MANU_PN_KEY] = None

val_purch_1_manu_pn_type = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_manu_pn_type[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.MANU_PN_KEY] = 1

# Amount
val_purch_1_amount_miss_field = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_amount_miss_field[ChemicalSchema.PURCH_FIELD_KEY].pop(ChemicalSchema.AMT_KEY)

val_purch_1_amount_miss_value = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_amount_miss_value[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.AMT_KEY] = None

val_purch_1_amount_type = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_amount_type[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.AMT_KEY] = "wrong type"

# Units
val_purch_1_units_miss_field = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_units_miss_field[ChemicalSchema.PURCH_FIELD_KEY].pop(ChemicalSchema.UNIT_KEY)

val_purch_1_units_miss_value = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_units_miss_value[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.UNIT_KEY] = None

val_purch_1_units_type = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_units_type[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.UNIT_KEY] = 1

val_purch_1_units_inval_list_entry = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_units_inval_list_entry[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.UNIT_KEY] = "Value of valid type but not in list"

# Container_Type
val_purch_1_container_miss_field = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_container_miss_field[ChemicalSchema.PURCH_FIELD_KEY].pop(ChemicalSchema.CONT_TYPE_KEY)

val_purch_1_container_miss_value = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_container_miss_value[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.CONT_TYPE_KEY] = None

val_purch_1_container_type = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_container_type[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.CONT_TYPE_KEY] = 1

val_purch_1_container_inval_list_entry = copy.deepcopy(valid_purchased_chemical_1)
val_purch_1_container_inval_list_entry[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.CONT_TYPE_KEY] = "Value of valid type but not in list"




# valid_purchased_chemical_2
# Name
val_purch_2_name_miss_field = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_name_miss_field.pop(ChemicalSchema.NAME_KEY)

val_purch_2_name_miss_value = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_name_miss_value[ChemicalSchema.NAME_KEY] = None

val_purch_2_name_type = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_name_type[ChemicalSchema.NAME_KEY] = 1

# CAS_Number
val_purch_2_cas_miss_field = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_cas_miss_field.pop(ChemicalSchema.CAS_KEY)

val_purch_2_cas_miss_value = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_cas_miss_value[ChemicalSchema.CAS_KEY] = None

val_purch_2_cas_type = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_cas_type[ChemicalSchema.CAS_KEY] = 1

# Classification
val_purch_2_classif_miss_field = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_classif_miss_field.pop(ChemicalSchema.CLASSIF_KEY)

val_purch_2_classif_miss_value = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_classif_miss_value[ChemicalSchema.CLASSIF_KEY] = None

val_purch_2_classif_type = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_classif_type[ChemicalSchema.CLASSIF_KEY] = 1

val_purch_2_classif_inval_list_entry = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_classif_inval_list_entry[ChemicalSchema.CLASSIF_KEY] = "Value of valid type but not in list"

# Source
val_purch_2_source_miss_field = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_source_miss_field.pop(ChemicalSchema.SOURCE_KEY)

val_purch_2_source_miss_value = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_source_miss_value[ChemicalSchema.SOURCE_KEY] = None

val_purch_2_source_type = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_source_type[ChemicalSchema.SOURCE_KEY] = 1

val_purch_2_source_inval_list_entry = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_source_inval_list_entry[ChemicalSchema.SOURCE_KEY] = "Value of valid type but not in list"

# Purchased_Fields
val_purch_2_purch_fields_miss_field = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_purch_fields_miss_field.pop(ChemicalSchema.PURCH_FIELD_KEY)

val_purch_2_purch_fields_miss_value = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_purch_fields_miss_value[ChemicalSchema.PURCH_FIELD_KEY] = None

val_purch_2_purch_fields_type = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_purch_fields_type[ChemicalSchema.PURCH_FIELD_KEY] = 1

# Manufacturer
val_purch_2_manu_miss_field = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_manu_miss_field[ChemicalSchema.PURCH_FIELD_KEY].pop(ChemicalSchema.MANU_KEY)

val_purch_2_manu_miss_value = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_manu_miss_value[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.MANU_KEY] = None

val_purch_2_manu_type = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_manu_type[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.MANU_KEY] = 1

val_purch_2_manu_inval_list_entry = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_manu_inval_list_entry[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.MANU_KEY] = "Value of valid type but not in list"

# Manufacturer_Part_Number
val_purch_2_manu_pn_miss_field = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_manu_pn_miss_field[ChemicalSchema.PURCH_FIELD_KEY].pop(ChemicalSchema.MANU_PN_KEY)

val_purch_2_manu_pn_miss_value = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_manu_pn_miss_value[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.MANU_PN_KEY] = None

val_purch_2_manu_pn_type = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_manu_pn_type[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.MANU_PN_KEY] = 1

# Amount
val_purch_2_amount_miss_field = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_amount_miss_field[ChemicalSchema.PURCH_FIELD_KEY].pop(ChemicalSchema.AMT_KEY)

val_purch_2_amount_miss_value = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_amount_miss_value[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.AMT_KEY] = None

val_purch_2_amount_type = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_amount_type[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.AMT_KEY] = "wrong type"

# Units
val_purch_2_units_miss_field = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_units_miss_field[ChemicalSchema.PURCH_FIELD_KEY].pop(ChemicalSchema.UNIT_KEY)

val_purch_2_units_miss_value = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_units_miss_value[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.UNIT_KEY] = None

val_purch_2_units_type = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_units_type[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.UNIT_KEY] = 1

val_purch_2_units_inval_list_entry = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_units_inval_list_entry[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.UNIT_KEY] = "Value of valid type but not in list"

# Container_Type
val_purch_2_container_miss_field = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_container_miss_field[ChemicalSchema.PURCH_FIELD_KEY].pop(ChemicalSchema.CONT_TYPE_KEY)

val_purch_2_container_miss_value = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_container_miss_value[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.CONT_TYPE_KEY] = None

val_purch_2_container_type = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_container_type[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.CONT_TYPE_KEY] = 1

val_purch_2_container_inval_list_entry = copy.deepcopy(valid_purchased_chemical_2)
val_purch_2_container_inval_list_entry[ChemicalSchema.PURCH_FIELD_KEY][ChemicalSchema.CONT_TYPE_KEY] = "Value of valid type but not in list"




# valid_prepared_chemical_1
# Name
val_prep_1_name_miss_field = copy.deepcopy(valid_prepared_chemical_1)
val_prep_1_name_miss_field.pop(ChemicalSchema.NAME_KEY)

val_prep_1_name_miss_value = copy.deepcopy(valid_prepared_chemical_1)
val_prep_1_name_miss_value[ChemicalSchema.NAME_KEY] = None

val_prep_1_name_type = copy.deepcopy(valid_prepared_chemical_1)
val_prep_1_name_type[ChemicalSchema.NAME_KEY] = 1

# CAS_Number
val_prep_1_cas_miss_field = copy.deepcopy(valid_prepared_chemical_1)
val_prep_1_cas_miss_field.pop(ChemicalSchema.CAS_KEY)

val_prep_1_cas_miss_value = copy.deepcopy(valid_prepared_chemical_1)
val_prep_1_cas_miss_value[ChemicalSchema.CAS_KEY] = None

val_prep_1_cas_type = copy.deepcopy(valid_prepared_chemical_1)
val_prep_1_cas_type[ChemicalSchema.CAS_KEY] = 1

# Classification
val_prep_1_classif_miss_field = copy.deepcopy(valid_prepared_chemical_1)
val_prep_1_classif_miss_field.pop(ChemicalSchema.CLASSIF_KEY)

val_prep_1_classif_miss_value = copy.deepcopy(valid_prepared_chemical_1)
val_prep_1_classif_miss_value[ChemicalSchema.CLASSIF_KEY] = None

val_prep_1_classif_type = copy.deepcopy(valid_prepared_chemical_1)
val_prep_1_classif_type[ChemicalSchema.CLASSIF_KEY] = 1

val_prep_1_classif_inval_list_entry = copy.deepcopy(valid_prepared_chemical_1)
val_prep_1_classif_inval_list_entry[ChemicalSchema.CLASSIF_KEY] = "Value of valid type but not in list"

# Storage_Condition
val_prep_1_stor_cond_miss_field = copy.deepcopy(valid_prepared_chemical_1)
val_prep_1_stor_cond_miss_field.pop(ChemicalSchema.STORAGE_KEY)

val_prep_1_stor_cond_miss_value = copy.deepcopy(valid_prepared_chemical_1)
val_prep_1_stor_cond_miss_value[ChemicalSchema.STORAGE_KEY] = None

val_prep_1_stor_cond_type = copy.deepcopy(valid_prepared_chemical_1)
val_prep_1_stor_cond_type[ChemicalSchema.STORAGE_KEY] = 1

val_prep_1_stor_cond_inval_list_entry = copy.deepcopy(valid_prepared_chemical_1)
val_prep_1_stor_cond_inval_list_entry[ChemicalSchema.STORAGE_KEY] = "Value of valid type but not in list"

# Source
val_prep_1_source_miss_field = copy.deepcopy(valid_prepared_chemical_1)
val_prep_1_source_miss_field.pop(ChemicalSchema.SOURCE_KEY)

val_prep_1_source_miss_value = copy.deepcopy(valid_prepared_chemical_1)
val_prep_1_source_miss_value[ChemicalSchema.SOURCE_KEY] = None

val_prep_1_source_type = copy.deepcopy(valid_prepared_chemical_1)
val_prep_1_source_type[ChemicalSchema.SOURCE_KEY] = 1

val_prep_1_source_inval_list_entry = copy.deepcopy(valid_prepared_chemical_1)
val_prep_1_source_inval_list_entry[ChemicalSchema.SOURCE_KEY] = "Value of valid type but not in list"

# Prepared_Fields
val_prep_1_prep_fields_miss_field = copy.deepcopy(valid_prepared_chemical_1)
val_prep_1_prep_fields_miss_field.pop(ChemicalSchema.PREP_FIELD_KEY)

val_prep_1_prep_fields_miss_value = copy.deepcopy(valid_prepared_chemical_1)
val_prep_1_prep_fields_miss_value[ChemicalSchema.PREP_FIELD_KEY] = None

val_prep_1_prep_fields_type = copy.deepcopy(valid_prepared_chemical_1)
val_prep_1_prep_fields_type[ChemicalSchema.PREP_FIELD_KEY] = 1

# Method_Step_Reference
val_prep_1_meth_miss_field = copy.deepcopy(valid_prepared_chemical_1)
# This particular error actually generates "Missing required value" for "Prepared_Fields"
# because it removes the only field in "Prepared_Fields" and leaves an empty dictionary.
# Rewrite test is schema is ever updated to allow multiple fields within Prepared_Fields.
val_prep_1_meth_miss_field[ChemicalSchema.PREP_FIELD_KEY].pop(ChemicalSchema.METH_REF_KEY)

val_prep_1_meth_miss_value = copy.deepcopy(valid_prepared_chemical_1)
val_prep_1_meth_miss_value[ChemicalSchema.PREP_FIELD_KEY][ChemicalSchema.METH_REF_KEY] = None

val_prep_1_meth_type = copy.deepcopy(valid_prepared_chemical_1)
val_prep_1_meth_type[ChemicalSchema.PREP_FIELD_KEY][ChemicalSchema.METH_REF_KEY] = 1




# valid_prepared_chemical_2
# Name
val_prep_2_name_miss_field = copy.deepcopy(valid_prepared_chemical_2)
val_prep_2_name_miss_field.pop(ChemicalSchema.NAME_KEY)

val_prep_2_name_miss_value = copy.deepcopy(valid_prepared_chemical_2)
val_prep_2_name_miss_value[ChemicalSchema.NAME_KEY] = None

val_prep_2_name_type = copy.deepcopy(valid_prepared_chemical_2)
val_prep_2_name_type[ChemicalSchema.NAME_KEY] = 1

# CAS_Number
val_prep_2_cas_miss_field = copy.deepcopy(valid_prepared_chemical_2)
val_prep_2_cas_miss_field.pop(ChemicalSchema.CAS_KEY)

val_prep_2_cas_miss_value = copy.deepcopy(valid_prepared_chemical_2)
val_prep_2_cas_miss_value[ChemicalSchema.CAS_KEY] = None

val_prep_2_cas_type = copy.deepcopy(valid_prepared_chemical_2)
val_prep_2_cas_type[ChemicalSchema.CAS_KEY] = 1

# Classification
val_prep_2_classif_miss_field = copy.deepcopy(valid_prepared_chemical_2)
val_prep_2_classif_miss_field.pop(ChemicalSchema.CLASSIF_KEY)

val_prep_2_classif_miss_value = copy.deepcopy(valid_prepared_chemical_2)
val_prep_2_classif_miss_value[ChemicalSchema.CLASSIF_KEY] = None

val_prep_2_classif_type = copy.deepcopy(valid_prepared_chemical_2)
val_prep_2_classif_type[ChemicalSchema.CLASSIF_KEY] = 1

val_prep_2_classif_inval_list_entry = copy.deepcopy(valid_prepared_chemical_2)
val_prep_2_classif_inval_list_entry[ChemicalSchema.CLASSIF_KEY] = "Value of valid type but not in list"

# Storage_Condition
val_prep_2_stor_cond_miss_field = copy.deepcopy(valid_prepared_chemical_2)
val_prep_2_stor_cond_miss_field.pop(ChemicalSchema.STORAGE_KEY)

val_prep_2_stor_cond_miss_value = copy.deepcopy(valid_prepared_chemical_2)
val_prep_2_stor_cond_miss_value[ChemicalSchema.STORAGE_KEY] = None

val_prep_2_stor_cond_type = copy.deepcopy(valid_prepared_chemical_2)
val_prep_2_stor_cond_type[ChemicalSchema.STORAGE_KEY] = 1

val_prep_2_stor_cond_inval_list_entry = copy.deepcopy(valid_prepared_chemical_2)
val_prep_2_stor_cond_inval_list_entry[ChemicalSchema.STORAGE_KEY] = "Value of valid type but not in list"

# Source
val_prep_2_source_miss_field = copy.deepcopy(valid_prepared_chemical_2)
val_prep_2_source_miss_field.pop(ChemicalSchema.SOURCE_KEY)

val_prep_2_source_miss_value = copy.deepcopy(valid_prepared_chemical_2)
val_prep_2_source_miss_value[ChemicalSchema.SOURCE_KEY] = None

val_prep_2_source_type = copy.deepcopy(valid_prepared_chemical_2)
val_prep_2_source_type[ChemicalSchema.SOURCE_KEY] = 1

val_prep_2_source_inval_list_entry = copy.deepcopy(valid_prepared_chemical_2)
val_prep_2_source_inval_list_entry[ChemicalSchema.SOURCE_KEY] = "Value of valid type but not in list"

# Prepared_Fields
val_prep_2_prep_fields_miss_field = copy.deepcopy(valid_prepared_chemical_2)
val_prep_2_prep_fields_miss_field.pop(ChemicalSchema.PREP_FIELD_KEY)

val_prep_2_prep_fields_miss_value = copy.deepcopy(valid_prepared_chemical_2)
val_prep_2_prep_fields_miss_value[ChemicalSchema.PREP_FIELD_KEY] = None

val_prep_2_prep_fields_type = copy.deepcopy(valid_prepared_chemical_2)
val_prep_2_prep_fields_type[ChemicalSchema.PREP_FIELD_KEY] = 1

# Method_Step_Reference
val_prep_2_meth_miss_field = copy.deepcopy(valid_prepared_chemical_2)
# This particular error actually generates "Missing required value" for "Prepared_Fields"
# because it removes the only field in "Prepared_Fields" and leaves an empty dictionary.
# Rewrite test is schema is ever updated to allow multiple fields within Prepared_Fields.
val_prep_2_meth_miss_field[ChemicalSchema.PREP_FIELD_KEY].pop(ChemicalSchema.METH_REF_KEY)

val_prep_2_meth_miss_value = copy.deepcopy(valid_prepared_chemical_2)
val_prep_2_meth_miss_value[ChemicalSchema.PREP_FIELD_KEY][ChemicalSchema.METH_REF_KEY] = None

val_prep_2_meth_type = copy.deepcopy(valid_prepared_chemical_2)
val_prep_2_meth_type[ChemicalSchema.PREP_FIELD_KEY][ChemicalSchema.METH_REF_KEY] = 1


invalid_chemicals = [
    # Invalid purchased chemical 1 permutations
    (val_purch_1_name_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (val_purch_1_name_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_purch_1_name_type, ValidationErrorCodes.WRONG_TYPE_MSG),
    (val_purch_1_cas_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (val_purch_1_cas_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_purch_1_cas_type, ValidationErrorCodes.WRONG_TYPE_MSG),
    (val_purch_1_classif_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (val_purch_1_classif_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_purch_1_classif_type, ValidationErrorCodes.WRONG_TYPE_MSG),
    (val_purch_1_classif_inval_list_entry, ValidationErrorCodes.INVAL_LIST_ENTRY_MSG),
    (val_purch_1_source_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),               # Payload 10
    (val_purch_1_source_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_purch_1_source_type, ValidationErrorCodes.WRONG_TYPE_MSG),
    (val_purch_1_source_inval_list_entry, ValidationErrorCodes.INVAL_LIST_ENTRY_MSG),
    (val_purch_1_purch_fields_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (val_purch_1_purch_fields_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_purch_1_purch_fields_type, ValidationErrorCodes.WRONG_TYPE_MSG),
    (val_purch_1_manu_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (val_purch_1_manu_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_purch_1_manu_type, ValidationErrorCodes.WRONG_TYPE_MSG),
    (val_purch_1_manu_inval_list_entry, ValidationErrorCodes.INVAL_LIST_ENTRY_MSG),         # Payload 20
    (val_purch_1_manu_pn_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (val_purch_1_manu_pn_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_purch_1_manu_pn_type, ValidationErrorCodes.WRONG_TYPE_MSG),
    (val_purch_1_amount_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (val_purch_1_amount_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_purch_1_amount_type, ValidationErrorCodes.WRONG_TYPE_MSG),
    (val_purch_1_units_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (val_purch_1_units_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_purch_1_units_type, ValidationErrorCodes.WRONG_TYPE_MSG),
    (val_purch_1_units_inval_list_entry, ValidationErrorCodes.INVAL_LIST_ENTRY_MSG),        # Paylaod 30
    (val_purch_1_container_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (val_purch_1_container_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_purch_1_container_type, ValidationErrorCodes.WRONG_TYPE_MSG),
    (val_purch_1_container_inval_list_entry, ValidationErrorCodes.INVAL_LIST_ENTRY_MSG),
    
    # Invalid purchased chemical 2 permutations
    (val_purch_2_name_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (val_purch_2_name_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_purch_2_name_type, ValidationErrorCodes.WRONG_TYPE_MSG),
    (val_purch_2_cas_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (val_purch_2_cas_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_purch_2_cas_type, ValidationErrorCodes.WRONG_TYPE_MSG),                            # Payload 40
    (val_purch_2_classif_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (val_purch_2_classif_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_purch_2_classif_type, ValidationErrorCodes.WRONG_TYPE_MSG),
    (val_purch_2_classif_inval_list_entry, ValidationErrorCodes.INVAL_LIST_ENTRY_MSG),
    (val_purch_2_source_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (val_purch_2_source_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_purch_2_source_type, ValidationErrorCodes.WRONG_TYPE_MSG),
    (val_purch_2_source_inval_list_entry, ValidationErrorCodes.INVAL_LIST_ENTRY_MSG),
    (val_purch_2_purch_fields_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (val_purch_2_purch_fields_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),         # Payload 50
    (val_purch_2_purch_fields_type, ValidationErrorCodes.WRONG_TYPE_MSG),
    (val_purch_2_manu_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (val_purch_2_manu_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_purch_2_manu_type, ValidationErrorCodes.WRONG_TYPE_MSG),
    (val_purch_2_manu_inval_list_entry, ValidationErrorCodes.INVAL_LIST_ENTRY_MSG),
    (val_purch_2_manu_pn_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (val_purch_2_manu_pn_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_purch_2_manu_pn_type, ValidationErrorCodes.WRONG_TYPE_MSG),
    (val_purch_2_amount_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (val_purch_2_amount_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),               # Paylaod 60
    (val_purch_2_amount_type, ValidationErrorCodes.WRONG_TYPE_MSG),
    (val_purch_2_units_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (val_purch_2_units_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_purch_2_units_type, ValidationErrorCodes.WRONG_TYPE_MSG),
    (val_purch_2_units_inval_list_entry, ValidationErrorCodes.INVAL_LIST_ENTRY_MSG),
    (val_purch_2_container_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (val_purch_2_container_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_purch_2_container_type, ValidationErrorCodes.WRONG_TYPE_MSG),
    (val_purch_2_container_inval_list_entry, ValidationErrorCodes.INVAL_LIST_ENTRY_MSG),

    # Invalid prepared chemical 1 permutations
    (val_prep_1_name_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),                  # Payload 70
    (val_prep_1_name_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_prep_1_name_type, ValidationErrorCodes.WRONG_TYPE_MSG),
    (val_prep_1_cas_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (val_prep_1_cas_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_prep_1_cas_type, ValidationErrorCodes.WRONG_TYPE_MSG),
    (val_prep_1_classif_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (val_prep_1_classif_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_prep_1_classif_type, ValidationErrorCodes.WRONG_TYPE_MSG),
    (val_prep_1_classif_inval_list_entry, ValidationErrorCodes.INVAL_LIST_ENTRY_MSG),
    (val_prep_1_stor_cond_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),             # Payload 80
    (val_prep_1_stor_cond_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_prep_1_stor_cond_type, ValidationErrorCodes.WRONG_TYPE_MSG),
    (val_prep_1_stor_cond_inval_list_entry, ValidationErrorCodes.INVAL_LIST_ENTRY_MSG),
    (val_prep_1_source_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (val_prep_1_source_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_prep_1_source_type, ValidationErrorCodes.WRONG_TYPE_MSG),
    (val_prep_1_source_inval_list_entry, ValidationErrorCodes.INVAL_LIST_ENTRY_MSG),
    (val_prep_1_prep_fields_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (val_prep_1_prep_fields_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_prep_1_prep_fields_type, ValidationErrorCodes.WRONG_TYPE_MSG),                     # Payload 90
    (val_prep_1_meth_miss_field, ValidationErrorCodes.MISS_REQ_VALUE_MSG),  # See note in this payloads creation
    (val_prep_1_meth_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_prep_1_meth_type, ValidationErrorCodes.WRONG_TYPE_MSG),

    # Invalid prepared chemical 2 permutations
    (val_prep_2_name_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (val_prep_2_name_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_prep_2_name_type, ValidationErrorCodes.WRONG_TYPE_MSG),
    (val_prep_2_cas_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (val_prep_2_cas_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_prep_2_cas_type, ValidationErrorCodes.WRONG_TYPE_MSG),
    (val_prep_2_classif_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),               # Payload 100
    (val_prep_2_classif_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_prep_2_classif_type, ValidationErrorCodes.WRONG_TYPE_MSG),
    (val_prep_2_classif_inval_list_entry, ValidationErrorCodes.INVAL_LIST_ENTRY_MSG),
    (val_prep_2_stor_cond_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (val_prep_2_stor_cond_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_prep_2_stor_cond_type, ValidationErrorCodes.WRONG_TYPE_MSG),
    (val_prep_2_stor_cond_inval_list_entry, ValidationErrorCodes.INVAL_LIST_ENTRY_MSG),
    (val_prep_2_source_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (val_prep_2_source_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_prep_2_source_type, ValidationErrorCodes.WRONG_TYPE_MSG),                          # Payload 110
    (val_prep_2_source_inval_list_entry, ValidationErrorCodes.INVAL_LIST_ENTRY_MSG),
    (val_prep_2_prep_fields_miss_field, ValidationErrorCodes.MISS_REQ_FIELD_MSG),
    (val_prep_2_prep_fields_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_prep_2_meth_miss_field, ValidationErrorCodes.MISS_REQ_VALUE_MSG),  # See note in this payloads creation
    (val_prep_2_meth_miss_value, ValidationErrorCodes.MISS_REQ_VALUE_MSG),
    (val_prep_2_meth_type, ValidationErrorCodes.WRONG_TYPE_MSG)
]

#____________________________________________________________________________________


chemicals_address = "/chemicals"

@pytest.fixture()
def post_valid_chemicals(
    client,
    post_all_lists,
    valid_purchased_chemical_1,
    valid_purchased_chemical_2,
    valid_prepared_chemical_1,
    valid_prepared_chemical_2
    ):
    # POST chemicals to set up testing
    post_chem_response_1 = client.post(chemicals_address, json=valid_purchased_chemical_1)
    post_chem_response_2 = client.post(chemicals_address, json=valid_purchased_chemical_2)
    post_chem_response_3 = client.post(chemicals_address, json=valid_prepared_chemical_1)
    post_chem_response_4 = client.post(chemicals_address, json=valid_prepared_chemical_2)

    val_purch_chem_id_1 = post_chem_response_1.json["inserted_id"]
    val_purch_chem_id_2 = post_chem_response_2.json["inserted_id"]
    val_prep_chem_id_1 = post_chem_response_3.json["inserted_id"]
    val_prep_chem_id_2 = post_chem_response_4.json["inserted_id"]

    assert post_chem_response_1.status_code == 201
    assert post_chem_response_2.status_code == 201
    assert post_chem_response_3.status_code == 201
    assert post_chem_response_4.status_code == 201

    return val_purch_chem_id_1, val_purch_chem_id_2, val_prep_chem_id_1, val_prep_chem_id_2

def test_update_chemical(
        client,
        post_all_lists,
        post_valid_chemicals,
        valid_purchased_chemical_1,
        valid_purchased_chemical_2,
        valid_prepared_chemical_1,
        valid_prepared_chemical_2,
        purch_chem_1_extra_field,
        purch_chem_2_extra_field,
        prep_chem_1_extra_field,
        prep_chem_2_extra_field,
        purch_chem_1_miss_field_type,
        purch_chem_2_miss_field_type,
        prep_chem_1_miss_field_type,
        prep_chem_2_miss_field_type
    ):

    (val_purch_chem_id_1,
     val_purch_chem_id_2,
     val_prep_chem_id_1,
     val_prep_chem_id_2
     ) = post_valid_chemicals
    
    # Add primary keys and aggregate fields to objects
    # No value sent with aggregate fields should matter as they should be popped off
    valid_purchased_chemical_1[ChemicalSchema.CHEM_ID_KEY] = val_purch_chem_id_1
    valid_purchased_chemical_2[ChemicalSchema.CHEM_ID_KEY] = val_purch_chem_id_2
    valid_prepared_chemical_1[ChemicalSchema.CHEM_ID_KEY] = val_prep_chem_id_1
    valid_prepared_chemical_2[ChemicalSchema.CHEM_ID_KEY] = val_prep_chem_id_2
    valid_purchased_chemical_1[ChemicalSchema.AVAIL_TOTAL_KEY] = 12
    valid_purchased_chemical_2[ChemicalSchema.AVAIL_TOTAL_KEY] = "Huzzah"
    valid_prepared_chemical_1[ChemicalSchema.AVAIL_TOTAL_KEY] = True
    valid_prepared_chemical_2[ChemicalSchema.AVAIL_TOTAL_KEY] = None
    valid_purchased_chemical_1[ChemicalSchema.AVAIL_OPEN_KEY] = 5.56
    valid_purchased_chemical_2[ChemicalSchema.AVAIL_OPEN_KEY] = ("break", "me")
    valid_prepared_chemical_1[ChemicalSchema.AVAIL_OPEN_KEY] = ["if", "you"]
    valid_prepared_chemical_2[ChemicalSchema.AVAIL_OPEN_KEY] = {"dare": 8934868}
    
    # HTTP code 200 testing
    ## Swap valid purchased chemicals with each other and swap valid prepared chemicals with each other.
    
    ### Update keys in objects to match request addresses
    valid_purchased_chemical_1[ChemicalSchema.CHEM_ID_KEY] = val_purch_chem_id_2
    valid_purchased_chemical_2[ChemicalSchema.CHEM_ID_KEY] = val_purch_chem_id_1
    valid_prepared_chemical_1[ChemicalSchema.CHEM_ID_KEY] = val_prep_chem_id_2
    valid_prepared_chemical_2[ChemicalSchema.CHEM_ID_KEY] = val_prep_chem_id_1
    
    put_chem_response_1 = client.put(f"{chemicals_address}/{val_purch_chem_id_1}", json=valid_purchased_chemical_2)
    put_chem_response_2 = client.put(f"{chemicals_address}/{val_purch_chem_id_2}", json=valid_purchased_chemical_1)
    put_chem_response_3 = client.put(f"{chemicals_address}/{val_prep_chem_id_1}", json=valid_prepared_chemical_2)
    put_chem_response_4 = client.put(f"{chemicals_address}/{val_prep_chem_id_2}", json=valid_prepared_chemical_1)
    
    assert put_chem_response_1.status_code == 200
    assert put_chem_response_2.status_code == 200
    assert put_chem_response_3.status_code == 200
    assert put_chem_response_4.status_code == 200

    ## Swap valid purchased chemicals with valid prepared chemicals and vice versa.
    
    ### Updates keys in objects to match request addresses
    valid_purchased_chemical_1[ChemicalSchema.CHEM_ID_KEY] = val_prep_chem_id_2
    valid_purchased_chemical_2[ChemicalSchema.CHEM_ID_KEY] = val_prep_chem_id_1
    valid_prepared_chemical_1[ChemicalSchema.CHEM_ID_KEY] = val_purch_chem_id_2
    valid_prepared_chemical_2[ChemicalSchema.CHEM_ID_KEY] = val_purch_chem_id_1

    put_chem_response_1 = client.put(f"{chemicals_address}/{val_purch_chem_id_1}", json=valid_prepared_chemical_2)
    put_chem_response_2 = client.put(f"{chemicals_address}/{val_purch_chem_id_2}", json=valid_prepared_chemical_1)
    put_chem_response_3 = client.put(f"{chemicals_address}/{val_prep_chem_id_1}", json=valid_purchased_chemical_2)
    put_chem_response_4 = client.put(f"{chemicals_address}/{val_prep_chem_id_2}", json=valid_purchased_chemical_1)

    assert put_chem_response_1.status_code == 200
    assert put_chem_response_2.status_code == 200
    assert put_chem_response_3.status_code == 200
    assert put_chem_response_4.status_code == 200

    ## Reset chemicals for HTTP code 422 testing
    valid_purchased_chemical_1[ChemicalSchema.CHEM_ID_KEY] = val_purch_chem_id_1
    valid_purchased_chemical_2[ChemicalSchema.CHEM_ID_KEY] = val_purch_chem_id_2
    valid_prepared_chemical_1[ChemicalSchema.CHEM_ID_KEY] = val_prep_chem_id_1
    valid_prepared_chemical_2[ChemicalSchema.CHEM_ID_KEY] = val_prep_chem_id_2

    delete_chem_response_1 = client.delete(f"{chemicals_address}/{val_purch_chem_id_1}")
    delete_chem_response_2 = client.delete(f"{chemicals_address}/{val_purch_chem_id_2}")
    delete_chem_response_3 = client.delete(f"{chemicals_address}/{val_prep_chem_id_1}")
    delete_chem_response_4 = client.delete(f"{chemicals_address}/{val_prep_chem_id_2}")

    assert delete_chem_response_1.status_code == 204
    assert delete_chem_response_2.status_code == 204
    assert delete_chem_response_3.status_code == 204
    assert delete_chem_response_4.status_code == 204


    # HTTP Code 400 response body Testing

    ### Test for a request body and address that have matching, invalid primary keys
    #### The end point code is a fail-safe: This case is handled in schema validations and
    #### will return HTTP code 422.


    # HTTP code 404 testing

    ## Test for chemical record existence
    put_chem_response_1 = client.put(f"{chemicals_address}/{val_purch_chem_id_1}", json=valid_purchased_chemical_1)
    put_chem_response_2 = client.put(f"{chemicals_address}/{val_purch_chem_id_2}", json=valid_purchased_chemical_2)
    put_chem_response_3 = client.put(f"{chemicals_address}/{val_prep_chem_id_1}", json=valid_prepared_chemical_1)
    put_chem_response_4 = client.put(f"{chemicals_address}/{val_prep_chem_id_2}", json=valid_prepared_chemical_2)

    data_1 = put_chem_response_1.get_json()
    data_2 = put_chem_response_2.get_json()
    data_3 = put_chem_response_3.get_json()
    data_4 = put_chem_response_4.get_json()

    assert put_chem_response_1.status_code == 404
    assert data_1["error"].startswith(ValidationErrorCodes.CHEM_NOT_FOUND_MSG)
    assert put_chem_response_2.status_code == 404
    assert data_2["error"].startswith(ValidationErrorCodes.CHEM_NOT_FOUND_MSG)
    assert put_chem_response_3.status_code == 404
    assert data_3["error"].startswith(ValidationErrorCodes.CHEM_NOT_FOUND_MSG)
    assert put_chem_response_4.status_code == 404
    assert data_4["error"].startswith(ValidationErrorCodes.CHEM_NOT_FOUND_MSG)

    # HTTP Code 422 response body Testing
    """
    Ensure all valid HTTP requests that fail ChemicalSchema validation return 422
    and the appropriate error message in the request body. Missing field, missing
    value, wrong type, and invalid list entry are handled in test_invalid_chemicals().
    """

    ## Add chemicals back to database
    post_chem_response_1 = client.post(chemicals_address, json=valid_purchased_chemical_1)
    post_chem_response_2 = client.post(chemicals_address, json=valid_purchased_chemical_2)
    post_chem_response_3 = client.post(chemicals_address, json=valid_prepared_chemical_1)
    post_chem_response_4 = client.post(chemicals_address, json=valid_prepared_chemical_2)

    assert post_chem_response_1.status_code == 201
    assert post_chem_response_2.status_code == 201
    assert post_chem_response_3.status_code == 201
    assert post_chem_response_4.status_code == 201

    ## Unexpected fields
    purch_chem_1_extra_field[ChemicalSchema.CHEM_ID_KEY] = val_purch_chem_id_1
    purch_chem_2_extra_field[ChemicalSchema.CHEM_ID_KEY] = val_purch_chem_id_2
    prep_chem_1_extra_field[ChemicalSchema.CHEM_ID_KEY] = val_prep_chem_id_1
    prep_chem_2_extra_field[ChemicalSchema.CHEM_ID_KEY] = val_prep_chem_id_2


    extra_field_chem_response_1 = client.put(f"{chemicals_address}/{val_purch_chem_id_1}", json=purch_chem_1_extra_field)
    extra_field_chem_response_2 = client.put(f"{chemicals_address}/{val_purch_chem_id_2}", json=purch_chem_2_extra_field)
    extra_field_chem_response_3 = client.put(f"{chemicals_address}/{val_prep_chem_id_1}", json=prep_chem_1_extra_field)
    extra_field_chem_response_4 = client.put(f"{chemicals_address}/{val_prep_chem_id_2}", json=prep_chem_2_extra_field)

    data_1 = extra_field_chem_response_1.get_json()
    data_2 = extra_field_chem_response_2.get_json()
    data_3 = extra_field_chem_response_3.get_json()
    data_4 = extra_field_chem_response_4.get_json()

    assert extra_field_chem_response_1.status_code == 422
    assert data_1["error"].startswith(ValidationErrorCodes.UNEXP_FIELD_MSG)
    assert extra_field_chem_response_2.status_code == 422
    assert data_2["error"].startswith(ValidationErrorCodes.UNEXP_FIELD_MSG)
    assert extra_field_chem_response_3.status_code == 422
    assert data_3["error"].startswith(ValidationErrorCodes.UNEXP_FIELD_MSG)
    assert extra_field_chem_response_4.status_code == 422
    assert data_4["error"].startswith(ValidationErrorCodes.UNEXP_FIELD_MSG)

    ## Multiple errors should return the first-encountered error (control flow testing)
    purch_chem_1_miss_field_type[ChemicalSchema.CHEM_ID_KEY] = val_purch_chem_id_1
    purch_chem_2_miss_field_type[ChemicalSchema.CHEM_ID_KEY] = val_purch_chem_id_2
    prep_chem_1_miss_field_type[ChemicalSchema.CHEM_ID_KEY] = val_prep_chem_id_1
    prep_chem_2_miss_field_type[ChemicalSchema.CHEM_ID_KEY] = val_prep_chem_id_2

    miss_field_type_response_1 = client.put(f"{chemicals_address}/{val_purch_chem_id_1}", json=purch_chem_1_miss_field_type)
    miss_field_type_response_2 = client.put(f"{chemicals_address}/{val_purch_chem_id_2}", json=purch_chem_2_miss_field_type)
    miss_field_type_response_3 = client.put(f"{chemicals_address}/{val_prep_chem_id_1}", json=prep_chem_1_miss_field_type)
    miss_field_type_response_4 = client.put(f"{chemicals_address}/{val_prep_chem_id_2}", json=prep_chem_2_miss_field_type)

    data_1 = miss_field_type_response_1.get_json()
    data_2 = miss_field_type_response_2.get_json()
    data_3 = miss_field_type_response_3.get_json()
    data_4 = miss_field_type_response_4.get_json()

    assert miss_field_type_response_1.status_code == 422
    assert data_1["error"].startswith(ValidationErrorCodes.MISS_REQ_FIELD_MSG)
    assert miss_field_type_response_2.status_code == 422
    assert data_2["error"].startswith(ValidationErrorCodes.MISS_REQ_FIELD_MSG)
    assert miss_field_type_response_3.status_code == 422
    assert data_3["error"].startswith(ValidationErrorCodes.MISS_REQ_FIELD_MSG)
    assert miss_field_type_response_4.status_code == 422
    assert data_4["error"].startswith(ValidationErrorCodes.MISS_REQ_FIELD_MSG)

    ## Invalid _id format
    ### Test that request bodies without a primary key are caught (also catches empty request bodies)
    miss_prim_key_req = copy.deepcopy(valid_purchased_chemical_1)
    miss_prim_key_req.pop(ChemicalSchema.CHEM_ID_KEY)
    
    miss_prim_key_response = client.put(f"{chemicals_address}/{val_purch_chem_id_1}", json=miss_prim_key_req)
    data = miss_prim_key_response.get_json()

    assert miss_prim_key_response.status_code == 422
    assert data["error"].startswith("Request body missing primary key:")

    ### Test that primary keys in address and body match each other
    mismatch_id_response_1 = client.put(f"{chemicals_address}/1", json=valid_purchased_chemical_1)
    data = mismatch_id_response_1.get_json()

    assert mismatch_id_response_1.status_code == 422
    assert data["error"].startswith("Request body primary key does not match address <chemical_id>:")

    ### Test for a request body and address that have matching, invalid primary keys
    malformed_prim_key_req = copy.deepcopy(valid_purchased_chemical_1)
    malformed_prim_key_req[ChemicalSchema.CHEM_ID_KEY] = "1"
    
    malformed_prim_key_response = client.put(f"{chemicals_address}/1", json=malformed_prim_key_req)
    data = malformed_prim_key_response.get_json()

    assert malformed_prim_key_response.status_code == 422
    assert data["error"].startswith(ValidationErrorCodes.INVALID_ID_MSG)



# Remaining 422 status code testing
## Missing fields, missing values, wrong types, and invalid list entries
## Testing all internal schema validation failures against all combinations of
## update between purchased and prepared reagents.
@pytest.mark.parametrize("payload, expected_error_prefix", invalid_chemicals)
def test_invalid_chemicals(client, payload, expected_error_prefix, post_all_lists, post_valid_chemicals):
    (val_purch_chem_id_1,
     val_purch_chem_id_2,
     val_prep_chem_id_1,
     val_prep_chem_id_2
     ) = post_valid_chemicals
    
    # Add primary keys and aggregate fields to objects
    ## No value sent with aggregate fields should matter as they should be popped off
    id_append_val_purch_chem_1 = copy.deepcopy(payload)
    id_append_val_purch_chem_2 = copy.deepcopy(payload)
    id_append_val_prep_chem_1 = copy.deepcopy(payload)
    id_append_val_prep_chem_2 = copy.deepcopy(payload)
    id_append_val_purch_chem_1[ChemicalSchema.CHEM_ID_KEY] = val_purch_chem_id_1
    id_append_val_purch_chem_2[ChemicalSchema.CHEM_ID_KEY] = val_purch_chem_id_2
    id_append_val_prep_chem_1[ChemicalSchema.CHEM_ID_KEY] = val_prep_chem_id_1
    id_append_val_prep_chem_2[ChemicalSchema.CHEM_ID_KEY] = val_prep_chem_id_2
    id_append_val_purch_chem_1[ChemicalSchema.AVAIL_TOTAL_KEY] = 12
    id_append_val_purch_chem_2[ChemicalSchema.AVAIL_TOTAL_KEY] = "Huzzah"
    id_append_val_prep_chem_1[ChemicalSchema.AVAIL_TOTAL_KEY] = True
    id_append_val_prep_chem_2[ChemicalSchema.AVAIL_TOTAL_KEY] = None
    id_append_val_purch_chem_1[ChemicalSchema.AVAIL_OPEN_KEY] = 5.56
    id_append_val_purch_chem_2[ChemicalSchema.AVAIL_OPEN_KEY] = ("break", "me")
    id_append_val_prep_chem_1[ChemicalSchema.AVAIL_OPEN_KEY] = ["if", "you"]
    id_append_val_prep_chem_2[ChemicalSchema.AVAIL_OPEN_KEY] = {"dare": 8934868}

    # Test payloads
    val_purch_chem_1_response = client.put(f"{chemicals_address}/{val_purch_chem_id_1}", json=copy.deepcopy(id_append_val_purch_chem_1))
    val_purch_chem_2_response = client.put(f"{chemicals_address}/{val_purch_chem_id_2}", json=copy.deepcopy(id_append_val_purch_chem_2))
    val_prep_chem_1_response = client.put(f"{chemicals_address}/{val_prep_chem_id_1}", json=copy.deepcopy(id_append_val_prep_chem_1))
    val_prep_chem_2_response = client.put(f"{chemicals_address}/{val_prep_chem_id_2}", json=copy.deepcopy(id_append_val_prep_chem_2))

    val_purch_chem_1_data = val_purch_chem_1_response.get_json()
    val_purch_chem_2_data = val_purch_chem_2_response.get_json()
    val_prep_chem_1_data = val_prep_chem_1_response.get_json()
    val_prep_chem_2_data = val_prep_chem_2_response.get_json()

    if not val_purch_chem_1_data["error"].startswith(str(expected_error_prefix)):
        print(f"Payload: {payload}")
        print(f"Expected error: {expected_error_prefix}")
        print(f"Returned error: {val_purch_chem_1_data['error']}")
    assert val_purch_chem_1_data["error"].startswith(str(expected_error_prefix))
    assert val_purch_chem_1_response.status_code == 422

    if not val_purch_chem_2_data["error"].startswith(str(expected_error_prefix)):
        print(f"Payload: {payload}")
        print(f"Expected error: {expected_error_prefix}")
        print(f"Returned error: {val_purch_chem_2_data['error']}")
    assert val_purch_chem_2_data["error"].startswith(str(expected_error_prefix))
    assert val_purch_chem_2_response.status_code == 422

    if not val_prep_chem_1_data["error"].startswith(str(expected_error_prefix)):
        print(f"Payload: {payload}")
        print(f"Expected error: {expected_error_prefix}")
        print(f"Returned error: {val_prep_chem_1_data['error']}")
    assert val_prep_chem_1_data["error"].startswith(str(expected_error_prefix))
    assert val_prep_chem_1_response.status_code == 422

    if not val_prep_chem_2_data["error"].startswith(str(expected_error_prefix)):
        print(f"Payload: {payload}")
        print(f"Expected error: {expected_error_prefix}")
        print(f"Returned error: {val_prep_chem_2_data['error']}")
    assert val_prep_chem_2_data["error"].startswith(str(expected_error_prefix))
    assert val_prep_chem_2_response.status_code == 422
