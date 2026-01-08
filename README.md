# GreenPlate — Backend (FastAPI)

A lightweight FastAPI backend for managing college food stalls, staff, and menus.
It uses Firebase Authentication + Firestore and supports AI-assisted menu extraction (Google Gemini).

Purpose
- Manage stalls, staff and menus for colleges.
- Staff can upload and edit menus for their assigned stall only.
- Managers can add/remove staff for their stall.
- Optional image-based menu extraction returns JSON of item names and prices.

Tech stack
- Python 3.13, FastAPI, Uvicorn
- Firebase Authentication (pyrebase + firebase_admin) and Firestore
- Google Generative AI (Gemini) for menu image parsing (optional)
- Docker (Dockerfile + compose.yaml) provided

Quick start (local)
1. Create and activate a virtual environment:

```bash
python -m venv .venv && source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Provide Firebase service account and env vars.
   - Recommended: set FIREBASE_SERVICE_ACCOUNT to the full JSON content of the service account file.
   - Alternatively mount a local file into the container (see Docker section) and set FIREBASE_SERVICE_ACCOUNT to its path.

4. Run the app:

```bash
python main.py
# or
uvicorn app.app:app --reload --host 0.0.0.0 --port 8000
```

Docker
- Build image and run (from repo root):

```bash
docker build -t greenplate-backend .
docker run --rm -p 8000:8000 --env-file .env -v $(pwd)/secrets:/app/secrets:ro greenplate-backend
```

- With Docker Compose (recommended for local development):

```bash
docker compose up --build
docker compose down
```

Environment variables (important)
- FIREBASE_SERVICE_ACCOUNT: JSON string or path to the service account key file used by firebase_admin.
- FIREBASE_API_KEY, FIREBASE_AUTH_DOMAIN, FIREBASE_DATABASE_URL, FIREBASE_PROJECT_ID, FIREBASE_STORAGE_BUCKET, FIREBASE_MESSAGING_SENDER_ID, FIREBASE_APP_ID, FIREBASE_MEASUREMENT_ID — used by pyrebase client (see `app/config.py`).
- GEMINI_API_KEY — required only if you use image scanning (`/staff/menu/scan-image`).

Security / Auth headers
- All protected endpoints require a Firebase ID token (not the UID) in the Authorization header:

```
Authorization: Bearer {idToken}
```

- You can obtain an ID token via the `/login/users` endpoint (or use `get_token.py` for tests).
- If you receive {"message": "Authorization header required"} or 401, ensure the header key is exactly `Authorization` and the value starts with `Bearer ` followed by the idToken.

Main endpoints (summary)
- GET /health — health check

Auth / User
- POST /signup/users — Sign up a student (payload: email, password, confirm_password)
- POST /login/users — Sign in (returns idToken)
- GET /user/menu — List available menus for the student’s college (requires Bearer idToken)

Staff / Manager
- POST /auth/verify-staff — Verify token and initialize manager account (if email matches a stall email) — returns role, stall_id, college_id
- POST /staff/menu — Upload menu JSON for a stall (staff only; stall_id must match the authenticated staff's stall)
- GET /staff/menu — Get menu for the authenticated staff's stall
- POST /staff/menu/scan-image — Upload an image; AI returns JSON array of items (name, price, description)
- PATCH /staff/menu/{item_id} — Update a menu item (staff/manager for that stall)
- DELETE /staff/menu/{item_id} — Delete a menu item (staff/manager for that stall)

Manager-only
- POST /staff/add-member — Add a staff member (manager only)
- GET /staff/list — List staff members for the manager's stall
- DELETE /staff/{staff_uid} — Remove a staff (manager only)
- PUT /staff/{staff_uid}/email — Update staff email (manager only)

Key behavior / rules
- Stall-level authorization: staff/manager tokens are checked against `staffs` collection. A staff can only modify menu items for their assigned `stall_id`.
- Manager initialization: when a verified token's email matches a stall's email and no staff document exists, the endpoint will create a manager record automatically.
- Menu upload expects JSON matching the Pydantic schema `MenuSchema`:
  - stall_id: string (must equal the staff's stall)
  - items: list of {name: str, price: float (>0), description?: str, is_available?: bool}
- Image scan returns a list of extracted items; results should be reviewed before saving (the AI may be imperfect).

Testing tokens
- Use `get_token.py` (dev helper) to exchange an existing Firebase user email/password for an idToken.
- Or call POST /login/users to get idToken on successful sign-in.

Troubleshooting
- Authorization header required: Header missing or malformed. Ensure `Authorization: Bearer <idToken>`.
- 401 Unauthorized: token invalid or expired — re-login to get a fresh idToken.
- 403 Forbidden: trying to modify a stall you don’t belong to or role mismatch.
- 413 Request Entity Too Large: uploaded image exceeds 5MB limit.

Useful paths
- API docs (Swagger): http://localhost:8000/docs

Contributing
- Keep secrets out of version control: do not commit `.env` or `secrets/serviceAccountKey.json`.
- See `app/firebase_init.py` to understand service account loading.

License
- See LICENSE in repo root.

Last updated: 2026-01-07
