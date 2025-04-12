# API Reference – CONQUEST-LIMS

This document outlines the REST API endpoints available in the CONQUEST-LIMS system for managing chemical templates, lots, and validated entry lists.

## /chemicals – Chemical Template Endpoints

### GET /chemicals
Description: Fetch all chemical templates.\
Returns:
* List of chemical documents with current aggregate fields (Available_Total, Available_Open).
* See GET /chemicals/<chemical_id> for single document structure.

### POST /chemicals
Description: Create a new chemical template.\
Returns:
* 201 Created with inserted _id, or
* 422 with validation error

Request body structures:

* Purchased chemicals:
```json
request = {
    "Name": str,               # Required.
    "CAS_Number": str,         # Required.
    "Classification": str,     # Required. Value from lists.{"Name": "Classifications"}
    "Storage_Condition": str,  # Required. Value from lists.{"Name": "Storage_Conditions"}
    "Source": str,             # Required. Value from lists.{"Name": "Sources"}
    "Purchased_Fields": {      # Required.
        "Manufacturer": str,   # Required. Value from lists.{"Name": "Manufacturers"}
        "Manufacturer_Part_Number": str,  # Required.
        "Amount": [int, float],           # Required. Either type is acceptable.
        "Units": str,                     # Required. Value from lists.{"Name": "Units"}
        "Container_Type": str             # Required. Value from lists.{"Name": "Container_Types"}
    }
}
```

* Prepared chemicals:
```json
request = {
    "Name": str,               # Required.
    "CAS_Number": str,         # Required.
    "Classification": str,     # Required. Value from lists.{"Name": "Classifications"}
    "Storage_Condition": str,  # Required. Value from lists.{"Name": "Storage_Conditions"}
    "Source": str,             # Required. Value from lists.{"Name": "Sources"}
    "Purchased_Fields": {      # Required.
        "Manufacturer": str,   # Required. Value from lists.{"Name": "Manufacturers"}
        "Manufacturer_Part_Number": str,  # Required.
        "Amount": [int, float],           # Required. Either type is acceptable.
        "Units": str,                     # Required. Value from lists.{"Name": "Units"}
        "Container_Type": str             # Required. Value from lists.{"Name": "Container_Types"}
    }
}
```

### GET /chemicals/<chemical_id>
Description: Fetch a single chemical template by _id.\

Returns:
* JSON document with updated aggregate fields.

Response body formats:
* Purchased chemicals:
```json
response = {
    "_id": str,
    "Name": str,
    "CAS_Number": str,
    "Classification": str,
    "Storage_Condition": str,
    "Source": str,
    "Purchased_Fields": {
        "Manufacturer": str,
        "Manufacturer_Part_Number": str,
        "Amount": [int, float],
        "Units": str,
        "Container_Type": str
    }
}
```

* Prepared chemicals:
```json
response = {
    "_id": str,
    "Name": str,
    "CAS_Number": str,
    "Classification": str,
    "Storage_Condition": str,
    "Source": str,
    "Prepared_Fields": {
        "Method_Step_Reference": str
    }
}
```

### PUT /chemicals/<chemical_id>
Description: Update an existing chemical template.\
Returns:
* 200 OK with modified count or appropriate error code.

Request body formats:

* Purchased chemicals:
```json
request = {
    "_id": str,                # Required. Convertable to a ObjectId(). Primary key.
    "Name": str,               # Required.
    "CAS_Number": str,         # Required.
    "Classification": str,     # Required. Value from lists.{"Name": "Classifications"}
    "Storage_Condition": str,  # Required. Value from lists.{"Name": "Storage_Conditions"}
    "Source": str,             # Required. Value from lists.{"Name": "Sources"}
    "Purchased_Fields": {      # Required.
        "Manufacturer": str,   # Required. Value from lists.{"Name": "Manufacturers"}
        "Manufacturer_Part_Number": str,  # Required.
        "Amount": [int, float],           # Required. Either type is acceptable.
        "Units": str,                     # Required. Value from lists.{"Name": "Units"}
        "Container_Type": str             # Required. Value from lists.{"Name": "Container_Types"}
    }
}
```

