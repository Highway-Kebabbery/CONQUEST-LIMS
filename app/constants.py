"""
This module stores system-level constants to reduce the use of string literals.
It was implemented late in development, so much of the API still required 
refactoring.
"""

# MongoDB collection names
LISTS_COLLECTION = "lists"
CHEMICALS_COLLECTION = "chemicals"
LOTS_COLLECTION = "lots"

# Elasticsearch keys
## Custom
ES_MONGO_ID_KEY = "Mongo_id"
ES_MONGO_COLL_KEY = "Mongo_Collection"

## Default


# MongoDB keys
##Default
MDB_INSERT_ID = "inserted_id"