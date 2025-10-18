# quectoCMS

quectoCMS is a minimalist, fileless micro content management system written in Python 3, Flask, and SQLite3.  
It is designed to stay small and transparent — a CMS you can fully understand at first glance — while still managing pages, comments, and basic multilingual content.

---

## Features

- Simple micro-architecture: single SQLite database, no heavy frameworks.
- Page blocks stored in the database with ordering (`position`) and optional locale.
- Comments module for visitor interaction.
- Key–value parameters table for global settings (e.g., `title`, `version`).
- Automatic redirect to initial setup when no site title is defined.
- Dynamic menu generated from existing pages.
- Plain HTML forms only, no JavaScript required. No JS at all, tbh.
- Clean three-column layout using simple CSS.

---

## Project structure

qbrack-web/
  ├─ app.py                  — Flask application entry point
  ├─ controllers/
  │   └─ app_controller.py   — Route registration (delegates to services)
  ├─ services/
  │   ├─ page_service.py     — Page rendering, setup flow, block creation
  │   ├─ comment_service.py  — Comment handling
  │   └─ home_service.py     — Global params (title, version, footer data)
  ├─ models/
  │   ├─ page_model.py       — CRUD for table "pages"
  │   ├─ comment_model.py    — CRUD for table "comments"
  │   └─ home_model.py       — CRUD for table "params"
  ├─ templates/
  │   ├─ page.html           — Main layout
  │   ├─ add_page.html       — Setup and block creation form
  │   ├─ comments.html       — Comments section
  │   └─ footer.html         — Common footer
  └─ static/
      └─ style.css           — Basic layout and styling

---

## Installation

1) Create and activate a virtual environment, then install Flask:

    python3 -m venv myenv
    source myenv/bin/activate
    pip install flask

2) Start the application:

    python app.py

3) Open http://localhost:5000 in your browser.

---

## Database schema (SQLite)

Table: pages  
- id: INTEGER PRIMARY KEY AUTOINCREMENT  
- page: TEXT — logical page name  
- page_order: INTEGER — order of pages in menu (per page)  
- locale: TEXT — language code (e.g., pl, en)  
- content: TEXT — HTML/Markdown block  
- position: INTEGER — block order within a page (ascending)

Table: comments  
- id: INTEGER PRIMARY KEY AUTOINCREMENT  
- ip: TEXT — visitor IP address  
- creation_date: TEXT — timestamp (local)  
- user: TEXT — optional nickname or email  
- comment: TEXT — comment content

Table: params  
- id: INTEGER PRIMARY KEY AUTOINCREMENT  
- name: TEXT UNIQUE — parameter key (e.g., "title")  
- value: TEXT — stored value

---

## Usage flow

1) First run initializes the SQLite database.  
2) If there is no site title in `params` (`name = "title"`), the app redirects to `/add_page`.  
3) Enter the site title and submit.  
4) Then add content blocks by providing:
   - page name,
   - block position (integer),
   - block content (HTML allowed).
5) Visit `/` to render the homepage using stored blocks.  
6) Visitors can add comments in the right-side section.

---

## Data persistence

All content and parameters are stored in a single file `qcms.db` located in the working directory.  
SQLite ensures transactional integrity and requires no additional setup.

---

## Customization

- Styling: edit `static/style.css`.  
- Templates: modify Jinja2 files under `templates/`.  
- Layout: the default view is a left menu, center content, and right comments column.

---

## Minimal API endpoints

- GET `/` — render homepage.  
- GET `/page/<page>` — render a given page.  
- GET `/add_page` — show setup or block creation form (depending on whether a title exists).  
- POST `/add_page` — save title or create a new content block.  
- POST `/add_comment` — submit a comment.  
- GET `/get_comments` — return comments as JSON.

---

## Philosophy

"If you can't explain your CMS in 30 seconds, it's too complicated."

quectoCMS demonstrates that a dynamic website does not need heavy frameworks or admin panels — only a small database, a few templates, and a clear structure.

---

## License

MIT License © 2025 mabalew