* Prepared chemicals:
```json
request = {
    "_id": str,                # Required. Convertable to a ObjectId(). Primary key.
    "Name": str,               # Required.
    "CAS_Number": str,         # Required.
    "Classification": str,     # Required. Value from lists.{"Name": "Classifications"}
    "Storage_Condition": str,  # Required. Value from lists.{"Name": "Storage_Conditions"}
    "Source": str,             # Required. Value from lists.{"Name": "Sources"}
    "Purchased_Fields": {      # Required.
        "Manufacturer": str,   # Required. Value from lists.{"Name": "Manufacturers"}
        "Manufacturer_Part_Number": str,  # Required.
        "Amount": [int, float],           # Required. Either type is acceptable.
        "Units": str,                     # Required. Value from lists.{"Name": "Units"}
        "Container_Type": str             # Required. Value from lists.{"Name": "Container_Types"}
    }
}
```

### DELETE /chemicals/<chemical_id>
Description: Delete a chemical template by _id.\
Returns:
* 204 No Content or 404 Not Found

## /lots – Lot Management Endpoints
### GET /lots
Description: Fetch all lot records.\
Returns:
* List of JSON-serializable lot documents.

Request body formats for single document:
* Purchased lots
```json
response = {
    "_id": str,
    "chemical_id": str,
    "Name": str,
    "CAS_Number": str,
    "Classification": str,
    "Storage_Condition": str,
    "Source": str,
    "Purchased_Fields": {
        "Manufacturer": str,
        "Manufacturer_Part_Number": str,
        "Manufacturer_Lot_Batch_Number": str,
        "Amount": [int, float],
        "Units": str,
        "Container_Type": str
    }
    "Open_Date": str,
    "Expiry_Date": str,
    "Empty_Date": str
}
```
* Prepared lots
```json
response = {
    "_id": str,
    "chemical_id": str,
    "Name": str,
    "CAS_Number": str,
    "Amount": [int, float],
    "Units": str,
    "Container_Type": str,
    "Classification": str,
    "Storage_Condition": str,
    "Source": str,
    "Prepared_Fields": {
        "Method_Step_Reference": str,
    }
    "Preparation_Date": str,
    "Expiry_Date": str,
    "Empty_Date": str,
    "Components": [  # List of dicts, one component per dict
        # Purchased chemical/lot component
        {
            "lot_id": ObjectId,
            "Name": str,
            "Manufacturer": str,
            "Manufacturer_Part_Number": str,
            "Manufacturer_Lot_Batch_Number": str,
            "Amount": [int, float],                # Either is allowed.
            "Units": str,
            "Expiry_Date": datetime
        },
        # Prepared chemical/lot component
        {
            "lot_id": ObjectId,
            "Name": str,
            "Method_Step_Reference": str,
            "Amount": [int, float],
            "Units": str,
            "Expiry_Date": datetime
        }
    ]
}
```

### POST /lots
Description: Add a new lot for an existing chemical.\
Returns:
* 201 Created or validation error

Request body formats:
* Purchased and prepared components currently have redundant schema but are defined separately in case of future divergence.
* Purchased lots
```json
request = {
    "_id": str,                            # Required. Convertable to ObjectId(). Primary key.
    "chemical_id": str,                    # Required. Links to chemicals._id of existing chemical.
    "Manufacturer_Lot_Batch_Number": str,  # Required.
    "Open_Date": str,                      # Optional. Timezone-aware ISO 8601 string.
    "Expiry_Date": str,                    # Required. Timezone-aware ISO 8601 string.
    "Empty_Date": str,                     # Optional. Timezone-aware ISO 8601 string.
}
```
* Prepared lots:
```json
request = {
    "_id": str,               # Required. Convertable to ObjectId(). Primary key.
    "chemical_id": str,       # Required. Links to chemicals._id of existing chemical.
    "Amount": [int, float],   # Required. Either type is acceptable.
    "Units": str,             # Required. Value from lists.{"Name": "Units"}
    "Container_Type": str,    # Required. Value from lists.{"Name": "Container_Types"}
    "Preparation_Date": str,  # Required. Timezone-aware ISO 8601 string.
    "Expiry_Date": str,       # Required. Timezone-aware ISO 8601 string.
    "Empty_Date": str,        # Optional. Timezone-aware ISO 8601 string.
    "Components": [           # Requires >= 1 components.
        {
            "lot_id": str,           # Required. Primary key of an existing lot.
            "Amount": [int, float],  # Required. Either type is acceptable.
            "Units": str             # Required. Value from lists.{"Name": "Units"}
        },
        # Prepared chemical/lot components
        {
            "lot_id": str,           # Required. Primary key of an existing lot.
            "Amount": [int, float],  # Required. Either type is acceptable.
            "Units": str             # Required. Value from lists.{"Name": "Units"}
        }
    ]
}
```

