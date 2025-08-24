# masterblog-api

A lightweight Flask-based blog API with CRUD operations, search, and sorting.

## Endpoints

### GET /api/posts
Retrieve all blog posts. Optional query parameters:
- `q`: Search term (matches in title or content)
- `sort`: Field to sort by (`title`, `content`, `id`)
- `direction`: Sort order (`asc` or `desc`, default: `asc`)

Examples:
- `/api/posts?q=hello&sort=title&direction=desc`

Returns 400 for invalid parameters.

### POST /api/posts
Add a new post. Expects JSON with `title` and `content`.  
Returns the created post with generated `id` (status 201).  
Returns 400 if fields are missing.

### PUT /api/posts/<id>
Update a post by ID. Supports partial updates.  
Returns updated post (200) or 404 if not found.

### DELETE /api/posts/<id>
Delete a post by ID.  
Returns 200 on success, 404 if not found.

## Data Storage
Posts are stored in `blog_posts.json` and persist across restarts.

## Usage
1. Run the backend:  
   `cd backend && python backend_app.py`
2. API available at: `http://127.0.0.1:5002/api/posts`

The frontend can connect to this API using the base URL `http://localhost:5002/api`.

## Note
Search is integrated into the main `/api/posts` endpoint using the `q` parameter.  
There is no separate search route.