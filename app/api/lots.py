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
from app.constants import LOTS_COLLECTION, ES_MONGO_ID_KEY, ES_MONGO_COLL_KEY

from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime, timezone
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
        Tuple[Response, int]: JSON response with inserted ID (201)
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

            # Index lot in Elasticsearch
            es_doc = {
                ES_MONGO_COLL_KEY: LOTS_COLLECTION,
                LotSchema.NAME_KEY: record.get(
                    LotSchema.NAME_KEY,
                    ""
                ),
                ES_MONGO_ID_KEY: str(result.inserted_id),
                LotSchema.EXPIRY_KEY: record[LotSchema.EXPIRY_KEY],
                LotSchema.EMPTY_KEY: record[LotSchema.EMPTY_KEY]
            }
            if LotSchema.OPEN_KEY in record:
                es_doc[LotSchema.OPEN_KEY] = record[LotSchema.OPEN_KEY]
            elif LotSchema.PREP_DATE_KEY in record:
                es_doc[LotSchema.PREP_DATE_KEY] = record[LotSchema.PREP_DATE_KEY]
            
            try:
                es_result = current_app.es.index(
                    index=LOTS_COLLECTION,
                    id=str(result.inserted_id),
                    document=es_doc
                )

                if (
                    es_result.get("result") != "created"
                    or es_result.get("_shards", {}).get("failed", 1) > 0
                ):
                    response = jsonify({
                        "inserted_id": str(result.inserted_id),
                        "warning": "Inserted to MongoDB; failed to index in Elasticsearch."
                    }), 207

            except Exception as e:
                response = jsonify({
                        "inserted_id": str(result.inserted_id),
                        "warning": f"Inserted to MongoDB; failed to index in Elasticsearch: {e}"
                    }), 207
                
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

                # Index lot in Elasticsearch
                es_doc = {
                    ES_MONGO_COLL_KEY: LOTS_COLLECTION,
                    LotSchema.NAME_KEY: record.get(
                        LotSchema.NAME_KEY,
                        ""
                    ),
                    ES_MONGO_ID_KEY: lot_id,
                    LotSchema.EXPIRY_KEY: record[LotSchema.EXPIRY_KEY],
                    LotSchema.EMPTY_KEY: record[LotSchema.EMPTY_KEY]
                }
                if LotSchema.OPEN_KEY in record:
                    es_doc[LotSchema.OPEN_KEY] = record[LotSchema.OPEN_KEY]
                elif LotSchema.PREP_DATE_KEY in record:
                    es_doc[LotSchema.PREP_DATE_KEY] = record[LotSchema.PREP_DATE_KEY]
                
                try:
                    es_result = current_app.es.index(
                        index=LOTS_COLLECTION,
                        id=lot_id,
                        document=es_doc
                    )

                    if (
                        es_result.get("result") != "created"
                        or es_result.get("_shards", {}).get("failed", 1) > 0
                    ):
                        response = jsonify({
                            "warning": "Updated in MongoDB; failed to index in Elasticsearch."
                        }), 207

                except Exception as e:
                    response = jsonify({
                            "warning": "Updated in MongoDB; failed to index in Elasticsearch: {e}"
                        }), 207
                
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

            # Delete from Elasticsearch
            try:
                deleted_es_result = current_app.es.delete(
                    index=LOTS_COLLECTION,
                    id=lot_id
                )

                if (
                    deleted_es_result.get("result") != "deleted"
                    or deleted_es_result.get("_shards", {}).get("failed", 1) > 0
                ):
                    response = jsonify({
                        "warning": "Deleted from MongoDB; failed to delete from Elasticsearch."
                    }), 207

            except Exception as e:
                response = jsonify({
                        "warning": f"Deleted from MongoDB; failed to delete from Elasticsearch: {str(e)}"
                    }), 207
                
    except InvalidId:
        response = jsonify({"error": "Invalid ID format"}), 400

    return response

@lots.route("/search",methods=["GET"])
def search_lots() -> Tuple[Response, int]:
    """
    Full-text search for lots by name.

    Parameters:
        query (str): Search keywords
    
    Returns:
        JSON list of matching lot records with partial or full name matches.
    """
    query = request.args.get("query")
    if not query:
        response = jsonify({"error": "Missing query"}), 400

    try:
        es_query = {
            "query": {
                "match": {
                    LotSchema.NAME_KEY: {
                        "query": query,
                        "fuzziness": "AUTO"
                    }
                }
            }
        }

        results = current_app.es.search(
            index=LOTS_COLLECTION,
            body=es_query
        )
        hits = results.get("hits", {}).get("hits", [])

        response_data = []
        for hit in hits:
            source = hit["_source"]

            lot_data = {
                "_id": hit["_id"],
                ES_MONGO_COLL_KEY: source.get(
                    ES_MONGO_COLL_KEY,
                    ""
                ),
                LotSchema.NAME_KEY: source.get(
                    LotSchema.NAME_KEY,
                    ""
                ),
                ES_MONGO_ID_KEY: source.get(
                    ES_MONGO_ID_KEY,
                    ""
                ),
                LotSchema.EXPIRY_KEY: source.get(
                    LotSchema.EXPIRY_KEY,
                    ""
                ),
                LotSchema.EMPTY_KEY: source.get(
                    LotSchema.EMPTY_KEY,
                    ""
                ),
                "score": hit["_score"]
            }

            if LotSchema.OPEN_KEY in source:
                lot_data[LotSchema.OPEN_KEY] = source[LotSchema.OPEN_KEY]
            elif LotSchema.PREP_DATE_KEY in source:
                lot_data[LotSchema.PREP_DATE_KEY] = source[LotSchema.PREP_DATE_KEY]
            
            response_data.append(lot_data)
                
        response = jsonify(response_data), 200

    except Exception as e:
        response = jsonify({"error": f"Elasticsearch unavailable: {e}"})
    
    return response

@lots.route("/analytics",methods=["GET"])
def get_lot_analytics() -> Tuple[Response, int]:
    """
    Returns analytics related to the lots collection.

    Parameters:
        None
    
    Returns:
        JSON object with: the total number of available lots logged in the system, the 
        number of lots awaiting disposal (expired but not empty), and the name of the 
        chemical with the most lots logged under its primary key.
    """
    # Find number of lots logged
    now = datetime.now(timezone.utc)
    total_lots = current_app.lots.count_documents({
        "$and": [
            {LotSchema.EXPIRY_KEY: {"$gt": now}},
            {LotSchema.EMPTY_KEY: {"$eq": None}}
        ]
    })

    lots_awaiting_disposal = current_app.lots.count_documents({
        "$and": [
            {LotSchema.EXPIRY_KEY: {"$lte": now}},
            {LotSchema.EMPTY_KEY: {"$eq": None}}
        ]
    })

    # Aggregation query
    # '.keyword' specifies an exact-match search
    es_agg_query = {
        "size": 0,
        "aggs": {
            "top_lots": {
                "terms": {
                    "field": "Name.keyword",
                    "size": 3
                }
            }
        }
    }

    try:
        es_response = current_app.es.search(index=LOTS_COLLECTION, body=es_agg_query)
        top_lots_buckets = es_response.get("aggregations", {}).get("top_lots", {}).get("buckets", [])

        top_lots = [bucket["key"] for bucket in top_lots_buckets]

        response = jsonify({
            "total_lots_all_chemicals": total_lots,
            "lots_awaiting_disposal": lots_awaiting_disposal,
            "most_populous_chemicals": top_lots
        }), 200

    except Exception as e:
        response = jsonify({"error": f"Failed to retrieve analytics: {e}"})

    return response