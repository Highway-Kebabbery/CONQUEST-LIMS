# <div align="center">CONQUEST-LIMS</div>
## Description
CONQUEST-LIMS is a lightweight, Flask- and MongoDB-based Laboratory Information Management System (LIMS) built to manage chemical inventories in highly regulated lab environments. It has a robust validation system and supports CRUD operations for chemical templates, lot records, and field-validated entry lists.

## Features
### Current
* Chemical templates: Defines a unique combinations of manufacturer, part number, and container data to standardize the entry of standards and reagents and avoid the creation of duplicate entries.
* Lot management: Record and manage bottles or containers tied to a specific chemical template.
* Supports separate, tailored data for in-house prepared standards or reagents and externally purchased standards or reagents.
* Supports validated field entry using lists of approved values to harmonize the entry of data in important fields across all users.
* Robust, schema-level validation to guarantee adherance to database schema.
* Offers an API with CRUD endpoints for all record types following RESTful design principles.
* A robust, full integration test suite validating all data flows across all schema using `pytest` and `mongomock`.

### Planned:
* The app is currently undergoing containerization using Docker and orchestration using Minikube.
* Following this, ElasticSearch will be implemented for fuzzy searches of chemical and lot names.
* For a detailed list of additional planned upgrades, please refer to [docs/specification.md](./docs/specification.md)

## How to Use

(Fill this out once app is containerized. Probably won't change after implementing ElasticSearch.)

### Software Requirements
(Fill this out once app is containerized. Probably won't change after implementing ElasticSearch.)

### Project Structure
(Come back and fill this in once the project is completely finished. In the meantime, check [here](./docs/specification.md/#project-structure)

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