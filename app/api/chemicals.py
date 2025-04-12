"""
API endpoints for chemical template and chemical database management.

This module provides CRUD routes for creating, retrieving,
updating, and deleting chemical template records. Chemical
records represent either a given manufacturer part number and amount
or a given chemical with a prescribed in-house preparation. Chemical
templates harmonize data entry for lots to prevent the creation of 
duplicate names for the same chemical.
"""

from flask import Blueprint, request, jsonify, current_app
from flask.wrappers import Response
from app.utils.validation_error_codes import ValidationErrorCodes
from app.models.chemicals import ChemicalSchema

from bson import ObjectId
from bson.errors import InvalidId
from typing import Tuple
import copy

chemicals = Blueprint("chemicals", __name__)

@chemicals.route("", methods=["GET"])
def get_all_chemicals() -> Tuple[Response, int]:
    """
    Retrieves all chemical template records from the database. Aggregate totals are
    refreshed before returning results.

    Returns:
        Tuple[Response, int]: JSON response containing all chemical templates and status code 200.
    """
    all_chem_ids = [
        chem[ChemicalSchema.CHEM_ID_KEY] for chem in current_app.chemicals.find(
            {},
            {ChemicalSchema.CHEM_ID_KEY: 1}
        )
    ]

    ChemicalSchema.query_current_totals(
        current_app.chemicals,
        current_app.lots,
        all_chem_ids,
        True
    )

    # Find and return refreshed records
    all_chemicals = list(current_app.chemicals.find())

    for chemical in all_chemicals:
        # Type ObjectId not JSON serializable
        chemical[ChemicalSchema.CHEM_ID_KEY] = str(
            chemical[ChemicalSchema.CHEM_ID_KEY]
        )

    response = jsonify(all_chemicals), 200

    return response

@chemicals.route("", methods=["POST"])
def add_chemical() -> Tuple[Response, int]:
    """
    Adds a new chemical template to the database. Requests are validated against
    database schema prior to insertion.

    Returns:
        Tuple[Response, int]: JSON response with inserted ID and status code 201 on success,
        or an error message with appropriate 4XX code on failure.
    """
    data = request.get_json()

    if not data:
        response = jsonify({"error": "Missing request body"}), 400
    else:
        # Validate data in request
        new_chemical = ChemicalSchema(
            copy.deepcopy(data),
            current_app.chemicals,
            current_app.lots
        )

        form_val = new_chemical.validate_chemical_form(request.method)

        if form_val[1] == 0:
            record = new_chemical.build_chem_record(request.method)
            result = new_chemical.insert_update_chem_record(
                current_app.chemicals,
                record,
                request.method
            )

            response = jsonify({"inserted_id": str(result.inserted_id)}), 201
        else:
            msg = ValidationErrorCodes.gen_val_err_msg(form_val)
            response = jsonify({"error": msg}), 422

    return response

@chemicals.route("/<chemical_id>", methods=["GET"])
def get_chemical(chemical_id) -> Tuple[Response, int]:
    """
    Retrieves a single chemical template by its primary key.

    Parameters:
        chemical_id (str): ObjectId string of the chemical to retrieve.

    Returns:
        Tuple[Response, int]: JSON response with the chemical record and status 200,
        or a 400/404 error response on failure.
    """
    try:
        chem_doc = current_app.chemicals.find_one(
            {ChemicalSchema.CHEM_ID_KEY: ObjectId(chemical_id)}
        )

        if not chem_doc:
            response = jsonify({"error": "Not found"}), 404
        else:
            # Update aggregate fields to reflect current state of lot database
            ChemicalSchema.query_current_totals(
                current_app.chemicals,
                current_app.lots,
                [chem_doc[ChemicalSchema.CHEM_ID_KEY]],
                True
            )

            # Find and return refreshed record
            chem_doc = current_app.chemicals.find_one(
                {ChemicalSchema.CHEM_ID_KEY: ObjectId(chemical_id)}
            )
            
            chem_doc[ChemicalSchema.CHEM_ID_KEY] = str(
                chem_doc[ChemicalSchema.CHEM_ID_KEY]
            )
            
            response = jsonify(chem_doc), 200
    except InvalidId:
        response = jsonify({"error": "Invalid ID format"}), 400

    return response

@chemicals.route("/<chemical_id>", methods=["PUT"])
def update_chemical(chemical_id) -> Tuple[Response, int]:
    """
    Updates a chemical template by primary key. Requests are 
    validated against database schema prior to insertion.

    Parameters:
        chemical_id (str): ObjectId string of the chemical to update. Must match the
        primary key in the request body.

    Returns:
        Tuple[Response, int]: JSON response with modified count and status 200 on success,
        or error response with status 400, 404, or 422.
    """
    data = request.get_json()
    
    if not ChemicalSchema.CHEM_ID_KEY in data:
        response = jsonify({
            "error": f"Request body missing primary key: {ChemicalSchema.CHEM_ID_KEY}"
        }), 422
    elif not data[ChemicalSchema.CHEM_ID_KEY] == chemical_id:
        response = jsonify({"error": "Request body primary key does not match address " \
            f"<chemical_id>: {data[ChemicalSchema.CHEM_ID_KEY]}, {chemical_id}"}), 422
            
    else:
        # Validate data in request
        updated_chemical = ChemicalSchema(
            copy.deepcopy(data),
            current_app.chemicals,
            current_app.lots
        )
        form_val = updated_chemical.validate_chemical_form(request.method)

        if form_val[1] == 0:
            try:
                record = updated_chemical.build_chem_record(
                    request.method,
                    chemical_id
                )

                result = updated_chemical.insert_update_chem_record(
                    current_app.chemicals,
                    record,
                    request.method,
                    chemical_id
                )
                
                response = jsonify({"modified_count": str(result.modified_count)}), 200

            except InvalidId:
                # This is a failsafe. validate_chemical_forms() handles this case.
                response = jsonify({"error": "Invalid ID format"}), 400
        elif form_val[1] == 5:
            msg = ValidationErrorCodes.gen_val_err_msg(form_val)
            response = jsonify({"error": msg}), 404
        else:
            msg = ValidationErrorCodes.gen_val_err_msg(form_val)
            response = jsonify({"error": msg}), 422

    return response

@chemicals.route("/<chemical_id>", methods=["DELETE"])
def delete_chemical(chemical_id) -> Tuple[Response, int]:
    """
    Deletes a chemical template by its primary key.

    Parameters:
        chemical_id (str): ObjectId string of the chemical to delete.

    Returns:
        Tuple[Response, int]: JSON response with deleted count and status 204 on success,
        or error response with status 400 or 404.
    """
    try:
        result = current_app.chemicals.delete_one(
            {ChemicalSchema.CHEM_ID_KEY: ObjectId(chemical_id)}
        )

        if result.deleted_count == 0:
            response = jsonify({"error": "Not found"}), 404
        else:
            response = jsonify({"deleted_count": result.deleted_count}), 204

    except InvalidId:
        response = jsonify({"error": "Invalid ID format"}), 400   
    
    return response
