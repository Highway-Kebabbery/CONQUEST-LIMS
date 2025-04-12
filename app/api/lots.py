"""
API endpoints for lists collection management.

This module defines CRUD routes for managing validated lot records.
Lot records represent a physical instance of a given chemical (e.g.
a bottle of Methanol received into the lab with a given lot number).

Lot records may be either purchased or prepared in-house. Lots prepared
in-house contain components that reference other existing lot records.
"""

from flask import Blueprint, request, jsonify, current_app
from flask.wrappers import Response
from app.utils.validation_error_codes import ValidationErrorCodes
from app.models.lots import LotSchema

from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime
from typing import Tuple
import copy

lots = Blueprint("lots", __name__)

@lots.route("", methods=["GET"])
def get_all_lots() -> Tuple[Response, int]:
    """
    Retrieve all lot documents from the database and convert non-JSON-serializable
    fields to JSON-serializable types.

    Returns:
        Tuple[Response, int]: A JSON response with all lot records and status code 200.
    """
    all_lots = list(current_app.lots.find())
    inval_json_types = (ObjectId, datetime)
    
    # Re-type JSON-incompatible data types to strings
    for lot in all_lots:
        for key in lot:
            if isinstance(lot[key], inval_json_types):
                lot[key] = str(lot[key])
            elif isinstance(lot[key], list) and isinstance(lot[key][0], dict):
                # Iterate through all values of all components
                for component in lot[key]:
                    comp_index = lot[key].index(component)
                    component_dict = lot[key][comp_index]
                    for subkey in component_dict:
                        if isinstance(component_dict[subkey], inval_json_types):
                            component_dict[subkey] = str(component_dict[subkey])

    response = jsonify(all_lots), 200

    return response

@lots.route("", methods=["POST"])
def add_lot() -> Tuple[Response, int]:
    """
    Add a new lot to the database. Requests are validated against database schema
    prior to insertion.

    Returns:
        Tuple[Response, int]: JSON response with inserted ID (201),
        or error message (4XX) if validation fails.
    """
    data = request.get_json()

    if not data:
        response = jsonify({"error": "Missing request body"}), 400
    else:
        # Validate data in request
        new_lot = LotSchema(
            copy.deepcopy(data),
            current_app.chemicals,
            current_app.lots
        )
        form_val = new_lot.validate_lot_form(request.method)
        
        if form_val[1] == 0:
            record = new_lot.build_lot_record()
            result = new_lot.insert_update_lot_record(
                current_app.chemicals,
                current_app.lots,
                record,
                request.method
            )

            response = jsonify({"inserted_id": str(result.inserted_id)}), 201

        elif form_val[1] == 5 or form_val[1] == 8:
            msg = ValidationErrorCodes.gen_val_err_msg(form_val)
            response = jsonify({"error": msg}), 404

        else:
            msg = ValidationErrorCodes.gen_val_err_msg(form_val)
            response = jsonify({"error": msg}), 422
    
    return response

@lots.route("/<lot_id>", methods=["GET"])
def get_lot(lot_id) -> Tuple[Response, int]:
    """
    Retrieve a lot record by primary key.

    Parameters:
        lot_id (str): ObjectId string of the lot to retrieve.

    Returns:
        Tuple[Response, int]: JSON-formatted lot or error message with code 4XX.
    """
    try:
        result = current_app.lots.find_one({LotSchema.LOT_ID_KEY: ObjectId(lot_id)})
        
        if not result:
            response = jsonify({"error": "Not found"}), 404
        else:
            inval_json_types = (ObjectId, datetime)

            # Re-type JSON-incompatible data types to strings
            for key in result:
                if isinstance(result[key], inval_json_types):
                    result[key] = str(result[key])
                elif isinstance(result[key], list) and isinstance(result[key][0], dict):
                    # Iterate through all values of all components
                    for component in result[key]:
                        comp_index = result[key].index(component)
                        component_dict = result[key][comp_index]
                        for subkey in component_dict:
                            if isinstance(component_dict[subkey], inval_json_types):
                                component_dict[subkey] = str(component_dict[subkey])

            response = jsonify(result), 200
    
    except InvalidId:
        response = jsonify({"error": "Invalid ID format"}), 400
    
    return response

@lots.route("/<lot_id>", methods=["PUT"])
def update_lot(lot_id) -> Tuple[Response, int]:
    """
    Update an existing lot record by primary key.

    Parameters:
        lot_id (str): ObjectId string of the lot to update.

    Returns:
        Tuple[Response, int]: Modified count or JSON-formatted error message 
        and a 4XX error code.
    """
    data = request.get_json()

    if not LotSchema.LOT_ID_KEY in data:
        response = jsonify({
            "error": f"Request body missing primary key: {LotSchema.LOT_ID_KEY}"
        }), 422
    elif not data[LotSchema.LOT_ID_KEY] == lot_id:
        response = jsonify({"error": "Request body primary key does not match address " \
            f"<lot_id>: {data[LotSchema.LOT_ID_KEY]}, {lot_id}"}), 422
    else:
        # Validate data in request
        updated_lot = LotSchema(
            copy.deepcopy(data),
            current_app.chemicals,
            current_app.lots
        )
        form_val = updated_lot.validate_lot_form(request.method)

        if form_val[1] == 0:
            try:
                record = updated_lot.build_lot_record()
                result = updated_lot.insert_update_lot_record(
                    current_app.chemicals,
                    current_app.lots,
                    record,
                    request.method,
                    lot_id
                )

                response = jsonify({"modified_count": str(result.modified_count)}), 200
            
            except InvalidId:
                # This is a failsafe. validate_lot_forms() handles this case.
                response = jsonify({"error": "Invalid ID format"}), 400
        elif form_val[1] == 5 or form_val[1] == 8:
            msg = ValidationErrorCodes.gen_val_err_msg(form_val)
            response = jsonify({"error": msg}), 404
        else:
            msg = ValidationErrorCodes.gen_val_err_msg(form_val)
            response = jsonify({"error": msg}), 422
    
    return response

@lots.route("/<lot_id>", methods=["DELETE"])
def delete_lot(lot_id) -> Tuple[Response, int]:
    """
    Delete a lot by primary key.

    Parameters:
        lot_id (str): ObjectId string of the lot to delete.

    Returns:
        Tuple[Response, int]: HTTP code 204 on success or 404 if not found.
    """
    try:
        result = current_app.lots.delete_one({LotSchema.LOT_ID_KEY: ObjectId(lot_id)})
       
        if result.deleted_count == 0:
            response = jsonify({"error": "Not found"}), 404
        else:
            response = "", 204

    except InvalidId:
        response = jsonify({"error": "Invalid ID format"}), 400

    return response
