# <div align="center">CONQUEST-LIMS</div>
## Description
CONQUEST-LIMS is a Flask- and MongoDB-based Laboratory Information Management System (LIMS) built to manage chemical inventories in highly regulated lab environments. It has a robust data-entry validation system and supports CRUD operations for chemical templates, lot records, and lists used to control validated-entry fields. It supports fuzzy searches for chemical and lot names via Elasticsearch and supports analytics aggregated from MongoDB and Elasticsearch. CONQUEST LIMS is containerized using Docker and orchestrated using Kubernetes. Minikube is used as a local Kubernetes cluster to simulate real-world orchestration allowing services to be deployed, scaled, and managed with full separation between the application, database, and Elasticsearch containers.

For hiring managers who might only skim the README: I recommend at least reading the [Motivation](#motivation) section in addition to information required to verify that the system functions as described. I also recommend reading the [design philosophy](docs/specification.md#design-philosophy) and [future upgrades](docs/specification.md#future-upgrades) outlined in the specifications document to develop a better understanding of my capabilities beyond the immediate technical competency demonstrated by the code itself.

## Features
### Current
For full system behaviour, record schema, design philosophy, and validation detail, see [docs/specifications.md](docs/specification.md)

* Chemical templates: Defines a chemical with a unique combination of manufacturer, manufacturer part number, amount, units, and container type which distinguishes it from other chemicals in order to standardize the entry of standards and reagents in the system and avoid the creation of duplicate records.
* Lot management: Record and manage bottles or containers related to a specific chemical template. Record which chemical lots were used as components in the preparation of prepared chemical lots.
* Supports separate, tailored data for in-house prepared standards or reagents and for externally purchased standards or reagents.
* Supports validated field entry using lists of approved values to harmonize system-wide data entry in key fields.
* Robust, schema-level validation guarantees adherence to database schema.
* Offers an API with CRUD endpoints following RESTful design principles for all record types.
* Supports fuzzy searches of chemical and lot names using Elasticsearch.
* Supports inventory analytics aggregated from MongoDB and Elasticsearch.
* Includes a robust, full integration testing suite that validates all data flows across all schema using `pytest` and `mongomock` (limited Elasticsearch functionality is not currently included in the comprehensive test suite).
* Performs smoke tests on system initialisation (Elasticsearch not currently included).
* Containerized using Docker to ensure consistent deployment across all platforms.
* Orchestrated using Kubernetes (locally using Minikube).

### Planned:
For a detailed list of planned upgrades, please refer to the [specification.](./docs/specification.md#future-upgrades)

### Design Philosophy:
For a detailed look at the design philosophy, please refer to the [specification.](docs/specification.md#design-philosophy)

## How to Use
### Quick Start
* This application is developed and tested in a Linux environment.
    * If you're using Windows, it's recommended to set up [Windows Subsystem for Linux (WSL)](https://learn.microsoft.com/en-us/windows/wsl/install) to ensure compatibility.
* Clone the repository and navigate to the root directory of the project.
* Run the command `chmod +x setup.sh`.
* Run the command `./setup.sh` to initialise the database.
    * If installing Docker for the first time, and if using WSL, the official Docker installation script will note that it detected your WSL environment and recommend a Windows product instead. The script will then wait for 20 seconds. Ignore Docker. When the wait time ends you may be prompted for your password and installation will continue.
        * You will need to restart the terminal. It is recommended to simply close and re-open the terminal as `exec $SHELL` may not be sufficient for this occasion in WSL. After restarting the terminal, run `./setup.sh` once more.
    * When finished, run the command `scripts/clean.sh` to clean up containers and database volumes.
        * During development, all options were selected when running `scripts/clean.sh` to remove any clutter that may have impeded the successful initialisation of the app. Success is not necessarily guaranteed when opting out of optional clean-up steps. Please review `scripts/clean.sh`, which is brief, before execution on your system.
    * On very rare occasions the stable app has failed during the smoke testing phase of initialisation. If this happens, run `scripts/clean.sh` and then restart the system using `./setup.sh`.

### Guided Tour
* Copy the url provided in the terminal at the end of `setup.sh`'s execution or run `minikube ip` to retrieve the minikube ip for use in constructing the request address. This address (of the form `http://<minikube id>:30007/`) is used to make requests to the app.
    * ***Be sure to replace*** `<minikube ip>` ***in the request below with the ip address returned in your terminal.***
* Send GET requests to each endpoint using:
    * `curl http://<minikube ip>:30007/`
    * `curl http://<minikube ip>:30007/chemicals | jq`
    * `curl http://<minikube ip>:30007/lots | jq`
    * `curl http://<minikube ip>:30007/lists | jq`
* Log an example chemical template:
    * Copy/paste this command, after updating the minikube ip address, into your terminal and execute it.
    ```bash
    curl -s -X POST "http://<minikube ip>:30007/chemicals" \
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
        }'  | jq
    ```
    * It didn't work. Be sure to check the chemicals you requested from the API above when you executed `curl http://<minikube ip>:30007/chemicals | jq` to make sure there wasn't already a chemical in the system for the template you were trying to log. You may review [Features](#features) above or [Important Usage Information](docs/specification.md#important-usage-information) in the specifications for clarification, though the API was designed to be helpful enough to inform developers of what happened without referencing documentation.
* Try logging another chemical:
    * Copy/paste this command, after updating the minikube ip address, into your terminal and execute it.
    ```bash
    curl -s -X POST "http://<minikube ip>:30007/chemicals" \
        -H "Content-Type: application/json" \
        -d '{
            "Name": "Trifluoromethanesulfonic acid, 99%, extra pure",
            "CAS_Number": "1493-13-6",
            "Classification": "reagent",
            "Storage_Condition": "Ambient",
            "Source": "Purchased",
            "Purchased_Fields": {
                "Manufacturer": "Fisher Scientific",
                "Manufacturer_Part_Number": " AC169890011",
                "Amount": 1,
                "Units": "L",
                "Container_Type": "Bottle"
            }
        }' | jq
    ```
    * Ah, that didn't work, either, did it? We ran `curl http://<minikube ip>:30007/lists | jq` above. Double-check that response to see which fields are validated entry fields and locate the error.
* Log a fun and safe chemical (for real this time!):
    * Copy/paste this command, after updating the minikube ip address, into your terminal and execute it.
    ```bash
    curl -s -X POST "http://<minikube ip>:30007/chemicals" \
        -H "Content-Type: application/json" \
        -d '{
            "Name": "Trifluoromethanesulfonic acid, 99%, extra pure",
            "CAS_Number": "1493-13-6",
            "Classification": "Reagent",
            "Storage_Condition": "Ambient",
            "Source": "Purchased",
            "Purchased_Fields": {
                "Manufacturer": "Fisher Scientific",
                "Manufacturer_Part_Number": " AC169890011",
                "Amount": 1,
                "Units": "L",
                "Container_Type": "Bottle"
            }
        }' | jq
    ```
* Oops, it looks like trifluoromethanesulfonic acid isn't quite as fun as it sounds. We need to update its description in the database.
    * Although the terminal returned trifluoromethanesulfonic acid's `inserted_id` primary key, which we need to alter the record, let's try using Elasticsearch to find "trifluoromethanesulfonic acid" so that we can test the use of Elasticsearch functionality to retrieve MongoDB primary keys. Please execute the following command in your terminal (after updating it with minikube's ip address):
    ```bash
    curl http://<minikube ip>:30007/chemicals/search?query=trifloromethansulfonic | jq
    ```
    * Fortunately Elasticsearch's fuzzy searching completely circumvents the issue of chemists not picking easier chemical names and our typographical errors were no obstacle to our mutual success.
    * Please paste this completely valid command into your terminal, update it with minikube's ip address, update it with trifluoromethanesulfonic acid's `_id` as returned above in **BOTH** the address *and* the request body (ensure it's enclosed in quotes in the request body), and then execute your request.
    ```bash
    curl -s -X PUT "http://<minikube ip>:30007/chemicals/<chemical_id>" \
        -H "Content-Type: application/json" \
        -d '{
            "_id": "<chemical_id>",
            "Name": "Trifluoromethanesulfonic acid, 99%, extra pure",
            "CAS_Number": "1493-13-6",
            "Classification": "Super acid",
            "Storage_Condition": "Ambient",
            "Source": "Purchased",
            "Purchased_Fields": {
                "Manufacturer": "Fisher Scientific",
                "Manufacturer_Part_Number": "AC169890011",
                "Amount": 1,
                "Units": "L",
                "Container_Type": "Bottle"
            }
        }' | jq
    ```
* Retrieve the record to visually verify that the change was made using `curl http://<minikube ip>:30007/chemicals/<chemical_id> | jq`.
* Try running the pytest integration testing suite while the app is deployed in Minikube:
    * Get the name of the `conquest-lims-api-xxxxxx` pod:
      ```bash
      kubectl get pods
      ```
    * Exec into the pod (replace the pod's name with the actual pod name):

      ```bash
      kubectl exec -it <conquest-lims-api-xxxxx> -- /bin/bash
      ```
    * Run pytest:
      ```bash
      pytest
      ```
    * Please allow ~10 seconds for the last test to complete. It's waiting on an impending expiry date to pass before retrieving the lot record again and confirming that what wasn't expired 10 seconds ago is now expired.
    * The functional testing suite is comprehensive and worth glancing over, though the code isn't always as elegant as the app itself given that the app was the focus of this project.
    * Elasticsearch functionality is not currently included in functional testing.


### Software Requirements
* A Linux environment
* Docker (installation prompted and handled in `setup.sh`)
* jq (Linux package: command-line JSON processor; installation prompted and handled in `setup.sh`)
* Minikube (installation prompted and handled in `setup.sh`)
* All other dependencies are automatically installed in their containers.

### Project Structure
```bash
CONQUEST-LIMS/
│
├── app/
│   ├── __init__.py               # Initialises Flask app and MongoDB client
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
│   ├── api_reference.md          # Documentation for API endpoints
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
├── scripts/                      # Accessory shell scripts
│   ├── clean.sh                  # Tears down containers, pods, and volumes
│   ├── load_data.sh              # Called in setup.sh. Initialises database with data
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

### Initialising the App
Refer to the [Quick Start](#how-to-use) section. `setup.sh` handles app initialisation.

### Operation
#### API Base URL
Retrieve the minikube ip address at any time using `minikube ip`.
```bash
http://<minikube ip>:30007/
```

#### API Overview

| Entity    | Endpoint                            | Description       |
|-----------|-------------------------------------|-------------------|
| Chemicals | `/chemicals`                        | GET, POST         |
|           | `/chemicals/<chemical_id>`          | GET, PUT, DELETE  |
|           | `/chemicals/search?query=key+words` | GET               |
| Lots      | `/lots`                             | GET, POST         |
|           | `/lots/<lot_id>`                    | GET, PUT, DELETE  |
|           | `/lots/search?query=key+words`      | GET               |
|           | `/lots/analytics`                   | GET               |
| Lists     | `/lists`                            | GET, POST         |
|           | `/lists/<list_name>`                | GET, PUT, DELETE  |

Detailed request/response schemas are documented in the [API reference.](./docs/api_reference.md)

### Database Validation Rules
See the [API reference](docs/api_reference.md) for request body and response body structures, data types, and detailed notes by field. See the [specifications](docs/specification.md#data-schema) for database and Elasticsearch storage structures, data types, and detailed notes by field.

* All required fields must be present and non-empty.
* Data types are strictly enforced per schema.
* Validated-entry field values must reference existing list values (e.g., from the approved manufacturers list).
* Dates must arrive as timezone-aware ISO 8601 formatted strings (UTC offset must be of the form `+00:00`; `Z` will not work as a convention for the UTC timezone).
* Dates are stored and returned in the UTC timezone.
* Prepared lots must include at least one valid component.
* Lists must contain at least one entry.
* For a detailed look at the validation strategy, click [here](./docs/specification.md/#validation-strategy)

### Testing
Run all tests with:
* Inside Docker containers orchestrated using `docker compose`:
```bash
docker exec -it conquest-lims-api pytest
```
* When deployed locally using Minikube (as in production and as the system is packaged):
    * Get the name of the `conquest-lims-api-xxxxxx` pod:
      ```bash
      kubectl get pods
      ```
    * Exec into the pod (replace the pods name with the actual pod name):

      ```bash
      kubectl exec -it <conquest-lims-api-xxxxx> -- /bin/bash
      ```
    * Run pytest:
      ```bash
      pytest
      ```

## Technology
* **Linux:** Chosen for its stability, security, and prevalence in production environments. It provides a consistent platform for local development and deployment.

The following tech stack was chosen (and learned contemporaneously) to align my skills with the needs and practices of modern web development:
* **Flask:** A lightweight and flexible Python web framework ideal for building RESTful APIs. Its simplicity allowed for rapid development and easy integration with MongoDB and Elasticsearch.
* **MongoDB:** A document-based NoSQL database well-suited for the flexible and hierarchical structure of chemical and lot records which often contain nested or variable fields in addition to containing slight differences between sub-categories of purchased and prepared lots/chemicals. Allows CONQUEST LIMS to capitalize on the document-based database mantra that "information frequently accessed together should be stored together" by duplicating chemical template data onto lot record documents.
* **Elasticsearch:** Enables fast, fuzzy, full-text searches for chemical and lot names. Helps users locate records without needing exact matches in addition to providing aggregate search functionality.
* **Docker:** Ensures consistency between development and deployment by containerizing the application, database, and Elasticsearch with their exact dependencies.
* **Minikube:** Simulates a Kubernetes cluster locally thus allowing orchestration, scaling, and testing of multi-service architecture in a way that mirrors real-world deployments.

## What I Learned
I learned too much over the course of this project to complete this section with any level of detail without misrepresenting my education by omitting far too much of what I learned. My previous portfolio pieces demonstrate what I knew heading into this project.

In order to complete this project I had to learn, from scratch and simultaneously:
* Web development practices
* Flask
* NoSQL database basics
* MongoDB
* Elasticsearch
* Containerization
* Docker
* Enough Kubernetes to run a local cluster in Minikube

## Motivation
I am going to be a software engineer. I knew too much about system design and the fundamentals from my previous roles and have demonstrated the ability to learn new technology for a project too many times to enter the field as a junior engineer, so I wanted to build something that fully demonstrated my capabilities. The system is far from perfect given the constraints of working alone on a tight deadline, but I tried at least to document many of my ideas for upgrades in the [Future Upgrades](docs/specification.md#future-upgrades) section of the specifications to illustrate that, although I am operating as a sole contributor without the benefit of a team or the ability to delegate lower-level tasks, my mind is still oriented towards the bigger picture of system design and integration rather than merely trying to get the individual pieces to work.

## Contributions
This project is currently maintained internally and not open to contributions.

## License
No license. All rights reserved.
