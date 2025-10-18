# quectoCMS

quectoCMS is a minimalist CMS built with Python 3, Flask, and SQLite.  
It focuses on simplicity and small size — everything is stored in one SQLite database and rendered through plain HTML templates.

---

## Features

- Minimal architecture: models, services, and Jinja2 templates.  
- Pages built from ordered blocks (`pages` table).  
- Comment system with timestamps.  
- Global parameters (`params` table).  
- Media uploads with SHA-256 deduplication and date-based folders.  
- Works entirely without JavaScript.  
- Clean layout with left menu, center content, and right comment panel.

---

## Project structure

```
/
├─ app.py                  — Flask application entry point
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

1. On first run, the SQLite database is initialized automatically.  
2. If no `title` exists in `params`, the user is redirected to `/add_page`.  
3. The title form appears first; once saved, block creation fields appear:  
   - page name  
   - block position (integer)  
   - block content (HTML allowed)  
4. `/` or `/page/<page>` renders all blocks ordered by `position`.  
5. The right column lists comments and allows new ones.  
6. The footer shows data from `params` (version, creation, modification dates).  
7. The same page includes an upload form for images.

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

---

## License

MIT License © 2025 Mariusz Balewski / TYO Labs
