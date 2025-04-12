# CONQUEST-LIMS Specifications
## Overview
CONQUEST-LIMS is a lightweight laboratory information management system (LIMS) designed to track chemical inventory in highly-regulated laboratory settings. It supports record creation, retrieval, update, and deletion of:
* Chemical templates
* Lot records (tied to chemicals)
* Lists for constraining validated field entries (Approved manufacturers, classification, unit, etc.)

All records are stored in MongoDB and served via a Flask-based API. Validation is enforced at the schema level through dedicated classes to ensure data harmonization and integrity.

## Architecture
### Backend Stack
* Language: Python 3.10+
* Framework: Flask
* Database: MongoDB (accessed via pymongo)
* Testing: pytest, mongomock
* Containerization (optional): Docker

### Project Structure
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
* equests to update existing chemical templates contain the ID of a valid chemical template
in the database (expired chemicals are still allowed to be added as components).
* When adding a purchased chemical, the system checks to see if the requested combination of manufacturer, manufacturer part number, amount, unit, and container type already exists in the database to prevent duplicate logging of the same chemical part in multiple templates under different names.
* When adding a prepared chemical, the system checks to see if a chemical template already exists in the database for the requested Method/Step Referenceto prevent duplicate logging of the same chemical part in multiple templates under different names.

### Lots
* A parent chemical template exists in the database for the PARENT_CHEM_ID provided when logging a lot.
* Requests to create lots of prepared reagents use valid lot IDs of chemicals that both exist as chemical templates and also have at least one lot logged.
* All non-empty date fields are received as strings in the ISO 8601 format with timezone offsets.
* Prepared reagents contain at least one chemical component.
* Requests to update lots are made for valid lot IDs of lots currently existing in the database.

### Lists
* The list name specified in a PUT request exists in the database.


All validation methods return structured tuples which are later passed to the ValidationErrorCodes class to generate an error message response:
* (field_or_context: str, error_code: int)