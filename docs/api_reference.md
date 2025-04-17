# API Reference – CONQUEST-LIMS

This document outlines the REST API endpoints available in the CONQUEST-LIMS system for managing chemical templates, lots, and validated entry lists.

## `/chemicals` – Chemical Template Endpoints

### `GET /chemicals`
Description:\
Retrieves all chemical template records from the database. Aggregate totals are refreshed before returning results.

Returns:\
Tuple[Response, int]: JSON response containing all chemical templates and status code 200.

Response body formats:
* Purchased chemicals:
```json
response = [
    {
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
        },
        "Total_Available_Lots": int,
        "Total_Open_Lots": int
    }
]
```
* Prepared chemicals:
```json
response = [
    {
        "_id": str,
        "Name": str,
        "CAS_Number": str,
        "Classification": str,
        "Storage_Condition": str,
        "Source": str,
        "Prepared_Fields": {
            "Method_Step_Reference": str
        },
        "Total_Available_Lots": int,
        "Total_Open_Lots": int
    }
]
```

### `POST /chemicals`
Description:\
Adds a new chemical template to the database. Requests are validated against database schema prior to insertion.

Returns:\
Tuple[Response, int]: JSON response with inserted ID and status code 201 on success or an error message with appropriate 4XX code on failure.

Request body structures:

* Purchased chemicals:
```json
request = {
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

# Name: Required.
# CAS_Number: Required.
# Classification: Required. Value from lists {"Name": "Classifications"}
# Storage_Condition: Required. Value from lists {"Name": "Storage_Conditions"}
# Source: Required. Value from lists {"Name": "Sources"}
# Purchased_Fields: Required.
# Manufacturer: Required. Value from lists {"Name": "Manufacturer"}
# Manufacturer_Part_Number: Required.
# Amount: Required. Either type is acceptable.
# Units: Required. Value from lists {"Name": "Units"}
# Container_Type: Required. Value from lists {"Name": "Container_Type"}
```

* Prepared chemicals:
```json
request = {
    "Name": str,
    "CAS_Number": str,
    "Classification": str,
    "Storage_Condition": str,
    "Source": str,
    "Prepared_Fields": {
        "Method_Step_Reference": str
    }
}

# Name: Required.
# CAS_Number: Required.
# Classification: Required. Value from lists {"Name": "Classifications"}
# Storage_Condition: Required. Value from lists {"Name": "Storage_Conditions"}
# Source: Required. Value from lists {"Name": "Sources"}
# Prepared_Fields: Required.
# Method_Step_Reference: Required.
```

### `GET /chemicals/<chemical_id>`
Description:\
Retrieves a single chemical template by its primary key.

