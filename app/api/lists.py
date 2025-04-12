"""
API endpoints for lists collection management.

This module defines CRUD routes for managing validated list records.
These lists serve as canonical sources for constrained field values
(e.g., manufacturers, container types, storage conditions) and are 
used for harmonizing data entry across all chemical and lot records.
"""

from flask import Blueprint, request, jsonify, current_app
from flask.wrappers import Response
from app.utils.validation_error_codes import ValidationErrorCodes
from app.models.lists import ListsSchema

from typing import Tuple
import copy

lists = Blueprint("lists", __name__)

@lists.route("", methods=["GET"])
def get_all_lists() -> Tuple[Response, int]:
    """
    Retrieve all list documents from the database.

    Returns:
        Tuple[Response, int]: A JSON response containing all lists and a 200 status code.
    """
    all_lists = list(current_app.lists.find(
        {},
        {"_id": 0}
    ))
    
    response = jsonify(all_lists), 200

    return response

@lists.route("", methods=["POST"])
def add_list() -> Tuple[Response, int]:
    """
    Add a new validated list to the database. Requests are validated against
    database schema prior to insertion.

    Returns:
        Tuple[Response, int]: A JSON response containing the inserted ID and a 201 status code,
        or an error message with a 4XX status code if validation fails.
    """
    data = request.get_json()

    if not data:
        response = jsonify({"error": "Missing request body"}), 400
    else:
        # Validate data in request
        new_list = ListsSchema(
            copy.deepcopy(data),
            current_app.lists
        )
        form_val = new_list.validate_list_form(request.method)
        
        if form_val[1] == 0:
            record = new_list.build_list_record()
            result = new_list.insert_update_list_record(
                current_app.lists,
                record,
                request.method
            )

            response = jsonify({"inserted_id": str(result.inserted_id)}), 201
        else:
            msg = ValidationErrorCodes.gen_val_err_msg(form_val)
            response = jsonify({"error": msg}), 422
    
    return response

@lists.route("/<list_name>", methods=["GET"])
def get_list(list_name) -> Tuple[Response, int]:
    """
    Retrieve a specific list by primary key ("Name").

    Parameters:
        list_name (str): The name of the list to fetch.

    Returns:
        Tuple[Response, int]: JSON response with list data and status 200,
        or an error message with status 404 if not found.
    """
    result = current_app.lists.find_one(
        {ListsSchema.LIST_NAME_KEY: list_name},
        {ListsSchema.LIST_ID_KEY: 0}
    )
    
    if not result:
        response = jsonify({"error": "List not found"}), 404
    else:
        response = jsonify(result), 200
    
    return response

@lists.route("/<list_name>", methods=["PUT"])
def update_list(list_name) -> Tuple[Response, int]:
    """
    Update an existing list by primary key ("Name"). Requests are validated against
    database schema prior to insertion.

    Parameters:
        list_name (str): Name of the list to update. Must match the name in the 
        request body.

    Returns:
        Tuple[Response, int]: JSON response with modified count and status 200 on success,
        or an error message with status 404 or 422 on failure.
    """
    data = request.get_json()

    if not ListsSchema.LIST_NAME_KEY in data:
        response = jsonify({
            "error": f"Request body missing primary key: {ListsSchema.LIST_NAME_KEY}"
        }), 422
    elif not data[ListsSchema.LIST_NAME_KEY] == list_name:
        response = jsonify({"error": "Request body primary key does not match address " \
            f"<list_name>: {data[ListsSchema.LIST_NAME_KEY]}, {list_name}"}), 422
    else:
        # Validate data in request
        updated_list = ListsSchema(
            copy.deepcopy(data),
            current_app.lists
        )
        form_val = updated_list.validate_list_form(request.method)

        if form_val[1] == 0:
            record = updated_list.build_list_record()
            result = updated_list.insert_update_list_record(
                current_app.lists,
                record,
                request.method,
                list_name    
            )

            response = jsonify({"modified_count": str(result.modified_count)}), 200
        elif form_val[1] == 13:
            msg = ValidationErrorCodes.gen_val_err_msg(form_val)
            response = jsonify({"error": msg}), 404
        else:
            msg = ValidationErrorCodes.gen_val_err_msg(form_val)
            response = jsonify({"error": msg}), 422

    return response

@lists.route("/<list_name>", methods=["DELETE"])
def delete_list(list_name) -> Tuple[Response, int]:
    """
    Delete a validated list from the database by primary key ("Name"). This action 
    is not recommended in production environments.

    Parameters:
        list_name (str): Name of the list to delete.

    Returns:
        Tuple[Response, int]: Empty response with 204 on success,
        or error message with 404 if the list is not found.
    """
    result = current_app.lists.delete_one(
        {ListsSchema.LIST_NAME_KEY: list_name}
        )
    
    if result.deleted_count == 0:
        response = jsonify({"error": "List not found"}), 404
    else:
        response = "", 204
    
    return response
