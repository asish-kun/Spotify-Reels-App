# collection_routes.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import User, Post, Collection


collection_bp = Blueprint("collection_bp", __name__)


@collection_bp.route("", methods=["POST"])  # /api/collections
@jwt_required()
def create_collection():
    """
    POST /api/collections
    Body JSON:
    {
      "name": "My Best Snippets",
      "post_ids": [1, 2, 3]
    }
    """
    current_user_id = int(get_jwt_identity())
    data = request.get_json()
    name = data.get("name")
    post_ids = data.get("post_ids", [])

    if not name:
        return jsonify({"msg": "Collection name is required"}), 400

    new_collection = Collection(user_id=current_user_id, name=name)
    db.session.add(new_collection)
    db.session.commit()

    # If you have a many-to-many table linking collections <-> posts,
    # you'd insert those relationships here.
    # For example, a "collection_posts" association table.

    return jsonify({
        "msg": "Collection created",
        "collection_id": new_collection.id
    }), 201



@collection_bp.route("/user/<int:user_id>", methods=["GET"])  # /api/collections/user/1
def get_user_collections(user_id):
    """
    GET /api/collections/user/<user_id>
    Returns all collections for a particular user.
    """
    collections = Collection.query.filter_by(user_id=user_id).all()
    results = []
    for c in collections:
        results.append({
            "id": c.id,
            "name": c.name,
            "created_at": c.created_at.isoformat()
        })
    return jsonify(results), 200



@collection_bp.route("/<int:collection_id>", methods=["PUT"])
@jwt_required()
def update_collection(collection_id):
    """
    PUT /api/collections/<collection_id>
    Body: { "name": "New Name", "post_ids": [5,6] (optional) }
    """
    current_user_id = int(get_jwt_identity())
    data = request.get_json()
    coll = Collection.query.get(collection_id)
    if not coll:
        return jsonify({"msg": "Collection not found"}), 404

    if coll.user_id != current_user_id:
        return jsonify({"msg": "Unauthorized"}), 403

    new_name = data.get("name")
    if new_name:
        coll.name = new_name

    # If you have a relationship to posts, update that here:
    # e.g. remove old post associations, add new ones from `post_ids`.

    db.session.commit()
    return jsonify({"msg": "Collection updated"}), 200



@collection_bp.route("/<int:collection_id>", methods=["DELETE"])
@jwt_required()
def delete_collection(collection_id):
    """
    DELETE /api/collections/<collection_id>
    """
    current_user_id = int(get_jwt_identity())
    coll = Collection.query.get(collection_id)
    if not coll:
        return jsonify({"msg": "Collection not found"}), 404

    # Must own the collection
    if coll.user_id != current_user_id:
        return jsonify({"msg": "Unauthorized"}), 403

    db.session.delete(coll)
    db.session.commit()
    return jsonify({"msg": "Collection deleted"}), 200
