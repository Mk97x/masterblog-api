const AUTO_LOAD_ON_START = false;

const apiBaseUrlInput = document.getElementById('api-base-url');
const postTitleInput = document.getElementById('post-title');
const postContentInput = document.getElementById('post-content');
const postContainer = document.getElementById('post-container');

const sortFieldSelect = document.getElementById('sort-field');
const sortDirectionSelect = document.getElementById('sort-direction');
const searchInput = document.getElementById('search-query');

window.onload = function() {
    const savedUrl = localStorage.getItem('apiBaseUrl');
    if (savedUrl) {
        apiBaseUrlInput.value = savedUrl;
    }

    if (savedUrl && AUTO_LOAD_ON_START) {
        loadPosts();
    }
};

function loadPosts() {
    const baseUrl = apiBaseUrlInput.value.trim();
    if (!baseUrl) {
        showError("Please enter a valid API base URL.");
        return;
    }

    localStorage.setItem('apiBaseUrl', baseUrl);

    let url;
    const query = searchInput?.value.trim();
    
    // Wenn Suchbegriff vorhanden, verwende den neuen Search Endpoint
    if (query) {
        // Suche in beiden Feldern (Titel UND Content) - passt zu deiner Backend-Logik
        url = `${baseUrl}/posts/search?title=${encodeURIComponent(query)}&content=${encodeURIComponent(query)}`;
    } else {
        // Normale Posts-Anzeige mit Sortierung
        let base_url = `${baseUrl}/posts`;
        const params = new URLSearchParams();
        
        const sortField = sortFieldSelect?.value;
        const sortDirection = sortDirectionSelect?.value;
        if (sortField) params.append('sort', sortField);
        if (sortDirection) params.append('direction', sortDirection);
        
        url = params.toString() ? `${base_url}?${params.toString()}` : base_url;
    }

    postContainer.innerHTML = '<p>Loading posts...</p>';

    fetch(url, {
        method: 'GET',
        headers: { 'Accept': 'application/json' }
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(posts => {
            if (!Array.isArray(posts) || posts.length === 0) {
                postContainer.innerHTML = '<p>No posts found.</p>';
                return;
            }

            postContainer.innerHTML = posts.map(post => `
                <div class="post">
                    <h2>${escapeHtml(post.title)}</h2>
                    <p>${escapeHtml(post.content)}</p>
                    <button onclick="deletePost(${post.id})">Delete</button>
                </div>
            `).join('');
        })
        .catch(error => {
            showError(`Failed to load posts: ${error.message}`);
        });
}

function addPost() {
    const baseUrl = apiBaseUrlInput.value.trim();
    const title = postTitleInput.value.trim();
    const content = postContentInput.value.trim();

    if (!baseUrl) {
        showError("API URL is missing.");
        return;
    }
    if (!title || !content) {
        showError("Title and content are required.");
        return;
    }

    const postData = { title, content };

    fetch(`${baseUrl}/posts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(postData)
    })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw new Error(err.error || 'Unknown error'); });
            }
            return response.json();
        })
        .then(newPost => {
            console.log('Post added:', newPost);
            postTitleInput.value = '';
            postContentInput.value = '';
            loadPosts(); 
        })
        .catch(error => {
            showError(`Add failed: ${error.message}`);
        });
}

function deletePost(postId) {
    const baseUrl = apiBaseUrlInput.value.trim();
    if (!baseUrl) {
        showError("API URL is missing.");
        return;
    }

    if (!confirm("Delete this post?")) return;

    fetch(`${baseUrl}/posts/${postId}`, { method: 'DELETE' })
        .then(response => {
            if (!response.ok) {
                throw new Error('Delete failed');
            }
            loadPosts(); // Aktualisiere
        })
        .catch(error => {
            showError(`Delete failed: ${error.message}`);
        });
}

function showError(message) {
    postContainer.innerHTML = `<p class="error">${escapeHtml(message)}</p>`;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}