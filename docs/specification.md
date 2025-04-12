# CONQUEST-LIMS Specifications
## Overview
CONQUEST-LIMS is a lightweight laboratory information management system (LIMS) designed to track chemical inventory in highly-regulated laboratory settings. It supports record creation, retrieval, update, and deletion of:
* Chemical templates
* Lot records (tied to chemicals)
* Lists for constraining validated field entries (Approved manufacturers, classification, unit, etc.)

### Functionality Overview
Chemical templates store information on a given, unique combination of manufacturer, manufacturer part number, amount, unit, and container type. In order to avoid system bloat and to prevent entry error, no two chemicals with the same combination of the aforementioned attributes can exist. "Chemicals" serve as a template against which individual bottles of standards or reagents, otherwise known as lots. Two given bottles of a lot may have the exact same values for every item in the lot and chemical fields as is often the case in a lab when multiple bottles of the same batch are received. Lots are thus distinguished by their internal lot number, which currently corresponds to the "_id" field primary key assigned by MongoDB upon record creation.

Information common to all lots of a given chemical is stored on the chemical document. Lot documents are linked to their parent chemical template record via the lots.chemical_id field, where lots.chemical_id corresponds to the primary key of a chemicals document: chemicals._id. Upon lot creation, all chemical data will be duplicated onto the lot record using the parent chemical form; lot requests only require information unique to the given lot being logged.

The addition of chemical templates is a highly validated process that constrains user entry in every way imaginable to prevent errors and to ensure the system will function in a regulated environment. Chemical templates must first be logged before a lot can be logged using that template. Chemical/lot related objects are split into purchased chemicals/lots and prepared chemicals/lots which further takes advantage of the flexibility of MongoDB's document-based design as each class of chemical/lot stores slightly different information with each group containing at least one unique field from the other. Purchased lots are logged as standards or reagents purchased from a manufacturer. They may then be used in testing, or otherwise as components to create prepared lots. Prepared lots are logged as standards or reagents prepared in-house and they accept one or more components to document their preparation. Each component used must come from an existing lot logged into the system, and they are linked on the fields lots.Components.lot_id = lots._id where lot_id is the primary key of a lot logged into the system. Each component additionally documents the amount and units used in preparation of the prepared standard or reagent lot.

Chemical and lot creation is in part controlled by the use of validated entry fields with acceptable inputs governed by lists that can be modified as needed. This further serves to harmonize data entry across the system and across multiple users. Examples include approved manufacturers, units, storage conditions, container types, *etc.* The name of each list is governed by the name of a linked field in the chemicals document schema, as are also many fields on lot documents governed by linked fields on the chemicals template.

Chemical documents also store information on the total number of lots available and open for use logged under the chemical's lots.chemical_id. These will be refreshed any time a lot is added or updated, or any time a chemical template is updated or retrieved.

## Design Philosophy
Chemical data are duplicated onto lot records in an attempt to work with the document-based database idea that information commonly accessed together should be stored together. Analysts in the lab will commonly need to access a list of all available lots, or at least all lots for a given chemical. At the expense of marginally larger documents, all required information for a given lot (chemical plus lot) can be pulled in one query. At the same time, lot creation requests, which are by far a more common occurrence than chemical creation requests, are vastly simplified as the front end is able to safely ignore the need to send anything but information related directly to the unique bottle in the analyst's hands, thus reducing the chance for errors to occur. Finally, the collections remain split because there are many instances in which an analyst may need to view all classes of chemicals in the system. Lot data would be useless in such a case.

All records are stored in MongoDB and served via a Flask-based API. Validation is enforced at the schema level through dedicated classes to ensure data harmonization and integrity.