Returns:\
Tuple[Response, int]: JSON response with the chemical record and status 200 or a 400/404 error response on failure.

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
    },
    "Total_Available_Lots": int,
    "Total_Open_Lots": int
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
    },
    "Total_Available_Lots": int,
    "Total_Open_Lots": int
}
```

### `PUT /chemicals/<chemical_id>`
Description:\
Updates a chemical template by primary key. Requests are validated against database schema prior to modification.

Returns:\
Tuple[Response, int]: JSON response with modified count and status 200 on success or error response with status 400, 404, or 422.

Request body formats:

* Purchased chemicals:
```json
request = {
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

# _id: Required. Convertible to ObjectId(). Primary key.
# Name: Required.
# CAS_Number: Required.
# Classification: Required. Value from lists {"Name": "Classifications"}
# Storage_Condition: Required. Value from lists {"Name": "Storage_Conditions"}
# Source: Required. Value from lists {"Name": "Sources"}

# Purchased_Fields: Required.
# Manufacturer: Required. Value from lists {"Name": "Manufacturer"}
# Manufacturer_Part_Number: Required
# Amount: Required. Either type is acceptable.
# Units: Required. Value from lists {"Name": "Units"}
# Container_Type: Required. Value from lists {"Name": "Container_Type"}
```

* Prepared chemicals:
```json
request = {
    "_id": str,
    "Name": str,
    "CAS_Number": str,
    "Classification": str,
    "Storage_Condition": str,
    "Source": str,
    "Prepared_Fields": {
        "Method_Step_Reference": str
    },
    "Total_Available_Lots": int,
    "Total_Open_Lots": int
}

# _id: Required. Convertible to ObjectId(). Primary key.
# Name: Required.
# CAS_Number: Required.
# Classification: Required. Value from lists {"Name": "Classifications"}
# Storage_Condition: Required. Value from lists {"Name": "Storage_Conditions"}
# Source: Required. Value from lists {"Name": "Sources"}

# Prepared_Fields: Required.
# Method_Step_Reference: Required.

# Total_Available_Lots: Initialized on POST /chemicals. Recalculated on POST/PUT /lots or GET/PUT /chemicals.
# Total_Open_Lots: Initialized on POST /chemicals. Recalculated on POST/PUT /lots or GET/PUT /chemicals.
```

### `DELETE /chemicals/<chemical_id>`
Description:\
Deletes a chemical template by its primary key.

Returns:\
Tuple[Response, int]: JSON response with deleted count and status 204 on success or error response with status 400 or 404.

### `GET /chemicals/search?query=key+words`
Description:\
Full-text search for chemicals by name.

Returns:\
JSON list of matching chemical records with partial or full name matches.

Response body format:
```json
response =[
    {
        "Mongo_Collection": str,
        "Name": str,
        "Mongo_id": str,
        "_id": str,
        "score": float
    }
]

# Mongo_Collection: The name of the MongoDB collection the document originates from.
# Name: The name of the chemical template.
# Mongo_id: The primary key of the corresponding database record.
# _id: Elasticsearch auto-generated primary key
# score: The result's relevance score
```

## `/lots` – Lot Management Endpoints
### `GET /lots`
Description:\
Retrieve all lot documents from the database and convert non-JSON-serializable fields to JSON-serializable types.

Returns:\
Tuple[Response, int]: A JSON response with all lot records and status code 200.

Response body formats:
* Purchased lots
```json
response = [
    {
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
        },
        "Open_Date": str,
        "Expiry_Date": str,
        "Empty_Date": str
    }
]
```
* Prepared lots
```json
response = [
    {
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
            "Method_Step_Reference": str
        },
        "Preparation_Date": str,
        "Expiry_Date": str,
        "Empty_Date": str,
        "Components": [
            # Purchased chemical/lot components
            {
                "lot_id": str,
                "Name": str,
                "Manufacturer": str,
                "Manufacturer_Part_Number": str,
                "Manufacturer_Lot_Batch_Number": str,
                "Amount": [int, float],
                "Units": str,
                "Expiry_Date": str
            },
            # Prepared chemical/lot components
            {
                "lot_id": str,
                "Name": str,
                "Method_Step_Reference": str,
                "Amount": [int, float],
                "Units": str,
                "Expiry_Date": str
            }
        ]
    }
]
```

### `POST /lots`
Description:\
Add a new lot to the database. Requests are validated against database schema prior to insertion.

Returns:\
Tuple[Response, int]: JSON response with inserted ID (201) or error message (4XX) if validation fails.

Request body formats:
* Purchased and prepared components currently have redundant schema but are defined separately in case of future divergence.
* Purchased lots:
```json
request = {
    "chemical_id": str,
    "Manufacturer_Lot_Batch_Number": str,
    "Open_Date": str,
    "Expiry_Date": str,
    "Empty_Date": str
}

# chemical_id: Required. Links to chemicals._id of existing chemical.
# Manufacturer_Lot_Batch_Number: Required.
# Open_Date: Optional. Timezone-aware ISO 8601 string (UTC offset of the form +00:00).
# Expiry_Date: Required. Timezone-aware ISO 8601 string (UTC offset of the form +00:00).
# Empty_Date: Optional. Timezone-aware ISO 8601 string (UTC offset of the form +00:00).
```
* Prepared lots:
```json
request = {
    "chemical_id": str,
    "Amount": [int, float],
    "Units": str,
    "Container_Type": str,
    "Preparation_Date": str,
    "Expiry_Date": str,
    "Empty_Date": str,
    "Components": [
        # Purchased chemical/lot components
        {
            "lot_id": str,
            "Amount": [int, float],
            "Units": str
        },
        # Prepared chemical/lot components
        {
            "lot_id": str,
            "Amount": [int, float],
            "Units": str
        }
    ]
}

