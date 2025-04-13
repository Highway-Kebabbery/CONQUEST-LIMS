# <div align="center">CONQUEST-LIMS</div>
## Description
CONQUEST-LIMS is a lightweight, Flask- and MongoDB-based Laboratory Information Management System (LIMS) built to manage chemical inventories in highly regulated lab environments. It has a robust validation system and supports CRUD operations for chemical templates, lot records, and lists used to control validated-entry fields..

## Features
### Current
* Chemical templates: Defines a chemical with a unique combination of manufacturer, manufacturer part number, amount, units, and container type which distinguishes it from other chemicals in order to standardize the entry of standards and reagents in the system and avoid the creation of duplicate entries.
* Lot management: Record and manage bottles or containers tied to a specific chemical template. Record which chemical lots were used in the preparation of prepared chemical lots.
* Supports separate, tailored data for in-house prepared standards or reagents and externally purchased standards or reagents.
* Supports validated field entry using lists of approved values to harmonize system-wide data entry in key fields.
* Robust, schema-level validation guarantees adherance to database schema.
* Offers an API with CRUD endpoints following RESTful design principles for all record types.
* Includes a robust, full integration testing suite that validates all data flows across all schema using `pytest` and `mongomock`.
* Containerized using Docker to ensure consistent deployment across all platforms.

### Planned:
* The app is currently undergoing orchestration using Minikube.
* Following this, ElasticSearch will be implemented for fuzzy searches of chemical and lot names.
* For a detailed list of additional planned upgrades, please refer to [docs/specification.md](./docs/specification.md)

## How to Use
(DRAFT, THIS IS A DRAFT)
* Install and configure Windows Subsystem for Linux (WSL) (DRAFT, THIS WILL BE FLESHED OUT)
* Download the project and navigate to the root directory of the project.
* Run the command `chmod +x setup.sh`.
* Run the command `./setup.sh` to initialize the database and load example data.
* Run the command `scripts/clean.md` when finished to clean up containers and database volumes.
* Send GET requests to each end point using:
    * `curl http://localhost:5000/`
    * `curl http://localhost:5000/chemicals`
    * `curl http://localhost:5000/lots`
    * `curl http://localhost:5000/lists`
* Log an example chemical template (for fun!):
    * Copy/paste this command into your terminal and execute it.
    ```bash
    curl -s -X POST "http://localhost:5000/chemicals" \
        -H "Content-Type: application/json" \
        -d '{
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
    ```
    * It didn't work, did it? Did you check to make sure there wasn't already a chemical in the system for the template you were trying to log?
* Try logging another chemical!:
    * Copy/paste this command into your terminal and execute it.
    ```bash
    curl -s -X POST "http://localhost:5000/chemicals" \
        -H "Content-Type: application/json" \
        -d '{
            "Name": "Trifluoromethanesulfonic acid, 99%, extra pure",
            "CAS_Number": "1493-13-6",
            "Classification": "Strong Acid",
            "Storage_Condition": "Ambient",
            "Source": "Purchased",
            "Purchased_Fields": {
                "Manufacturer": "Fisher Scientific",
                "Manufacturer_Part_Number": " AC169890011",
                "Amount": 1,
                "Units": "L",
                "Container_Type": "Bottle"
            }
        }'
    ```
    * Ah, that didn't work, either, did it? Did you run `curl http://localhost:5000/lists` to see which fields are validated entry fields, or did you believe that you could trust me?
* Log a fun chemical (for real this time!):
    * Copy/paste this command into your terminal and execute it.
    ```bash
    curl -s -X POST "http://localhost:5000/chemicals" \
        -H "Content-Type: application/json" \
        -d '{
            "Name": "Trifluoromethanesulfonic acid, 99%, extra pure",
            "CAS_Number": "1493-13-6",
            "Classification": "Strong acid",
            "Storage_Condition": "Ambient",
            "Source": "Purchased",
            "Purchased_Fields": {
                "Manufacturer": "Fisher Scientific",
                "Manufacturer_Part_Number": " AC169890011",
                "Amount": 1,
                "Units": "L",
                "Container_Type": "Bottle"
            }
        }'
    ```
