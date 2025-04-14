# post_routes.py
import os
import uuid
from flask import Blueprint, request, jsonify, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from extensions import db
from models import Post, Like, Comment
from urllib.parse import urljoin
# Boto3 import
import boto3
from botocore.exceptions import ClientError

post_bp = Blueprint("post_bp", __name__)

# --------------------------------------------------
# 1. Upload a new post with video/audio snippet
# --------------------------------------------------
@post_bp.route("", methods=["POST"])  # /api/posts
@jwt_required()
def create_post():
    print("create_post route was hit!")
    current_user_id = int(get_jwt_identity())

    # 1. Grab the uploaded file from form-data
    file = request.files.get('file')
    if not file:
        return jsonify({"msg": "No file uploaded"}), 400

    # 2. Extract any other form fields you want
    caption = request.form.get('caption', "")
    genres = request.form.get('genres', "")
    location = request.form.get('location', "")

    # 3. Upload file to S3
    uploaded_url = upload_file_to_s3(file)
    if not uploaded_url:
        return jsonify({"msg": "Error uploading to S3"}), 500

    # 4. Construct your new Post record
    new_post = Post(
        user_id=current_user_id,
        media_url=uploaded_url,  # S3 public URL
        caption=caption,
        genres=genres,
        location=location
    )

    # 5. Persist to DB
    db.session.add(new_post)
    db.session.commit()

    return jsonify({
        "msg": "Post created",
        "post_id": new_post.id,
        "media_url": new_post.media_url
    }), 201

# This is your S3 bucket name
S3_BUCKET = "my-app-reels"
# region name: e.g., 'us-east-1' (or wherever your bucket is located)
AWS_REGION = "us-east-1"


def upload_file_to_s3(file_obj, bucket_name=S3_BUCKET, acl="public-read"):
    """
    Uploads a FileStorage object directly to S3.
    Returns the public S3 URL of the uploaded file.
    """
    s3 = boto3.client("s3", region_name=AWS_REGION)

    # Generate a unique filename to avoid collisions
    # Use uuid or you can do secure_filename + some randomization
    file_extension = file_obj.filename.split('.')[-1].lower()
    filename = f"{uuid.uuid4()}.{file_extension}"

    # (Optional) store it in a "reels/" folder in the bucket
    key = f"reels/{filename}"

    try:
        # Upload to S3
        s3.upload_fileobj(
            file_obj,
            bucket_name,
            key,
            ExtraArgs={
                "ContentType": file_obj.content_type  # important for video
            }
        )
    except ClientError as e:
        print(e)
        return None

    # Construct the S3 URL – format depends on region & bucket settings
    # For most AWS regions: https://{bucket}.s3.{region}.amazonaws.com/{key}
    # If it's the "classic" region or older buckets it can be slightly different
    file_url = f"https://{bucket_name}.s3.{AWS_REGION}.amazonaws.com/{key}"
    return file_url


