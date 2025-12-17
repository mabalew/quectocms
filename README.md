![QCMS Logo](static/images/logo.svg)
# quectoCMS

quectoCMS is a minimalist CMS built with Python 3, Flask, and SQLite.  
It focuses on simplicity and small size — everything is stored in one SQLite database and rendered through plain HTML templates.

---

## Features

- Minimal architecture: models, services, and Jinja2 templates.  
- Pages composed of ordered content blocks stored in SQLite  (`pages` table).  
- Comment system with timestamps.  
- Global parameters (`params` table).  
- Media uploads with SHA-256 deduplication and date-based folders.  
- Works entirely without JavaScript.  
- Clean, responsive CSS-based layout with left menu, center content, and right comment panel.
- No JavaScript dependencies, no front-end frameworks
- HTTP Basic Auth for admin routes (no cookies; nothing stored on client side!)
- Admin interface for:
  - Adding new pages  
  - Editing and deleting existing pages  
  - Adding, editing, and deleting individual content blocks  

---

## Project structure

```
/
├─ app.py                  — Flask application entry point
├─ auth.py                 — Authentication module
├─ controllers/
│   └─ app_controller.py   — Route registration (delegates to services)
├─ services/
│   ├─ page_service.py     — Page rendering, setup flow, block creation, media upload
│   ├─ comment_service.py  — Comment handling
│   ├─ home_service.py     — Global params (title, version, footer data)
│   └─ media_service.py    — Optional separation for upload logic
├─ models/
│   ├─ page_model.py       — CRUD for table "pages"
│   ├─ comment_model.py    — CRUD for table "comments"
│   ├─ home_model.py       — CRUD for table "params"
│   └─ media_model.py      — CRUD for table "media" (SHA-256, path, mime)
├─ templates/
│   ├─ page.html           — Main layout
│   ├─ add_page.html       — Setup and block creation form + media upload
│   ├─ admin.html          — Admin home (page list and actions)
│   ├─ edit_page.html      — Block editing interface (per page)
│   ├─ comments.html       — Comments section
│   └─ footer.html         — Common footer
└─ static/
    ├─ style.css           — Basic layout and styling
    └─ uploads/            — Date-based media storage (YYYY/MM/DD/…)
```

---

## Database schema (SQLite)

### Table: `pages`

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PRIMARY KEY AUTOINCREMENT | unique ID |
| `page` | TEXT | logical page name |
| `page_order` | INTEGER | order of pages in menu |
| `locale` | TEXT | language code (e.g., `pl`, `en`) |
| `content` | TEXT | HTML or Markdown block |
| `position` | INTEGER | block order within page |

### Table: `comments`

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PRIMARY KEY AUTOINCREMENT | unique ID |
| `ip` | TEXT | visitor IP address |
| `creation_date` | TEXT | timestamp (local) |
| `user` | TEXT | optional nickname or email |
| `comment` | TEXT | comment content |

### Table: `params`

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PRIMARY KEY AUTOINCREMENT | unique ID |
| `name` | TEXT UNIQUE | parameter key (e.g., `title`) |
| `value` | TEXT | stored value |

### Table: `media`

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER PRIMARY KEY AUTOINCREMENT | unique ID |
| `sha256` | TEXT UNIQUE | SHA-256 of file content |
| `rel_path` | TEXT UNIQUE | relative path under `static/` |
| `mime` | TEXT | MIME type (e.g., `image/jpeg`) |
| `uploaded_at` | TEXT | timestamp (local) |

---

## Usage flow

1. **First run:**
   The SQLite database is initialized automatically
   If the database does not contain a `title` in `params`, the app redirects to `/add_page`.  
   The title form appears first; once saved, block creation fields appear:  
   - page name  
   - block position (integer)  
   - block content (HTML allowed)
   
2. **Normal usage:**  
   - Visit `/` to see public pages.  
   - Add or manage content through `/admin` (requires Basic Auth).

3. **Adding content:**  
   - Use `/add_page` or link on the `/admin` page to create new pages or add blocks to existing ones.  
   - Uploaded files are stored under `static/uploads/YYYY/MM/DD/` with SHA-256 deduplication.  
   - If a file with the same hash already exists, it’s reused automatically.
   - The right column lists comments and allows new ones.  

4. **Editing content:**  
   - Go to `/edit/<page>` or use link on the `admin` page to modify or delete individual blocks.  
   - Each block can have its `content` and `position` changed independently.  
   - New blocks can be added directly from the editor view.

5. **Deleting:**  
   - Pages or individual blocks can be removed from `/admin` or `/edit/<page>`.  
   - All deletions are immediate and permanent (no recycle bin).
---

## Media uploads

- The upload form (in `add_page.html`) lets the user select a file.  
- Server workflow:
  1. Compute SHA-256 of the uploaded file.  
  2. Check the `media` table — if the hash exists, return the existing path.  
  3. Otherwise, save the file to `static/uploads/YYYY/MM/DD/<sha-prefix>_<filename>`  
     and insert a record in `media`.  
- The app displays a copyable image path for easy embedding:
  ```
  <img src="/static/uploads/2025/10/18/abcd1234_image.jpg" alt="" />
  ```
- Recent uploads (today and yesterday) are listed for quick reuse.

---
## Admin protection (HTTP Basic Auth, no cookies)

HTTP Basic Auth provides access control without any cookies or client-side storage.  
Credentials are sent in the \`Authorization\` header and kept only in browser memory during the session.  
No data is written to the user’s computer. Always use **HTTPS**.


1. Install Werkzeug if needed:  
   ```bash
   pip install werkzeug
   ```

2. Generate a password hash in Python:  
   ```bash
   from werkzeug.security import generate_password_hash
   print(generate_password_hash("YourStrongPassword"))
   ```

3. Set environment variables (include the entire hash generated in pt. 2):  
   ```bash
   export ADMIN_USER='admin'
   export ADMIN_PASS_HASH='scrypt:32768:8:1$uy3R3TRf$...full_hash_here...'
   ```
   
Notes:
- Works entirely without cookies or local storage.  
- With HTTPS, credentials are protected in transit.  
- To change the password, regenerate the hash and restart the app. 


## Installation

```
python3 -m venv myenv
source myenv/bin/activate
pip install flask
```

---

## Running the app

```
python app.py
```

Visit `http://localhost:5000` in a browser.

---

## Endpoints

| Method | Route | Description |
|--------|--------|-------------|
| GET | `/` | Render homepage |
| GET | `/page/<page>` | Render specific page |
| GET / POST | `/add_page` | Setup and content block creation |
| POST | `/add_comment` | Add new comment |
| GET | `/get_comments` | Return comments as JSON |
| POST | `/upload_media` | Upload image (SHA-256, deduplicate, return path) |

---

## Notes

- `page_order` sorts pages in the menu; `position` sorts blocks within a page.  
- Media files are never stored as BLOBs, only as file paths in `static/uploads`.  
- The upload directory is date-based to prevent large flat folders.  
- Deduplication is deterministic via SHA-256; re-uploading the same file reuses the same path.  
- No JavaScript is required for any functionality.
- No data stored on client side.

---

## License

MIT License © 2025 mabalew