# chemical_id: Required. Links to chemicals._id of existing chemical.
# Amount: Required. Either type is acceptable.
# Units: Required. Value from lists {"Name": "Units"}
# Container_Type: Required. Value from lists {"Name": "Container_Type"}
# Preparation_Date: Required. Timezone-aware ISO 8601 string (UTC offset of the form +00:00).
# Expiry_Date: Required. Timezone-aware ISO 8601 string (UTC offset of the form +00:00).
# Empty_Date: Optional. Timezone-aware ISO 8601 string (UTC offset of the form +00:00).

# Components: Required. Requires >= 1 components.

# Purchased chemical/lot components
# lot_id: Required. Primary key of an existing lot.
# Amount: Required. Either type is acceptable.
# Units: Required. Value from lists {"Name": "Units"}

# Prepared chemical/lot components
# lot_id: Required. Primary key of an existing lot.
# Amount: Required. Either type is acceptable.
# Units: Required. Value from lists {"Name": "Units"}
```

### `GET /lots/<lot_id>`
Description:\
Retrieve a lot record by primary key.

Returns:\
Tuple[Response, int]: JSON-formatted lot or error message with code 4XX.

Response body formats:
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
    },
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
        "Method_Step_Reference": str
    },
    "Preparation_Date": str,
    "Expiry_Date": str,
    "Empty_Date": str,
    "Components": [
        # Purchased chemical/lot components
        {
            "lot_id": str,
            "Name": str,
            "Manufacturer": str,
            "Manufacturer_Part_Number": str,
            "Manufacturer_Lot_Batch_Number": str,
            "Amount": [int, float],
            "Units": str,
            "Expiry_Date": str
        },
        # Prepared chemical/lot components
        {
            "lot_id": str,
            "Name": str,
            "Method_Step_Reference": str,
            "Amount": [int, float],
            "Units": str,
            "Expiry_Date": str
        }
    ]
}
```

### `PUT /lots/<lot_id>`
Description:\
Update an existing lot record by primary key. Requests are validated against database schema prior to modification.

Returns:\
Tuple[Response, int]: Modified count or JSON-formatted error message and a 4XX error code.

Request body structure:
* Purchased lots:
```json
request = {
    "_id": str,
    "chemical_id": str,
    "Manufacturer_Lot_Batch_Number": str,
    "Open_Date": str,
    "Expiry_Date": str,
    "Empty_Date": str
}

# _id: Required. Convertible to ObjectId(). Primary key.
# chemical_id: Required. Links to chemicals._id of existing chemical.
# Manufacturer_Lot_Batch_Number: Required.
# Open_Date: Optional. Timezone-aware ISO 8601 string (UTC offset of the form +00:00).
# Expiry_Date: Required. Timezone-aware ISO 8601 string (UTC offset of the form +00:00).
# Empty_Date: Optional. Timezone-aware ISO 8601 string (UTC offset of the form +00:00).
```
* Prepared lots:
```json
request = {
    "_id": str,
    "chemical_id": str,
    "Amount": [int, float],
    "Units": str,
    "Container_Type": str,
    "Preparation_Date": str,
    "Expiry_Date": str,
    "Empty_Date": str,
    "Components": [
        # Purchased chemical/lot components
        {
            "lot_id": str,
            "Amount": [int, float],
            "Units": str
        },
        # Prepared chemical/lot components
        {
            "lot_id": str,
            "Amount": [int, float],
            "Units": str
        }
    ]
}

# _id: Required. Convertible to ObjectId(). Primary key.
# chemical_id: Required. Links to chemicals._id of existing chemical.
# Amount: Required. Either type is acceptable.
# Units: Required. Value from lists {"Name": "Units"}
# Container_Type: Required. Value from lists {"Name": "Container_Type"}
# Preparation_Date: Required. Timezone-aware ISO 8601 string (UTC offset of the form +00:00).
# Expiry_Date: Required. Timezone-aware ISO 8601 string (UTC offset of the form +00:00).
# Empty_Date: Optional. Timezone-aware ISO 8601 string (UTC offset of the form +00:00).

# Components: Required. Requires >= 1 components.

# Purchased chemical/lot components
# lot_id: Required. Primary key of an existing lot.
# Amount: Required. Either type is acceptable.
# Units: Required. Value from lists {"Name": "Units"}

# Prepared chemical/lot components
# lot_id: Required. Primary key of an existing lot.
# Amount: Required. Either type is acceptable.
# Units: Required. Value from lists {"Name": "Units"}
```

### `DELETE /lots/<lot_id>`
Description:\
Delete a lot by primary key.