# --------------------------------------------------
# 2. Retrieve vertical reels feed
# --------------------------------------------------
@post_bp.route("", methods=["GET"])  # /api/posts
def get_reels_feed():
    """
    GET /api/posts
    Return a list of posts, presumably in reverse chronological order
    or some recommendation-based order.

    On the FRONTEND:
    - You’d keep a small queue of upcoming reels in memory.
    - As the user scrolls, you automatically load the next post from the queue.
    - Meanwhile, the app quietly fetches the next batch in the background
      so you’re never waiting too long for a new reel.

    On the BACKEND:
    - You can handle pagination (limit & offset). 
    - This is a simple version returning everything.
    """
    # For a real feed system, you'd implement pagination or recommendation logic.
    # Let's do a simple "all posts" approach, newest first.
    
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("limit", 5))
    posts = Post.query.order_by(Post.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    results = [{
        "id": p.id,
        "user_id": p.user_id,
        "media_url": p.media_url,
        "caption": p.caption,
        "created_at": p.created_at.isoformat()
    } for p in posts.items]

    return jsonify({
        "page": page,
        "posts": results
    }), 200

# to get all the posts related to this user
@post_bp.route("/user/<int:user_id>", methods=["GET"])
def get_posts_for_user(user_id):
    """
    GET /api/posts/user/<user_id>
    Returns all posts belonging to the given user, newest first.
    """
    posts = Post.query.filter_by(user_id=user_id).order_by(Post.created_at.desc()).all()
    
    results = []
    for p in posts:
        results.append({
            "id": p.id,
            "user_id": p.user_id,
            "media_url": p.media_url,
            "caption": p.caption,
            "genres": p.genres,
            "location": p.location,
            "created_at": p.created_at.isoformat()
        })
    
    return jsonify(results), 200


@post_bp.route("/<int:post_id>", methods=["GET"])  # /api/posts/<post_id>
def get_single_post(post_id):
    """
    GET /api/posts/<post_id>
    Retrieve a single post's details
    """
    post = Post.query.get(post_id)
    if not post:
        return jsonify({"msg": "Post not found"}), 404

    return jsonify({
        "id": post.id,
        "user_id": post.user_id,
        "media_url": post.media_url,
        "caption": post.caption,
        "created_at": post.created_at.isoformat()
    }), 200


# --------------------------------------------------
# 3. Likes
# --------------------------------------------------
@post_bp.route("/<int:post_id>/like", methods=["POST"])
@jwt_required()
def like_post(post_id):
    """
    POST /api/posts/<post_id>/like
    """
    current_user_id = int(get_jwt_identity())

    # Check if user already liked
    existing_like = Like.query.filter_by(user_id=current_user_id, post_id=post_id).first()
    if existing_like:
        return jsonify({"msg": "You already liked this post"}), 400

    new_like = Like(user_id=current_user_id, post_id=post_id)
    db.session.add(new_like)
    db.session.commit()

    return jsonify({"msg": "Post liked"}), 201


@post_bp.route("/<int:post_id>/like", methods=["DELETE"])
@jwt_required()
def unlike_post(post_id):
    """
    DELETE /api/posts/<post_id>/like
    """
    current_user_id = int(get_jwt_identity())
    existing_like = Like.query.filter_by(user_id=current_user_id, post_id=post_id).first()
    if not existing_like:
        return jsonify({"msg": "Like not found"}), 404

    db.session.delete(existing_like)
    db.session.commit()
    return jsonify({"msg": "Like removed"}), 200


# --------------------------------------------------
# 4. Comments
# --------------------------------------------------
@post_bp.route("/<int:post_id>/comment", methods=["POST"])
@jwt_required()
def add_comment(post_id):
    """
    POST /api/posts/<post_id>/comment
    """
    current_user_id = int(get_jwt_identity())
    data = request.get_json()
    text = data.get("text")

    if not text:
        return jsonify({"msg": "Comment text required"}), 400

    new_comment = Comment(user_id=current_user_id, post_id=post_id, text=text)
    db.session.add(new_comment)
    db.session.commit()

    return jsonify({
        "msg": "Comment added",
        "comment_id": new_comment.id
    }), 201


@post_bp.route("/<int:post_id>/comments", methods=["GET"])
def get_comments(post_id):
    """
    GET /api/posts/<post_id>/comments
    """
    comments = Comment.query.filter_by(post_id=post_id).order_by(Comment.created_at.asc()).all()
    results = []
    for c in comments:
        results.append({
            "id": c.id,
            "user_id": c.user_id,
            "text": c.text,
            "created_at": c.created_at.isoformat()
        })

    return jsonify(results), 200


@post_bp.route("/comments/<int:comment_id>", methods=["DELETE"])
@jwt_required()
def delete_comment(comment_id):
    """
    DELETE /api/posts/comments/<comment_id>
    """
    current_user_id = int(get_jwt_identity())
    comment = Comment.query.get(comment_id)
    if not comment:
        return jsonify({"msg": "Comment not found"}), 404

    if comment.user_id != current_user_id:
        return jsonify({"msg": "Unauthorized"}), 403

    db.session.delete(comment)
    db.session.commit()
    return jsonify({"msg": "Comment deleted"}), 200
