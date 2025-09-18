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

## Search Posts

### `GET /api/posts/search`

Search for posts by title or content.

#### Query Parameters

| Name       | Required | Description                                                                 |
|------------|----------|-----------------------------------------------------------------------------|
| `q`        | Yes      | Search term used to match against post titles and content.                  |
| `sort`     | No       | Field to sort by (e.g. `title`, `content`, `id`).                           |
| `direction`| No       | Sort direction: `asc` (default) or `desc`.                                  |

#### Examples

- `GET /api/posts/search?q=hello`  
  Searches for posts containing `hello` in the title or content.  

- `GET /api/posts/search?q=world&sort=title&direction=desc`  
  Searches for posts containing `world` and sorts results by title in descending order.  

#### Responses

- **200 OK** — Returns a JSON array of matching posts (empty array if no matches).  
- **400 Bad Request** — Returned if `q` is missing or invalid query parameters are provided.

## Data Storage
Posts are stored in `blog_posts.json` and persist across restarts.

## Usage
1. Run the backend:  
   `cd backend && python backend_app.py`
2. API available at: `http://127.0.0.1:5002/api/posts`

The frontend can connect to this API using the base URL `http://localhost:5002/api`.
