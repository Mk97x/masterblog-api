from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import json

app = Flask(__name__)
CORS(app) 


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_FILE = os.path.join(SCRIPT_DIR, 'blog_posts.json')


def load_posts():
    """
    Load blog posts from the JSON file.
    If the file doesn't exist, create it with default posts.
    Returns a list of posts.
    """
    print(f"Loading data from: {JSON_FILE}")
    if not os.path.exists(JSON_FILE):
        print("File not found. Creating new file with default posts.")
        initial_posts = [
            {"id": 1, "title": "First post", "content": "This is the first post."},
            {"id": 2, "title": "Second post", "content": "This is the second post."},
        ]
        save_posts(initial_posts)
        return initial_posts

    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as file:
            data = json.load(file)
            print(f"Loaded {len(data)} posts.")
            return data
    except Exception as e:
        print(f"Failed to read JSON file: {e}")
        return []


def save_posts(posts):
    """
    Save the list of posts to the JSON file.
    Ensures data persistence across server restarts.
    """
    try:
        with open(JSON_FILE, 'w', encoding='utf-8') as file:
            json.dump(posts, file, indent=4, ensure_ascii=False)
        print(f"Successfully saved to {JSON_FILE}")
    except Exception as e:
        print(f"Failed to save posts: {e}")


def get_next_id():
    """
    Generate the next available unique ID.
    Returns 1 if no posts exist, otherwise max ID + 1.
    """
    if not POSTS:
        return 1
    return max(post["id"] for post in POSTS) + 1

def delete_post_by_id(post_id):
    """
    Delete a post by its 'id' (not index).
    Returns the deleted post if found, otherwise None.
    """
    global POSTS
    for post in POSTS:
        if post["id"] == post_id:
            POSTS.remove(post)
            save_posts(POSTS) 
            return post
    return None

def fetch_post_by_id(post_id):
    """
    Fetch a post by its 'id'.
    Returns the post if found, otherwise None.
    """
    for post in POSTS:
        if post["id"] == post_id:
            return post
    return None


POSTS = load_posts()

@app.route('/api/posts', methods=['POST'])
def add_post():
    """
    Handle POST request to add a new blog post.
    Expects JSON with 'title' and 'content'.
    Returns the created post with status 201.
    """
    global POSTS

    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 415

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    title = data.get("title")
    content = data.get("content")

    if not title:
        return jsonify({"error": "Missing required field: title"}), 400
    if not content:
        return jsonify({"error": "Missing required field: content"}), 400

    new_id = get_next_id()
    new_post = {
        "id": new_id,
        "title": title,
        "content": content
    }

    POSTS.append(new_post)
    save_posts(POSTS)

    return jsonify(new_post), 201


@app.route('/api/posts', methods=['GET'])
def get_posts():
    """
    Retrieve all blog posts with optional filtering and sorting.
    Supports:
    - ?q=<query>          : Search in title and content
    - ?sort=<field>       : Sort by 'title', 'content', or 'id'
    - ?direction=<asc/desc>: Sort order

    If no parameters, returns posts in original order.
    Returns 400 for invalid parameters.
    """
    sort = request.args.get('sort')
    direction = request.args.get('direction', 'asc')
    query = request.args.get('q', '').strip()

    allowed_sort_fields = ['title', 'content', 'id']
    allowed_directions = ['asc', 'desc']

    #error handling
    if direction not in allowed_directions:
        return jsonify({
            "error": f"Invalid direction: '{direction}'. Allowed values: {allowed_directions}"
        }), 400
    if sort and sort not in allowed_sort_fields:
        return jsonify({
            "error": f"Invalid sort field: '{sort}'. Allowed values: {allowed_sort_fields}"
        }), 400

    
    posts_to_return = POSTS.copy() # copy to maintain original list

    # filter for search term, if given
    if query:
        posts_to_return = [
            post for post in posts_to_return
            if query.lower() in post['title'].lower() or query.lower() in post['content'].lower()
        ]

    if sort:
        reverse = direction == 'desc'
        if sort == 'id':
            # sort numerical
            posts_to_return.sort(key=lambda p: p['id'], reverse=reverse)
        else:
            # sort text
            posts_to_return.sort(key=lambda p: str(p[sort]).lower(), reverse=reverse)

    return jsonify(posts_to_return)


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    """
    DELETE /api/posts/<id>
    Delete a post by its ID.
    Returns 200 with message if deleted, 404 if not found.
    """
    deleted_post = delete_post_by_id(post_id)
    if deleted_post:
        return jsonify({
            "message": "Post deleted successfully",
            "deleted": deleted_post
        }), 200
    else:
        return jsonify({"error": "Post not found"}), 404


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    """
    PUT /api/posts/<id>
    Update a blog post by ID.
    Expects JSON with 'title' and/or 'content'.
    Returns updated post on success, 404 if not found.
    """
    global POSTS

    post = fetch_post_by_id(post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404

    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 415

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    # update provided fields
    if 'title' in data:
        if not data['title'].strip():
            return jsonify({"error": "Title cannot be empty"}), 400
        post['title'] = data['title'].strip()

    if 'content' in data:
        if not data['content'].strip():
            return jsonify({"error": "Content cannot be empty"}), 400
        post['content'] = data['content'].strip()

    save_posts(POSTS)

    return jsonify(post), 200

@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    """
    Search posts by title or content.
    Supports: ?title=... and/or ?content=...
    Returns posts where title OR content matches the search terms.
    """
    title_query = request.args.get('title', '').strip()
    content_query = request.args.get('content', '').strip()

    if not title_query and not content_query:
        return jsonify(POSTS)

    filtered_posts = []
    for post in POSTS:
        title_match = title_query and title_query.lower() in post['title'].lower()
        content_match = content_query and content_query.lower() in post['content'].lower()
        
        
        include_post = False
        if title_query and content_query:
            include_post = title_match or content_match
        elif title_query:
            include_post = title_match
        elif content_query:
            include_post = content_match
            
        if include_post:
            filtered_posts.append(post)

    return jsonify(filtered_posts)

if __name__ == '__main__':
    print(f"Server starting on http://127.0.0.1:5002")
    app.run(host="0.0.0.0", port=5002, debug=True)