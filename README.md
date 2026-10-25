# Motorhaus — Car Dealership Inventory System

A full-stack inventory application built for the Incubyte TDD Kata. The app supports account registration/login, JWT-protected inventory access, vehicle search/filtering, purchases, and administrator inventory management.

## Stack
- **API:** Python, FastAPI, SQLAlchemy
- **Database:** SQLite for local development (persistent file database; not in-memory)
- **Authentication:** JWT bearer tokens and Argon2 password hashing
- **UI:** React, TypeScript, HTML5, CSS3, Tailwind CSS
- **Tests:** pytest, FastAPI TestClient

## Features
- Register and log in; passwords are hashed and never returned by the API.
- JWT-protected vehicle listing and search.
- Search by make, model, category, minimum price and maximum price.
- Admin-only create, update, delete, and restock operations.
- Authenticated purchase decrements stock and refuses purchases when stock is zero.
- Responsive inventory dashboard with search controls, stock states and admin create form.

## Local setup

### 1. Backend
Requirements: Python 3.11+.

```bash
cd backend
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell:
# .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

The API is available at http://localhost:8000 and interactive docs at http://localhost:8000/docs. SQLite creates `backend/dealership.db` on first startup.

**Admin account for local evaluation:** public registration intentionally creates customer accounts only. To create an admin, register a user, then use a local database session or a one-off trusted script to set that user's `is_admin=True`. Never expose a public admin-registration endpoint. Example from `backend/`:

```bash
python - <<'PY'
from app.database import SessionLocal
from app.models import User
with SessionLocal() as db:
    user = db.query(User).filter_by(email="you@example.com").one()
    user.is_admin = True
    db.commit()
print("Admin role granted locally.")
PY
```

### 2. Frontend
Requirements: Node.js 20+.

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Open http://localhost:5173. The frontend expects the API at `http://localhost:8000` by default; set `VITE_API_URL` if needed.

## API overview

| Method | Endpoint | Access | Purpose |
|---|---|---|---|
| POST | `/api/auth/register` | Public | Register customer |
| POST | `/api/auth/login` | Public | Login and issue JWT |
| GET | `/api/auth/me` | Authenticated | Current account |
| GET | `/api/vehicles` | Authenticated | List inventory |
| GET | `/api/vehicles/search` | Authenticated | Filter inventory |
| POST | `/api/vehicles` | Admin | Add vehicle |
| PUT | `/api/vehicles/{id}` | Admin | Update vehicle |
| DELETE | `/api/vehicles/{id}` | Admin | Delete vehicle |
| POST | `/api/vehicles/{id}/purchase` | Authenticated | Purchase one unit |
| POST | `/api/vehicles/{id}/restock` | Admin | Add stock quantity |

A vehicle contains `id`, `make`, `model`, `category`, `price`, and `quantity`. Search parameters are `make`, `model`, `category`, `min_price`, and `max_price`.

## Run tests

From `backend/` with the virtual environment active:

```bash
pytest -v
```

Tests use a separate temporary SQLite database, so they do not modify the development inventory database. The suite covers registration/login, duplicate registration, input validation, authentication, role-based authorization, searching, purchase stock changes, restocking, update and deletion.

### Test report
The test report is intentionally not pre-filled with a claimed pass count. Run `pytest -v` and paste the actual output into `TEST_REPORT.md`, including date, Python version, command, passed/failed counts, and any follow-up fixes.

## TDD and Git workflow

Use small, real red-green-refactor commits. For each behavior:
1. Add a failing test and commit it (`test: specify ...`).
2. Run it and record the failure.
3. Implement the smallest change and commit it (`feat: implement ...`).
4. Refactor with tests still passing (`refactor: ...`).

Do not manufacture historical commits or claim a test failed before you ran it. The supplied project is a starter implementation; establish your own Git history from the actual work you perform.

For commits that used AI, add a co-author trailer after two blank lines. The assessment gives `AI Tool Name <AI@users.noreply.github.com>` as an example; use a truthful tool identity and a valid configured author identity where your platform supports it.

Example:

```bash
git add backend/tests/test_auth.py
git commit -m "test: specify registration behavior" \
  -m "Co-authored-by: ChatGPT <AI@users.noreply.github.com>"
```

## My AI Usage

I used ChatGPT to help interpret the kata requirements, propose an initial project structure, draft API and UI scaffolding, and generate an initial set of test cases and documentation. I need to review the code, run the tests, verify behavior, and make the final design and implementation decisions myself. AI-generated code can contain bugs; tests and manual review are required before submission. During development, I will use AI for targeted debugging and review, and record the relevant prompts in `PROMPTS.md`.

## Screenshots

Add genuine screenshots after running the app locally. Suggested files:
- `docs/screenshots/login.png`
- `docs/screenshots/inventory-dashboard.png`
- `docs/screenshots/admin-add-vehicle.png`

Do not use mock screenshots as evidence of a running application.

## Known limitations / next improvements

- Add a production migration workflow (Alembic), structured logging, rate limiting, and deployment secrets management.
- Add automated frontend tests (Vitest/React Testing Library) and end-to-end browser tests.
- Add optimistic concurrency / a database-level conditional stock decrement for robust simultaneous purchase handling.
- Add admin edit/delete/restock controls to the UI; the corresponding protected API endpoints are implemented.
- Configure production CORS origins and replace the development JWT secret before deployment.
- Add a deployment pipeline and CI workflow once the target host is chosen.

## Security notes
The included JWT secret is for local development only. Configure a strong random `JWT_SECRET_KEY` in every non-local environment. Do not commit real secrets or customer data.