* Oops, it looks like trifluoromethanesulfonic acid isn't quite as fun as it sounds. We need to update its description in the database.
    * (DRAFTING DOCUMENT. THIS IS A GOOD PLACE TO ENCOURAGE USE OF THE ELASTIC SEARCH FUNCTIONALITY TO FIND THIS CHEMICAL BY NAME TO GET THE PRIMARY KEY FOR A PUT REQUEST. FOR NOW THEY CAN JUST SEND A GET REQUEST OR LOOK AT THE RETURNED "inserted_id" FIELD FROM TEN SECONDS AGO.)
    * Please paste this completely valid command into your terminal, update it with trifluoromethanesulfonic acid's "_id," and then execute your request.
    ```bash
    curl -s -X PUT "http://localhost:5000/chemicals/<chemical_id>" \
        -H "Content-Type: application/json" \
        -d '{
            "_id": <chemical_id>,
            "Name": "Trifluoromethanesulfonic acid, 99%, extra pure",
            "CAS_Number": "1493-13-6",
            "Classification": "Super acid",
            "Storage_Condition": "Ambient",
            "Source": "Purchased",
            "Purchased_Fields": {
                "Manufacturer": "Fisher Scientific",
                "Manufacturer_Part_Number": " AC169890011",
                "Amount": 1,
                "Units": "L",
                "Container_Type": "Bottle"
            }
        }'
    ```
* Try running the integration testing suite using `docker exec -it conquest-lims-api pytest`.

### Software Requirements
(Fill this out once app is containerized. Probably won't change after implementing ElasticSearch.)

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
│   ├── app-deployment.yaml
│   ├── app-service.yaml
│   ├── mongo-deployment.yaml
│   └── mongo-service.yaml
│
├── scripts/                      # Kubernetes deployment files
│   ├── clean.sh                  # Tears down containers and volumes
│   ├── load_data.sh              # Called in setup.sh
│   └── smoke_test.sh             # Called in setup.sh
│
├── tests/                        # Full integration test suite for each module and edge cases
│
├── Dockerfile                    # Defines the app container image
├── docker-compose.yml
├── requirements.txt
│
├── run.py                        # Entry point for the app from Dockerfile
│
├── README.md
│
└── setup.sh                      # Entry point for the system from the terminal
```

### (Setting up environment (WSL, etc.))

### (Starting the actual app. Should just be a shell script)

### Operation
#### API Base URL
```python
http://localhost:5000/
```

#### API Overview

| Entity    | Endpoint                   | Description       |
|-----------|----------------------------|-------------------|
| Chemicals | `/chemicals`               | GET, POST         |
|           | `/chemicals/<chemical_id>` | GET, PUT, DELETE  |
| Lots      | `/lots`                    | GET, POST         |
|           | `/lots/<lot_id`            | GET, PUT, DELETE  |
| Lists     | `/lists`                   | GET, POST         |
|           | `/lists/<list_name>`       | GET, PUT, DELETE  |

Detailed request/response schemas are documented in the [API reference.](./docs/api_reference.md)

(Include a bit about how to use curl to interact with the API via the command line and a reference to find example chemical objects in testing or set-up.)

### Validation Rules
* All required fields must be present and non-empty.
* Data types are strictly enforced per schema.
* List-based fields must reference existing list values (e.g., approved manufacturers).
* Dates must arrive as timezone-aware ISO 8601 formatted strings.
* Prepared lots must include at least one valid component.
* Lists must contain at least one entry.
* For a detailed look at the validation strategy, click [here](./docs/specification.md/#validation-strategy)

### Testing
Run all tests with
```bash
pytest
```
(Include a portion in set-up about getting pytest to run in the root directory.)


## Technology


## What I Learned
(.....how to build the back end of a web app. Because I've never done anything remotely similar.)

## Motivation
(The company I want to work for uses this tech stack. I can also use this tech stack to build my own custom web apps now, and I have plans for how to use this power to grow my band with tools that other peple don't have available. Tools that I build.)

## Contributions
This project is currently maintained internally and not open to contributions.

## License
(Come back after completion to fill this section out. This project is not available for use by anybody, anywhere, any time) (...I think not adding a license is what I do to achieve this.)