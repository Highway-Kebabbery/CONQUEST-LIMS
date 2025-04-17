# CONQUEST-LIMS Specifications
## Overview
CONQUEST-LIMS is a laboratory information management system (LIMS) designed to track chemical inventory in highly-regulated laboratory settings. It supports creation, retrieval, update, and deletion of:
* Chemical templates
* Lot records (related to specific chemicals)
* Lists for constraining validated field entries (approved manufacturers, classification, unit, *etc.*)

### Functionality Overview
Chemical templates store information for a given, unique combination of manufacturer, manufacturer part number, amount, unit, and container type. In order to avoid system bloat and to prevent entry error, no two chemicals with the same combination of the aforementioned attributes can exist. "Chemicals" serve as a template against which individual bottles of standards or reagents, otherwise known as **lots**, may be logged. Information common to all lots of a given chemical is stored on the chemical document. Lot documents are linked to their parent chemical template record via the `lots.chemical_id` field, where `lots.chemical_id` corresponds to the primary key of a chemicals document: `chemicals._id`. Upon lot creation, all chemical data will be duplicated onto the lot record using the parent chemical form as a template; lot requests only require from the front-end the information unique to the given lot being logged. This alleviates the burden of logging information common to multiple lots for every instance of a lot logged into the lab and also helps to avoid entry errors.

With respect to lots: two different physical bottles of a purchased chemical may arrive with the exact same values for every field in both the lot and chemical document schema as is often the case in a lab when multiple bottles of the same manufacturer batch number are received. Lots are thus distinguished by their internal lot number which currently corresponds to the "_id" field primary key assigned by MongoDB upon record creation. There is a future upgrade pending to develop a generator for unique and human-readable internal lot numbers (*e.g.* 20250416-L0001). The difficulty would be ensuring that, if multiple lots are logged concurrently by separate users, each logged lot still receives a unique internal lot number.

The creation and modification of chemical templates is a highly validated process that constrains user entry in every way imaginable to prevent entry errors, to ensure consistency of records, and to ensure the system will function in a regulated environment. Chemical templates must first be logged before a lot can be logged using that template. Chemical/lot related objects are split into purchased chemicals/lots and prepared chemicals/lots. Standards or reagents purchased from a manufacturer are logged as "purchased" lots; they may then be used in testing, or otherwise as components to create "prepared" lots. Standards or reagents prepared in-house are logged as "prepared" lots; they accept one or more components to document their preparation. Each component used must come from an existing lot logged into the system. Components are linked to their lot record on the field `lots.Components.lot_id`, which corresponds to `lots._id`, where `lot_id` is the primary key of a lot already logged into the system. Each component of a prepared lot additionally documents the amount and units used in preparation of the prepared standard or reagent lot.

Chemical and lot creation is harmonized across users and the system by the use of validated entry fields with allowed inputs governed by lists that can be modified as needed. Examples include approved manufacturers, units, storage conditions, container types, *etc.* The name of each list is governed by the name of a linked field in the chemicals document schema, as are also many fields on lot documents governed by linked fields on the chemicals template.

Chemical documents also store information on the total number of lots available and the number of open lots logged under that chemical's primary key (`lots.chemical_id`). These values refresh any time a lot is added or updated and any time a chemical template is updated or retrieved.

CONQUEST LIMS supports fuzzy searches of chemicals and lots by name as well as limited analytics for chemical inventory: The three most popular manufacturers, the number of lots awaiting disposal, and the total number of available lots logged into the system. All Elasticsearch documents mirror changes to the database; there is no direct interaction.

## Design Philosophy
Chemical data are duplicated onto lot records in an attempt to work with the document-based database idea that information commonly accessed together should be stored together. Analysts in the lab will commonly need to access a list of all available lots, or at least all lots for a given chemical. At the expense of marginally larger documents, all required information for a given lot (chemical information plus unique lot information) can be pulled in one query. At the same time, lot creation requests, which are by far a more common occurrence than chemical creation requests, are vastly simplified as the front end is able to safely ignore the need to send anything but information related directly to the unique bottle in the analyst's hands, thus reducing the chance for errors to occur. Finally, the collections remain split because there are many instances in which an analyst may need to view all chemical templates logged in the system. Lot data would be useless in such a case.

The segregation of chemicals and lots into purchased and prepared sub-categories further takes advantage of the flexibility of MongoDB's document-based design as each sub-category of chemical/lot stores slightly different information with each group containing at least one unique field with respect to the other.