Returns:\
Tuple[Response, int]: HTTP code 204 on success or 404 if not found.

### `GET /lots/search?query=key+words`
Description:\
Full-text search for lots by name.

Returns:\
JSON list of matching lot records with partial or full name matches.

Response body format for single documents:
* Purchased lots:
```json
response = [
    {
        "Mongo_Collection": str,
        "Name": str,
        "Mongo_id": str,
        "Expiry_Date": str,
        "Empty_Date": str,
        "Open_Date": str,
        "_id": str,
        "score": float
    }
]

# Mongo_Collection: The name of the MongoDB collection the document originates from.
# Name: The name of the chemical template the lot is logged under.
# Mongo_id: The primary key of the corresponding database record.
# Expiry_Date: See database schema for more information.
# Empty_Date: See database schema for more information.
# Open_Date: See database schema for more information.
# _id: Elasticsearch auto-generated primary key
# score: The result's relevance score
```
* Prepared lots:
```json
response = [
    {
        "Mongo_Collection": str,
        "Name": str,
        "Mongo_id": str,
        "Expiry_Date": str,
        "Empty_Date": str,
        "Preparation_Date": str,
        "_id": str,
        "score": float
    }
]

# Mongo_Collection: The name of the MongoDB collection the document originates from.
# Name: The name of the chemical template the lot is logged under.
# Mongo_id: The primary key of the corresponding database record.
# Expiry_Date: See database schema for more information.
# Empty_Date: See database schema for more information.
# Preparation_Date: See database schema for more information.
# _id: Elasticsearch auto-generated primary key
# score: The result's relevance score
```

### `GET /lots/analytics`
Description:\
Returns analytics related to the lots collection.

Returns:\
JSON object with: the total number of available lots logged in the system, the number of lots awaiting disposal (expired but not empty), and the name of the chemical with the most lots logged under its primary key.

Response body format:
```json
{
  "lots_awaiting_disposal": int,
  "most_populous_chemicals": [
    str,
    str,
    str
  ],
  "total_lots_all_chemicals": int
}

# lots_awaiting_disposal: The number of expired lots that haven't been emptied.
# most_populous_chemicals: The three chemicals with the most lots logged under their primary key.
# total_lots_all_chemicals: The total number of non-expired, non-empty lots logged in the system.
```
## `/lists` – Controlled Vocabulary List Endpoints
### `GET /lists`
Description:\
Retrieve all list documents from the database.

Returns:\
Tuple[Response, int]: A JSON response containing all lists and a 200 status code.

Response body format:
```json
response = [
    {
        "Name": str,
        "List_entries": [
            str
        ]
    }
]
```

### `POST /lists`
Description:\
Add a new validated list to the database. Requests are validated against database schema prior to insertion.

Returns:\
Tuple[Response, int]: A JSON response containing the inserted ID and a 201 status code or an error message with a 4XX status code if validation fails.

Request body format:
```json
request = {
    "Name": str,
    "List_entries": [
        str
    ]
}

# Name: Required. Must be unique. Primary key.
# List_entries: Required. Lists must have at least one entry.
# (List entries): At least one entry required.
```

### `GET /lists/<list_name>`
Description:\
Retrieve a specific list by primary key ("Name").

Returns:\
Tuple[Response, int]: JSON response with list data and status 200 or an error message with status 404 if not found.

Response body format:
```json
response = {
    "Name": str,
    "List_entries": [
        str
    ]
}
```

### `PUT /lists/<list_name>`
Description:\
Update an existing list by primary key ("Name"). Requests are validated against database schema prior to modification.

Returns:\
Tuple[Response, int]: JSON response with modified count and status 200 on success or an error message with status 404 or 422 on failure.


Request body format:
```json
request = {
    "Name": str,
    "List_entries": [
        str
    ]
}

# Name: Required. Must be unique. Primary key.
# List_entries: Required. Lists must have at least one entry.
# (List entries): At least one entry required.
```


### `DELETE /lists/<list_name>`
Description:\
Delete a validated list from the database by primary key ("Name"). This action is not recommended in production environments. Deleting certain lists can break the chemical inventory system.

Returns:\
Tuple[Response, int]: Empty response with 204 on success or error message with 404 if the list is not found.

## Error Handling

All endpoints return errors with the following format:
```json
{
  "error": "<descriptive message>"
}
```