### GET /lots/<lot_id>
Description: Fetch single lot by _id.\
Returns:
* JSON lot document
* See GET /lots/ for single document structure.

### PUT /lots/<lot_id>
Description: Update an existing lot\
Returns:
* 200 OK or validation errors

Request body structure:
* Purchased lots:
```json
request = {
    "_id": str,                            # Required. Convertable to ObjectId(). Primary key.
    "chemical_id": str,                    # Required. Links to chemicals._id of existing chemical.
    "Manufacturer_Lot_Batch_Number": str,  # Required.
    "Open_Date": str,                      # Optional. Timezone-aware ISO 8601 string.
    "Expiry_Date": str,                    # Required. Timezone-aware ISO 8601 string.
    "Empty_Date": str,                     # Optional. Timezone-aware ISO 8601 string.
}
```
* Prepared lots:
```json
request = {
    "_id": str,               # Required. Convertable to ObjectId(). Primary key.
    "chemical_id": str,       # Required. Links to chemicals._id of existing chemical.
    "Amount": [int, float],   # Required. Either type is acceptable.
    "Units": str,             # Required. Value from lists.{"Name": "Units"}
    "Container_Type": str,    # Required. Value from lists.{"Name": "Container_Types"}
    "Preparation_Date": str,  # Required. Timezone-aware ISO 8601 string.
    "Expiry_Date": str,       # Required. Timezone-aware ISO 8601 string.
    "Empty_Date": str,        # Optional. Timezone-aware ISO 8601 string.
    "Components": [           # Requires >= 1 components.
        {
            "lot_id": str,           # Required. Primary key of an existing lot.
            "Amount": [int, float],  # Required. Either type is acceptable.
            "Units": str             # Required. Value from lists.{"Name": "Units"}
        },
        # Prepared chemical/lot components
        {
            "lot_id": str,           # Required. Primary key of an existing lot.
            "Amount": [int, float],  # Required. Either type is acceptable.
            "Units": str             # Required. Value from lists.{"Name": "Units"}
        }
    ]
}
```

### DELETE /lots/<lot_id>
Description: Remove lot from database\
Returns:
* 204 No Content or 404 Not Found

## /lists – Controlled Vocabulary List Endpoints
### GET /lists
Description: Return all list templates.\
Returns:
* List of all field list documents.

Response body format for single document:
```json
response = {
    "Name": str,
    "List_entries: [
        str
    ]
}
```

### POST /lists
Description: Add a new list.\
Returns:
* 201 Created or 422 validation error

Request body format:
```json
request = {
    "Name": str,
    "List_entries: [
        str
    ]
}
```

### GET /lists/<list_name>
Description: Return entries for a specific list.\
Returns:
* JSON list document
* See GET /lists for response body format.

### PUT /lists/<list_name>
Description: Update an existing list.\
Returns:
* 200 OK or 404 if not found

Request body format:
* See POST /lists for request body format.


### DELETE /lists/<list_name>
Description: Delete a list from the database.\
Returns:
* 204 No Content








## Error Handling

All endpoints return errors with the following format:
```json
{
  "error": "<descriptive message>"
}
```