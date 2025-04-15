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
            # Build chemical record and insert into database
            record = new_chemical.build_chem_record(request.method)
            result = new_chemical.insert_update_chem_record(
                current_app.chemicals,
                record,
                request.method
            )

            # Index chemical name in Elasticsearch
            es_doc = {
                ChemicalSchema.NAME_KEY: record.get(
                    ChemicalSchema.NAME_KEY,
                    ""
                ),
                ################REEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE rename these as references to the database names
                "type": "chemical",
                "mongo_id": str(result.inserted_id)
            }

            current_app.es.index(
                index="chemicals",
                id=str(result.inserted_id),
                document=es_doc
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
                # Build updated chemical record and update in database
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
                
                # Update corresponding document in Elasticsearch
                try:
                    updated_es_doc = {
                        "name": record.get("name", ""),
                        "type": "chemical",
                        "mongo_id": chemical_id
                    }
                    current_app.es.index(index="chemicals", id=chemical_id, document=updated_es_doc)

                    response = jsonify({"modified_count": str(result.modified_count)}), 200

                except Exception as e:
                    response = jsonify({"error": f"Could not update document in Elasticsearch {e}"}), 500

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
        # Delete chemical record from the database
        result = current_app.chemicals.delete_one(
            {ChemicalSchema.CHEM_ID_KEY: ObjectId(chemical_id)}
        )

        if result.deleted_count == 0:
            response = jsonify({"error": "Not found"}), 404
        else:
            try:
                current_app.es.delete(index="chemicals", id=chemical_id)
                response = jsonify({"deleted_count": result.deleted_count}), 204
            except Exception as e:
                response = jsonify({"error": f"Failed to delete document in Elasticsearch {e}"}), 500

    except InvalidId:
        response = jsonify({"error": "Invalid ID format"}), 400   
    
    return response

@chemicals.route("/search", methods=["GET"])
def search_chemicals() -> Tuple[Response, int]:
    """
    Full-text search for chemicals by name.
    
    Parameters:
        query (str): Search keywords
    
    Returns:
        JSON list of matching chemical records with partial or full name matches
    """
    query = request.args.get("query")
    if not query:
        response = jsonify({"error": "Missing query"}), 400
    
    try:
        es_query = {
            "query": {
                "match": {
                    "name": {
                        "query": query,
                        "fuzziness": "AUTO"
                    }
                }
            }
        }

        results = current_app.es.search(index="chemicals", body=es_query)
        hits = results.get("hits", {}).get("hits", [])

        response_data = [
            {
                "_id": hit["_id"],
                "mongo_id": hit["_source"].get("mongo_id", ""),
                "name": hit["_source"].get("name", ""),
                "score": hit["_score"]
            }
            for hit in hits
        ]

        response = jsonify(response_data), 200

    except Exception as e:
        response = jsonify({"error": f"Elasticsearch unavailable{e}"})
    
    return response