All records are stored in MongoDB and served via a Flask-based API. Data validation is enforced at the schema level through dedicated classes to ensure data harmonization and integrity prior to record insertion or update.

The implementation of Elasticsearch allows users to search for chemicals or lots by name which makes it easier to locate records in the system without the need to commit exact chemical or lot names to memory.

CONQUEST LIMS is containerized using Docker and orchestrated using Kubernetes (locally via Minikube) to allow the system to be deployed, scaled, and managed with full separation between the application and database containers.

## Important Usage Information
* Initial configuration:
    * All lists for validated entry fields must be created before any object with a validated entry field (currently: `chemicals` and `lots`) can be created.
    * Purchased chemicals/lots should be created first followed by prepared chemicals/lots that use only purchased lots as components.
* `lots.chemical_id` links to `chemicals._id`.
* `lots.Components.lot_id` links to `lots._id`.
* Optional fields are required to be sent with either `null` or an empty value of the type specified in the schema. The key cannot be missing.
* Datetimes must be sent to the system in local time with timezone offsets (UTC timezones must be received in the form `+00:00`; **"Z" will not work for UTC**).
* Datetimes are returned in the UTC timezone.
* Do not attempt a `PUT` request to update a chemical template with the template of another (prepared) chemical whose lots would require the first chemical, the replaced one, as a preparation component. This cannot be enforced until and unless the system is changed to operate in a more rigorous fashion where chemical templates also prescribe prepared lot components and amounts (see ["Future Upgrades"](#future-upgrades)).

## Architecture
### Backend Stack
* Language: Python 3.10+
* Framework: Flask
* Database: MongoDB (accessed via pymongo)
* Testing: pytest, mongomock
* Search: Elasticsearch
* Containerization: Docker
* Orchestration: Kubernetes (simulated locally using Minikube)

## Project Structure
```bash
CONQUEST-LIMS/
│
├── app/
│   ├── __init__.py               # Initializes Flask app and MongoDB client
│   ├──constants.py               # Constants shared by all modules
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
│   ├── app-deployment.yaml
│   ├── app-service.yaml
│   ├── elasticsearch-deployment.yaml
│   ├── elasticsearch-service.yaml
│   ├── mongo-deployment.yaml
│   └── mongo-service.yaml
│
├── scripts/                      # Kubernetes deployment files
│   ├── clean.sh                  # Tears down containers, pods, and volumes
│   ├── load_data.sh              # Called in setup.sh. Initializes database with data
│   └── smoke_test.sh             # Called in setup.sh
│
├── tests/                        # Full integration test suite for api and database
│
├── docker-compose.yml            # Development only; defines containers for services
├── Dockerfile                    # Defines the app container image
├── requirements.txt
│
├── run.py                        # Entry point for the app from Dockerfile
│
├── README.md
│
└── setup.sh                      # Start here. Entry point for system from terminal
```

## API Endpoints

All endpoints return proper HTTP status codes, follow RESTful practices, and expect JSON payloads where appropriate.

### Lists

| Method | Endpoint                 | Description                  |
|--------|--------------------------|------------------------------|
| GET    | /lists/                  | Get all lists records        |
| POST   | /lists/                  | Add a new lists template     |
| GET    | /lists/<list_name>       | Fetch a specific lists by ID |
| PUT    | /lists/<list_name>       | Update a lists template      |
| DELETE | /lists/<list_name>       | Delete a lists template      |

### Chemicals

| Method | Endpoint                          | Description                     |
|--------|-----------------------------------|---------------------------------|
| GET    | /chemicals/                       | Get all chemical records        |
| POST   | /chemicals/                       | Add a new chemical template     |
| GET    | /chemicals/<chemical_id>          | Fetch a specific chemical by ID |
| PUT    | /chemicals/<chemical_id>          | Update a chemical template      |
| DELETE | /chemicals/<chemical_id>          | Delete a chemical template      |
| GET    | /chemicals/search?query=key+words | Search chemicals by name        |

### Lots

| Method | Endpoint                     | Description                                           |
|--------|------------------------------|-------------------------------------------------------|
| GET    | /lots/                       | Get all lots records                                  |
| POST   | /lots/                       | Add a new lots template                               |
| GET    | /lots/<lot_id>               | Fetch a specific lots by ID                           |
| PUT    | /lots/<lot_id>               | Update a lots template                                |
| DELETE | /lots/<lot_id>               | Delete a lots template                                |
| GET    | /lots/search?query=key+words | Search lots by name                                   |
| GET    | /lots/analytics              | Return basic analytics from MongoDB and Elasticsearch |

## Data Schema
### MongoDB
The following represent the database schema for each object type:

* Purchased chemicals:
```json
record = {
    "_id": ObjectId,
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

# _id: Required. Primary key.
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

# Total_Available_Lots: Initialized on POST /chemicals. Recalculated on POST/PUT /lots or GET/PUT /chemicals.
# Total_Open_Lots: Initialized on POST /chemicals. Recalculated on POST/PUT /lots or GET/PUT /chemicals.
```
* Prepared chemicals:
```json
record = {
    "_id": ObjectId,
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

# _id: Required. Primary key.
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
* Purchased lots:
```json
record = {
    "_id": ObjectId,
    "chemical_id": ObjectId,
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
    "Open_Date": datetime,
    "Expiry_Date": datetime,
    "Empty_Date": datetime
}

# _id: Required. Primary key.
# chemical_id: Required. Links to chemicals._id of existing chemical.
# Name: Required. From parent chemical.
# CAS_Number: Required. From parent chemical.
# Classification: Required. From parent chemical.
# Storage_Condition: Required. From parent chemical.
# Source: Required. From parent chemical.

# Purchased_Fields: Required. From parent chemical.
# Manufacturer: Required. From parent chemical.
# Manufacturer_Part_Number: Required. From parent chemical.
# Manufacturer_Lot_Batch_Number: Required.
# Amount: Required. From parent chemical. Either type.
# Units: Required. From parent chemical.
# Container_Type: Required. From parent chemical.

# Open_Date: Optional. Timezone-aware ISO 8601 string (UTC offset of the form +00:00).
# Expiry_Date: Required. Timezone-aware ISO 8601 string (UTC offset of the form +00:00).
# Empty_Date: Optional. Timezone-aware ISO 8601 string (UTC offset of the form +00:00).
```
* Prepared lots
```json
record = {
    "_id": ObjectId,
    "chemical_id": ObjectId,
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
    }
    "Preparation_Date": datetime,
    "Expiry_Date": datetime,
    "Empty_Date": datetime,
    "Components": [
        # Purchased chemical/lot component
        {
            "lot_id": ObjectId,
            "Name": str,
            "Manufacturer": str,
            "Manufacturer_Part_Number": str,
            "Manufacturer_Lot_Batch_Number": str,
            "Amount": [int, float],
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

# _id: Required. Primary key.
# chemical_id: Required. Links to chemicals._id of existing chemical.
# Name: Required. From parent chemical.
# CAS_Number: Required. From parent chemical.
# Amount: Required. From parent chemical. Either type.
# Units: Required. From parent chemical.
# Container_Type: Required. From parent chemical.
# Classification: Required. From parent chemical.
# Storage_Condition: Required. From parent chemical.
# Source: Required. From parent chemical.

# Prepared_Fields: Required. From parent chemical.
# Method_Step_Reference: Required. From parent chemical.

# Preparation_Date: Optional. Timezone-aware ISO 8601 string (UTC offset of the form +00:00).
# Expiry_Date: Required. Timezone-aware ISO 8601 string (UTC offset of the form +00:00).
# Empty_Date: Optional. Timezone-aware ISO 8601 string (UTC offset of the form +00:00).

# Components: # Required. Must be >= 1 components.

# Purchased chemical/lot component:
# lot_id: Required. Primary key of an existing lot.
# Name: Required. From parent chemical.
# Manufacturer: Required. From parent chemical.
# Manufacturer_Part_Number: Required. From parent chemical.
# Manufacturer_Lot_Batch_Number: Required.
# Amount: Required. From parent chemical. Either type.
# Units: Required. From parent chemical.
# Expiry_Date: Required. Timezone-aware ISO 8601 string (UTC offset of the form +00:00).

# Prepared chemical/lot component:
# lot_id: Required. Primary key of an existing lot.
# Name: Required. From parent chemical.
# Method_Step_Reference: Required. From parent chemical.
# Amount: Required. From parent chemical. Either type.
# Units: Required. From parent chemical.
# Expiry_Date: Required. Timezone-aware ISO 8601 string (UTC offset of the form +00:00).
```
* Lists
```json
record = {
    "_id": ObjectId,
    "Name": str,
    "List_entries": [
        str
    ]
}

# _id: Not managed. MongoDB default primary key.
# Name: Required. Must be unique. Primary key.
# List_Entries: Required. Lists must have at least one entry.
# (List entries): At least one entry required.
```

### Elasticsearch
The following represent the Elasticsearch document models. Elasticsearch documents are mirrored from fields and values in MongoDB documents at the time of insertion or modification.

* Chemicals
```json
document = {
    "Mongo_Collection": str,
    "Name": str,
    "Mongo_id": str,
    "id": str,
    "score": float
}

# Mongo_Collection: The name of the MongoDB collection the document originates from.
# Name: The name of the chemical template the lot is logged under.
# Mongo_id: The primary key of the corresponding database record.
# _id: Elasticsearch auto-generated primary key
# score: The result's relevance score
```
* Purchased lots
```json
document = {
    "Mongo_Collection": str,
    "Name": str,
    "Mongo_id": str,
    "Expiry_Date": str,
    "Empty_Date": str,
    "Open_Date": str,
    "id": str,
    "score": float
}

# Mongo_Collection: The name of the MongoDB collection the document originates from.
# Name: The name of the chemical template the lot is logged under.
# Mongo_id: The primary key of the corresponding database record.
# Expiry_Date: See database schema for more information.
# Empty_Date: See database schema for more information.
# Open_Date: See database schema for more information.
# _id: Elasticsearch auto-generated primary key
# score: The result's relevance score
```
* Prepared lots
```json
document = {
    "Mongo_Collection": str,
    "Name": str,
    "Mongo_id": str,
    "Expiry_Date": str,
    "Empty_Date": str,
    "Preparation_Date": str,
    "id": str,
    "score": float
}

# Mongo_Collection: The name of the MongoDB collection the document originates from.
# Name: The name of the chemical template the lot is logged under.
# Mongo_id: The primary key of the corresponding database record.
# Expiry_Date: See database schema for more information.
# Empty_Date: See database schema for more information.
# Preparation_Date: See database schema for more information.
# _id: Elasticsearch auto-generated primary key
# score: The result's relevance score
```

## Data Validation Strategy

Each database schema (Chemical, Lot, List) has a corresponding class module (ChemicalSchema, LotSchema, ListsSchema) which, as necessary and in some cases in addition to the end points, verifies that:

### All Schema:
* All required fields are present.
* All required values are present.
* No extra fields are present.
* All fields have the correct type.
* Validated entry field values exist in their corresponding validated entry list.
* Primary keys are not malformed:
    * Chemicals and lots: The system checks to ensure any `_id` key is a valid object of the type `ObjectId()`.
    * Lists: List documents do not use MongoDB's `_id` as their primary key; list requests are validated to ensure the `Name` field is unique.
* Primary keys match in the incoming request body and request address.

### Chemicals:
* Requests to update existing chemical templates contain the `_id` of a valid chemical template in the database (expired chemicals are still allowed to be added as components).
* When adding a purchased chemical, the system checks to see if the requested combination of manufacturer, manufacturer part number, amount, unit, and container type already exists in the database to prevent duplication of the same chemical part in multiple templates under different names.
* When adding a prepared chemical, the system checks to see if a chemical template already exists in the database for the requested Method/Step Reference to prevent duplication of the same chemical part in multiple templates under different names.

### Lots
* A parent chemical template exists in the database for the `chemical_id` provided when logging a lot.
* Requests to create lots of prepared standards or reagents use valid lot `_id`s of chemicals that both exist as chemical templates and also have at least one lot logged.
* All non-empty date fields are received as strings in the ISO 8601 format with timezone offsets (UTC **must** be formatted as `+00:00`; `Z` will not work).
* Prepared standards or reagents contain at least one chemical component.
* Requests to update lots are made for valid lot IDs of lots currently existing in the database.

### Lists
* The list name specified in a `PUT` request exists in the database.
* The list contains at least one list entry.


All validation methods return tuples which are later passed to the ValidationErrorCodes class to generate an error message response:
* (field_or_context: str, error_code: int)

## Testing

### Integration testing (Flask-MongoDB; excludes Elasticsearch)
Full integration tests are implemented using `pytest`. Tests are located under the `tests/` directory and are grouped by schema.

Fixtures include:
* Valid chemicals, lists, and lots
* Chemicals, lists, and lots invalidated in each field in a way that should fail validation

The following items are tested for each schema module:

#### Chemical Aggregate Fields (Total_Available_Lots and Total_Open_Lots):
* Chemical aggregate fields are initialized to `0` upon chemical template creation.
* Chemical aggregate fields will refresh as a result of lots being open, emptied, or their expiry date passing (updates related to expiry are realized upon any `GET` request).
* Chemical aggregate fields are refreshed when a `PUT` or `GET` request is submitted for a chemical(s).
* Chemical aggregate fields are refreshed for a chemical template when when a `POST` or `PUT` request is submitted for a lot.
* Chemical aggregate fields are NOT refreshed when lots are deleted. Though the system currently supports lot deletion, it is marked for an upgrade to remove the ability to delete lots (or anything, for that matter). A very high-level user may need access to truly delete records, but the system should instead have `Removed` flag fields for all objects. "Deleting" an object should merely set `<collection>.Removed = True`.
    * This would be considered a critical issue if this system were live.
* Chemical aggregate fields are technically refreshed when a chemical template receives a `PUT` request, but this is obfuscated by the
fact that chemical aggregate fields are refreshed when a `GET` request is received for the template.

#### Lists:
* Lists receive standard testing for HTTP codes 200, 201, and 204 in addition to 404 and 400 (missing request body).
* Lists receive HTTP code 422 testing for: Attempt to create a duplicate list, missing required field, missing required value, and incorrect type for field.

#### Chemicals:
##### HTTP code 200:
* Chemical objects of all valid configurations are successfully modified in or retrieved from the database.

##### HTTP code 201
* Chemical objects of all valid configurations are successfully inserted in the database.

##### HTTP code 204
* Chemical objects of all valid configurations are successfully deleted from the database.

##### HTTP code 400
* Missing request bodies return error code 400.
* `GET` requests with malformed primary keys return error code 400

##### HTTP code 404
* Chemicals not found in the database return error code 404.

##### HTTP code 422:
All fields in the chemical request body, the primary key (if applicable), and the nature of the request itself are tested individually to verify that the system properly validates all applicable error codes:

* No required keys are missing from chemical requests.
* No required values are left empty in chemical requests.
* All fields in a chemical request are the correct type.
* No fields in a chemical request with entry constrained by a list contain values not in that list.
* No unexpected keys arrive in a chemical request.
* `PUT`: The chemical requested for update exists in the database.
* `POST`: The chemical request does not attempt to create a new chemical with the same combination of manufacturer, manufacturer part number, amount, unit, and container type as an existing chemical to prevent duplicate entries of the same reagent or standard under different names.
* `PUT`: The chemical request does not contain a malformed primary key.
* Additionally, the system is designed to short-circuit upon the first error found in chemical form validation and return that error message. The tests ensure that requests with two errors return the error message for the first error encountered.
* Confirm that primary keys match in the request body and address.
* `PUT`: All configurations of valid chemicals are checked for successful update against each configuration of a valid chemical.
* `PUT`: All invalid chemical configurations are tested for failure to update against all valid chemical configurations.

#### Lots:
##### HTTP code 200:
* Verify that lot objects of all valid configurations are successfully modified in or retrieved from the database.

##### HTTP code 201
* Verify that lot objects of all valid configurations are successfully inserted in the database.

##### HTTP code 204
* Lot objects of all valid configurations are successfully deleted from the database.

##### HTTP code 400
* Missing request bodies return error code 400.
* `GET` requests with malformed primary keys return error code 400.

##### HTTP code 404
* Lots not found in the database return error code 404.
* Lots with parent chemical templates not found in the database return error code 404.

##### HTTP code 422:
All fields in the lot request body, the primary key (if applicable), and the nature of the request itself are tested individually to verify that the system properly validates all applicable error codes:

* No required keys are missing from lot requests.
* No required values are left empty in lot requests.
* Verify that all fields in a lot request are the correct type.
* No fields in a lot request with entry constrained by a list contain values not in that list.
* No unexpected keys arrive in a lot request, nor in the fields of a purchased or prepared component in a lot request.
* Verify that prepared lots contain at least one component.
* Verify that a lot request's parent chemical exists in the database.
* Verify that all date strings are in ISO 8601 format with timezone offsets (UTC must be formatted as `+00:00`; `Z` will not work).
* Verify that optional data fields are not flagged for missing values.
* Verify that lot records used as components on other prepared lots exist in the database.
* Additionally, the system is designed to short-circuit upon the first error found in lot form validation and return that error message. The tests ensure that requests with two errors return the error message for the first error.
* Verify primary keys in request body and address match each other.
* Verify that request body contains a primary key.
* `PUT`: Verify that the lot requested for update exists in the database.
* `PUT`: Verify that the lot request does not contain a malformed primary key.


## End-to-End Testing
The system runs smoke tests through the terminal on start-up inside `setup.sh`, which calls `smoke_test.sh`, to ensure all end points are available and that a successful connection to the database has been established. Elasticsearch is not currently tested in the smoke tests.

## Future Upgrades
* The chemical inventory module of CONQUEST LIMS isn't as robust as it could be. Ideally, prepared reagent chemical templates would prescribe which purchased chemicals are allowed to be used for each component, they would prescribe the number of components added, and they would also prescribe the amounts added of each chemical component. Prepared *lots* would then query their parent chemical to receive the prescribed component configurations (chemical_ids, amounts, units). Lots would then receive fields to record the actual amount used for each component, and this field could potentially be validated against the prescribed amount.
* Maintain current request structure but flatten requests for validation. It would be easier to separate the concerns of validation out by type of validation check. I would likely create for each type of validation check a list of fields for the current schema that receive that validation check check. I could then use each list to check the keys in the flattened request that exist in the list. Checks would be run in the order that validation checks must be run (missing field, missing value, wrong type, and invalid list entry, followed by checks like datetime format, primary key validity, and existence in the database). This would make it easier both to skip optional values in the `HelperFunctions.miss_req_value()` check and also to include the "N/A" string as a valid entry for fields not typed as strings (such as `Amount`). Records would be reconstructed according to the schema definition prior to record insertion.
* Develop a generator for unique and human-readable internal lot numbers (*e.g.* 20250416-L0001).
    * The difficulty would be ensuring that, if multiple lots are logged concurrently by separate users, each logged lot still receives a unique internal lot number.
* Move Elasticsearch document construction out of end point logic and into class methods.
* Reject requests to replace a chemical template with a chemical that requires the replaced chemical as a preparation component.
    * This cannot be achieved until the system is reconfigured to mirror the change notes above.
    * This is an extreme edge case.
* Introduce character limits for each field.
* Create an APIErrorCodes module similar to ValidationErrorCodes to harmonize and centralize the generation of error codes not related to request content.
    * Tests anticipating these error codes can then be made more robust/integrated by calling the reference to the set value in the APIErrorCodes module.
* Add an optional "Comments" field to all chemical, lot, and component records to allow users to include preparation notes.
* Add an optional "Description" field to the chemical schema.
* Water dispensers can currently be logged as purchased chemicals and used to trace the generation of in-house reagent water. However, though the "chemical" can be classed as an instrument, the "Amount" field still requires a numerical input greater than `0`. Include the option to "N/A" the amount field.
    * This should trigger a mandatory audit comment.
    * This will be easier to implement once the upgrade to flatten incoming requests for validation is implemented.
* Rather than deleting fields, add a `<collection>.Removed` flag and change `DELETE` CRUD operations to merely set `<collection>.Removed = True`.
* Add an audit trail module.
    * This is a monumental task. We here at CONQUEST LIMS (it's me; I'm "we here at CONQUEST LIMS") are simply acknowledging the need for an audit trail.
* In addition to changing `DELETE` operations to simply toggle a `<collection>.Removed` flag, consider locking the `Name` field of records for edits after initial creation. This would make it so that it would be effectively useless to fully swap out one chemical record with another (thereby making this a soft fix to the problem described above where a prepared chemical template could overwrite its own dependency).
* Prevent `Open_Date` from being future dates/times.
* Prevent `Empty_Date` from being earlier than open or prepared dates.
* Only allow the use of opened lots as components prepared lots.
* Prevent logging the same lot onto a prepared lot twice.
    * This would be nullified with the architectural change to have chemical templates prescribe components and amounts.
* Add Elasticsearch tests to `smoke_tests.sh`.
* Add Elasticsearch tests to the functional tests modules in `tests/`.
* Finish refactoring constants into the `constants.py` module.
    * This will be limited to global constants such as default field names and values for MongoDB or Elasticsearch documents. Constants related to database schema modules should remain in the appropriate schema model module.
* Add the ability to `GET` a specific list of lots; not one lot, not all lots, but a custom list of lots.