from chemical_inventory_api_v1 import ListsSchema

"""
* post new, valid lists
* return list primary keys

* Send empty request body
* HTTP code 422:
    * miss req field
    * miss req value
    * wrong type (name field)
    * wrong type (list itself)
    * unexp field
    * list_name already exists (POST)
    * list_name doesn't exist (PUT)
"""