## Important Usage Information
* lots.chemical_id links to chemicals._id.
* lots.Components.lot_id links to lots._id.
* Optional fields are required to be sent with an empty value of either `None` type or of the type specified in the schema. The key cannot be missing.
* Do not attempt a PUT request to update a chemical template with the template of another chemical whose lots would need to use the first chemical, the replaced one, as a component. This cannot be enforced until and unless the system is changed to operate in a more rigorous fashion where chemical templates also prescribe prepared lot components and amounts (see ["Future Upgrades"](#future-upgrades)).

## Architecture
### Backend Stack
* Language: Python 3.10+
* Framework: Flask
* Database: MongoDB (accessed via pymongo)
* Testing: pytest, mongomock
* Containerization: Docker

## Project Structure
```bash
CONQUEST-LIMS/
│
├── app/
│   ├── __init__.py               # Initializes Flask app and MongoDB client
│   ├── api/                      # Flask Blueprints for API endpoints
│   │   ├── chemicals.py
│   │   ├── lists.py
│   │   └── lots.py
│   │
│   ├── models/                   # Schema validation and transformation classes
│   │   ├── chemicals.py
│   │   ├── lists.py
│   │   └── lots.py
│   │
│   └── utils/                    # Supporting validation logic and constants
│       ├── helper_functions.py
│       └── validation_error_codes.py
│    
├── docs/
│   ├── api_reference.md          # Documentation for API end points
│   └── specifications.md         # This document
│
├── k8s/                          # Kubernetes deployment files
│
│
├── tests/                        # Full test suite for each module and edge cases
├── run.py                        # Entrypoint to run the Flask app
├── requirements.txt
└── Dockerfile                    # Defines the container image for the application
```

## API Endpoints

All endpoints return proper HTTP status codes, follow RESTful practices, and expect JSON payloads.

### Lists

| Method | Endpoint                 | Description                  |
|--------|--------------------------|------------------------------|
| GET    | /lists/                  | Get all lists records        |
| POST   | /lists/                  | Add a new lists template     |
| GET    | /lists/&lt;list_name&gt; | Fetch a specific lists by ID |
| PUT    | /lists/&lt;list_name&gt; | Update a lists template      |
| DELETE | /lists/&lt;list_name&gt; | Delete a lists template      |

### Chemicals

| Method | Endpoint                       | Description                     |
|--------|--------------------------------|---------------------------------|
| GET    | /chemicals/                    | Get all chemical records        |
| POST   | /chemicals/                    | Add a new chemical template     |
| GET    | /chemicals/&lt;chemical_id&gt; | Fetch a specific chemical by ID |
| PUT    | /chemicals/&lt;chemical_id&gt; | Update a chemical template      |
| DELETE | /chemicals/&lt;chemical_id&gt; | Delete a chemical template      |

### Lots

| Method | Endpoint              | Description                 |
|--------|-----------------------|-----------------------------|
| GET    | /lots/                | Get all lots records        |
| POST   | /lots/                | Add a new lots template     |
| GET    | /lots/&lt;lots_id&gt; | Fetch a specific lots by ID |
| PUT    | /lots/&lt;lots_id&gt; | Update a lots template      |
| DELETE | /lots/&lt;lots_id&gt; | Delete a lots template      |

## Data Schema
The following represent the database schema for each object type:

* Purchased chemicals:
```json
record = {
    "_id": ObjectId,                      # Required. Convertible to ObjectId(). Primary key.
    "Name": str,                          # Required.
    "CAS_Number": str,                    # Required.
    "Classification": str,                # Required. Value from lists {"Name": "Classifications"}
    "Storage_Condition": str,             # Required. Value from lists {"Name": "Storage_Conditions"}
    "Source": str,                        # Required. Value from lists {"Name": "Sources"}
    "Purchased_Fields": {                 # Required.
        "Manufacturer": str,              # Required. Value from lists {"Name": "Manufacturer"}
        "Manufacturer_Part_Number": str,  # Required
        "Amount": [int, float],           # Required. Either type is acceptable.
        "Units": str,                     # Required. Value from lists {"Name": "Units"}
        "Container_Type": str             # Required. Value from lists {"Name": "Container_Types"}
    }
    "Total_Available_Lots": int,               # Initialized on POST /chemicals. Recalculated on POST/PUT /lots or GET/PUT /chemicals.
    "Total_Open_Lots": int                 # Initialized on POST /chemicals. Recalculated on POST/PUT /lots or GET/PUT /chemicals.
}
```
* Prepared chemicals:
```json
record = {
    "_id": ObjectId,                   # Required. Convertible to ObjectId(). Primary key.
    "Name": str,                       # Required.
    "CAS_Number": str,                 # Required.
    "Classification": str,             # Required. Value from lists {"Name": "Classifications"}
    "Storage_Condition": str,          # Required. Value from lists {"Name": "Storage_Conditions"}
    "Source": str,                     # Required. Value from lists {"Name": "Sources"}
    "Prepared_Fields": {               # Required.
        "Method_Step_Reference": str   # Required.
    }
    "Total_Available_Lots": int,       # Initialized on POST /chemicals. Recalculated on POST/PUT /lots or GET/PUT /chemicals.
    "Total_Available_Open": int        # Initialized on POST /chemicals. Recalculated on POST/PUT /lots or GET/PUT /chemicals.
}
```
* Purchased lots:
```json
record = {
    "_id": ObjectId,                           # Required. Convertible to ObjectId(). Primary key.
    "chemical_id": ObjectId,                   # Required. Links to chemicals._id of existing chemical.
    "Name": str,                               # Required. From parent chemical.
    "CAS_Number": str,                         # Required. From parent chemical.
    "Classification": str,                     # Required. From parent chemical.
    "Storage_Condition": str,                  # Required. From parent chemical.
    "Source": str,                             # Required. From parent chemical.
    "Purchased_Fields": {                      # Required. From parent chemical.
        "Manufacturer": str,                   # Required. From parent chemical.
        "Manufacturer_Part_Number": str,       # Required. From parent chemical.
        "Manufacturer_Lot_Batch_Number": str,  # Required.
        "Amount": [int, float],                # Required. From parent chemical. Either type.
        "Units": str,                          # Required. From parent chemical.
        "Container_Type": str                  # Required. From parent chemical.
    }
    "Open_Date": datetime,                     # Optional. Timezone-aware ISO 8601 string.
    "Expiry_Date": datetime,                   # Required. Timezone-aware ISO 8601 string.
    "Empty_Date": datetime                     # Optional. Timezone-aware ISO 8601 string.
}
```
* Prepared lots
```json
record = {
    "_id": ObjectId,                               # Required. Convertible to ObjectId(). Primary key.
    "chemical_id": ObjectId,                       # Required. Links to chemicals._id of existing chemical.
    "Name": str,                                   # Required. From parent chemical.
    "CAS_Number": str,                             # Required. From parent chemical.
    "Amount": [int, float],                        # Required. Either type.
    "Units": str,                                  # Required. Value from lists {"Name": "Units"}
    "Container_Type": str,                         # Required. Value from lists {"Name": "Container_Types"}
    "Classification": str,                         # Required. From parent chemical.
    "Storage_Condition": str,                      # Required. From parent chemical.
    "Source": str,                                 # Required. From parent chemical.
    "Prepared_Fields": {                           # Required. From parent chemical.
        "Method_Step_Reference": str               # Required. From parent chemical.
    }
    "Preparation_Date": datetime,                  # Required. Timezone-aware ISO 8601 string.
    "Expiry_Date": datetime,                       # Required. Timezone-aware ISO 8601 string.
    "Empty_Date": datetime,                        # Optional. Timezone-aware ISO 8601 string.
    "Components": [                                # Required. Must be >= 1 components.
        {
            "lot_id": ObjectId,                    # Required. Primary key of an existing lot.
            "Name": str,                           # Required. From parent chemical.
            "Manufacturer": str,                   # Required. From parent chemical.
            "Manufacturer_Part_Number": str,       # Required. From parent chemical.
            "Manufacturer_Lot_Batch_Number": str,  # Required. From parent chemical.
            "Amount": [int, float],                # Required. Either type is acceptable.
            "Units": str,                          # Required. Value from lists {"Name": "Units"}
            "Expiry_Date": datetime                # Required. From parent chemical.
        },
        # Prepared chemical/lot component
        {
            "lot_id": ObjectId,                    # Required. Primary key of an existing lot.
            "Name": str,                           # Required. From parent chemical.
            "Method_Step_Reference": str,          # Required. From parent chemical.
            "Amount": [int, float],                # Required. Either type is acceptable.
            "Units": str,                          # Required. Value from lists {"Name": "Units"}
            "Expiry_Date": datetime                # Required. From parent chemical.
        }
    ]
}
```
* Lists
```json
record = {
    "_id": ObjectId,        # Not managed. MongoDB default primary key.
    "Name": str,            # Required. Must be unique. Primary key.
    "List_entries: [        # Required. Lists must have at least one entry.
        str                 # Required.
    ]
}
```

## Validation Strategy

Each database schema (Chemical, Lot, List) has a corresponding class (ChemicalSchema, LotSchema, ListsSchema) which verifies, as necessary and in some cases in addition to the end points, that:

### All Schema:
* All required fields are present.
* All required values are present.
* No extra fields are present.
* All fields have the correct type.
* Validated entry field values exist in their corresponding validated entry list.
* Primary keys are not malformed:
    * Chemicals and lots: The system checks to ensure any ID key is a valid object of the type ObjectId().
    * Lists: List documents do not use MongoDB's "_id" as their primary key; list requests are validated to ensure the "Name" field is unique.
* Primary keys match in the incoming request body and request address.

### Chemicals:
* Requests to update existing chemical templates contain the ID of a valid chemical template in the database (expired chemicals are still allowed to be added as components).
* When adding a purchased chemical, the system checks to see if the requested combination of manufacturer, manufacturer part number, amount, unit, and container type already exists in the database to prevent duplicate logging of the same chemical part in multiple templates under different names.
* When adding a prepared chemical, the system checks to see if a chemical template already exists in the database for the requested Method/Step Reference to prevent duplicate logging of the same chemical part in multiple templates under different names.

### Lots
* A parent chemical template exists in the database for the PARENT_CHEM_ID provided when logging a lot.
* Requests to create lots of prepared standards or reagents use valid lot IDs of chemicals that both exist as chemical templates and also have at least one lot logged.
* All non-empty date fields are received as strings in the ISO 8601 format with timezone offsets.
* Prepared standards or reagents contain at least one chemical component.
* Requests to update lots are made for valid lot IDs of lots currently existing in the database.

### Lists
* The list name specified in a PUT request exists in the database.
* The list contains at least one list entry.


All validation methods return structured tuples which are later passed to the ValidationErrorCodes class to generate an error message response:
* (field_or_context: str, error_code: int)

## Testing

Full integration tests are implemented using pytest. Tests are located under the /tests/ directory and grouped by schema.

Fixtures include:
* Valid chemicals, lists, and lots
* Chemicals, lists, and lots invalidated in each field in a way that should fail validation

The following items are tested for each schema module:

### Chemical Aggregate Fields (Total_Available_Lots and Total_Open_Lots):
* Chemical aggregate fields are initialized to int(0) upon chemical template creation.
* Chemical aggregate fields will change as a result of lots being open, emptied, or their expiry date passing.
* Chemical aggregate fields are recalculated when a PUT or GET request is submitted for a chemical(s).
* Chemical aggregate fields are recalculated for a chemical template when lots are created or updated.
* Chemical aggregate fields are NOT recalculated when lots are deleted. Though the system currently supports lot deletion, it is marked for an upgrade to remove the ability to delete lots (or anything, for that matter). A very high-level user may need access to truly delete records, but the system should instead have "Removed" field flags for all objects, and "deleting" an object should merely set the "Removed" flag to "True".
    * This would be considered a critical issue if this system were live.
* Chemical aggregate fields are technically updates when a chemical template receives a PUT request, but this is obfuscated by the
fact that chemical aggregate fields are updated when a GET request is received for the template.

### Lists:
* Lists receive standard testing for HTTP codes 200, 201, and 204 in addition to 404 and 400 (missing request body).
* Lists receive HTTP code 422 testing for: Attempt to create a duplicate list, missing required field, missing required value, and incorrect type for field.

### Chemicals:
#### HTTP code 200:
* Chemical objects of all valid configurations are successfully modified in or retrieved from the database.

#### HTTP code 201
* Chemical objects of all valid configurations are successfully inserted in the database.

#### HTTP code 204
* Chemical objects of all valid configurations are successfully deleted from the database.

#### HTTP code 400
* Missing request bodies return error code 400.
* GET requests with malformed primary keys return error code 400

#### HTTP code 404
* Chemicals not found in the database return error code 404.

#### HTTP code 422:
All fields in the chemical request body, the primary key (if applicable), and the nature of the request itself are tested individually to verify that the system properly validates all applicable error codes:

* No required keys are missing from chemical requests.
* No required values are left empty in chemical requests.
* All fields in a chemical request are the correct type.
* No fields in a chemical request with entry constrained by a list contain values not in that list.
* No unexpected keys arrive in a chemical request.
* PUT: The chemical requested for update exists in the database.
* POST: The chemical request does not attempt to create a new chemical with the same combination of manufacturer, manufacturer part number, amount, unit, and container type as an existing chemical to prevent duplicate entries of the same reagent or standard under different names.
* PUT: The chemical request does not contain a malformed primary key.
* Additionally, the system is designed to short-circuit upon the first error found in chemical form validation and return that error message. The tests ensure that requests with two errors return the error message for the first error.
* Confirm that primary keys match in the request body and address.
* PUT: All configurations of valid chemicals are checked for successful update against each configuration of a valid chemical.
* PUT: All invalid chemical configurations are tested for failure to update against all valid chemical configurations.

### Lots:
#### HTTP code 200:
* Verify that lot objects of all valid configurations are successfully modified in or retrieved from the database.

#### HTTP code 201
* Verify that lot objects of all valid configurations are successfully inserted in the database.

#### HTTP code 204
* Lot objects of all valid configurations are successfully deleted from the database.

#### HTTP code 400
* Missing request bodies return error code 400.
* GET requests with malformed primary keys return error code 400.

#### HTTP code 404
* Lots not found in the database return error code 404.
* Lots with parent chemical templates not found in the database return error code 404.

#### HTTP code 422:
All fields in the lot request body, the primary key (if applicable), and the nature of the request itself are tested individually to verify that the system properly validates all applicable error codes:

* No required keys are missing from lot requests.
* No required values are left empty in lot requests.
* Verify that all fields in a lot request are the correct type.
* No fields in a lot request with entry constrained by a list contain values not in that list.
* No unexpected keys arrive in a lot request, nor in the fields of a purchased or prepared component in a lot request.
* Verify that prepared lots contain at least one component.
* Verify that a lot request's parent chemical exists in the database.
* Verify that all date strings are in ISO 8601 format with timezone offsets.
* Verify that optional data fields are not flagged for missing values.
* Verify that lot records used as components on other prepared lots exist in the database.
* Additionally, the system is designed to short-circuit upon the first error found in lot form validation and return that error message. The tests ensure that requests with two errors return the error message for the first error.
* Verify primary keys in request body and address match each other.
* Verify that request body contains a primary key.
* PUT: Verify that the lot requested for update exists in the database.
* PUT: Verify that the lot request does not contain a malformed primary key.

All schema modules are tested to ensure that multiple errors will short-circuit and return the first error.

## Future Upgrades
* The chemical inventory module of CONQUEST LIMS isn't as robust as it could be. Ideally prepared reagent chemical templates would prescribe which purchased chemicals are allowed to be used for each component, they would prescribe the number of components added, and they would also prescribe the amounts added of each chemical component. Prepared *lots* would then query their parent chemical to receive the prescribed component configurations (chemical_ids, amounts, units). Lots would then receive fields to record the actual amount used for each component, and this field could potentially be validated against the prescribed amount.
* Reject requests to replace a chemical template with a chemical that requires the replaced chemical as a preparation component.
    * This cannot be achieved until the system is reconfigured to mirror the change notes above.
    * This is an edge case.
* Create an APIErrorCodes module similar to ValidationErrorCodes to harmonize and centralize the generation of error codes not related to request content.
    * Tests anticipating these error codes can then be made more robust/integrated by calling the reference to the set value in the APIErrorCodes module.
* Add an optional "Comments" field to all chemical, lot, and component records to allow users to include preparation notes.
* Add an optional "Description" field to the chemical schema.
* Water dispensers can currently be logged as purchased chemicals and used to trace the generation of in-house reagent water. However, though the "chemical" can be classed as an instrument, the "Amount" field still requires a numerical input greater than 0. Include the option to "N/A" the amount field.
    * This should trigger a mandatory audit comment.
    * This will be easier to implement once the upgrade to flatten incoming requests for validation is implemented.
* Rather than deleting fields, add a "Removed" flag and change DELETE CRUD operations to merely alter the "Removed" flag.
* Add an audit trail module.
* In addition to changing DELETE operations to simply toggle a "Removed" flag, consider locking the "Name" field of records for edits after initial creation. This would make it so that it would be effectively useless to fully swap out one chemical record with another (thereby making this a soft fix to the problem described above where a prepared chemical template could overwrite its own dependency).
* Prevent "Open Dates" from being future dates/times.
* Prevent "Empty Dates" from being earlier than open or prepared dates.
* Prevent logging the same lot onto a prepared lot twice.
    * This would be nullified with the architectural change to have chemical templates prescribe components and amounts.
* Maintain current request structure but flatten requests for validation. It would be easier to separate the concerns of validation out by type of validation check. I would likely create a list of fields-by-required-validation check and use each list to check flattened_request[validated_field_list_element] values in the order that validation checks must be run (missing field, missing value, wrong type, and invalid list entry, followed by checks like datetime format, primary key validity, and existence in the database). This would make it easier both to skip optional values in the miss_req_value check and to include the "N/A" string as a valid entry for fields not typed as strings. Records would be reconstructed according to the schema definition prior to record insertion.