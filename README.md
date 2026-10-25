# CodeRev

CodeRev is an internal app for scheduling focused, synchronous code-review sessions. A host publishes available slots, and teammates book a session without manual coordination or interruptions.

Built for the **TeamLift Product Engineer Internship Challenge**.

## Features

- Landing page, public slot timeline, and host dashboard (`/`, `/review-slots`, `/host`)
- Booking with name, email, topic, and optional context
- Available, taken, and started states; chronological listings and server-side pagination
- Host slot creation, booking details, and confirmed deletion; List, Columns, and Sections views
- Date/time pickers, duration presets, responsive modals, and light/dark themes
- Server-side validation, CSRF protection, PostgreSQL overlap and double-booking safeguards
- UTC-based scheduling, Europe/Skopje display timezone, and UUID public identifiers

## Tech Stack

- **Frontend:** React, JavaScript, Vite, React Router, Tailwind CSS v4, Lucide React, react-datepicker
- **Backend:** Python 3.14, Django, Django ORM, JSON API
- **Database:** PostgreSQL 17
- **Tooling:** ESLint

## Project Structure

```text
CodeRev/
├── frontend/              # React + Vite app
└── backend/
    ├── requirements.txt   # Python dependencies
    └── coderev/           # Django project (manage.py, .env.example)
```

## Local Development

The commands below use **Windows PowerShell**. On macOS/Linux, use the corresponding virtual-environment activation command and shell file-copy syntax.

### 1. Prerequisites and clone

Install **Git**, **Python 3.14** (including `pip` and `venv`), **Node.js and npm**, and **PostgreSQL 17**. Ensure they are accessible from your terminal and that PostgreSQL is running.

```powershell
git clone https://github.com/AndrejEftimov/CodeRev.git
cd CodeRev
```

### 2. Create the PostgreSQL database

Connect using `psql -U postgres` (or another PostgreSQL administrator) and run:

```sql
CREATE USER coderev_admin WITH PASSWORD 'choose-a-local-password';
CREATE DATABASE coderev OWNER coderev_admin;
```

The initial Django migration installs the PostgreSQL **`btree_gist`** extension to enforce non-overlapping slots. Ensure the database user can create extensions in the database, or ask a database administrator to enable `btree_gist` in `coderev` before migrating. On a typical local PostgreSQL 17 installation, the database owner can install this trusted extension.

### 3. Install and configure the backend

From the repository root:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
cd coderev
Copy-Item .env.example .env
```

Edit `backend/coderev/.env` to match your local database and set a **nonempty, unique `SECRET_KEY`**:

```dotenv
DB_NAME=coderev
DB_USER=coderev_admin
DB_PASSWORD=choose-a-local-password
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=replace-with-a-random-secret-key
```

You can generate a Django secret key after installing dependencies:

```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Paste the generated value into `.env`. **Never commit `.env` or real credentials.** The app uses UTC internally and presents dates/times in `Europe/Skopje`; do not change Django's `TIME_ZONE` to compensate for display time.

Apply migrations and start Django:

```powershell
python manage.py check
python manage.py migrate
python manage.py runserver
```

Keep this terminal running; Django listens on `http://127.0.0.1:8000/` by default.

### 4. Install and start the frontend

In a **second terminal**, from the repository root:

```powershell
cd frontend
npm install
npm run dev
```

Open the URL Vite prints (normally `http://localhost:5173/`). Browse `/`, `/review-slots`, and `/host`. Both servers must be running; Vite proxies `/api` requests to Django in local development. If the port or host changes, review `frontend/vite.config.js` and Django's CSRF trusted origins.

### 5. Optional development data

From `backend/coderev/` with the Python environment active:

```powershell
python manage.py seed_review_slots
```

The command creates realistic demo slots and bookings in a development database; it refuses to overwrite existing scheduling data. To preview or replace existing data:

```powershell
python manage.py seed_review_slots --dry-run --reset --confirm-reset
python manage.py seed_review_slots --reset --confirm-reset
```

**Warning:** A reset permanently deletes existing slots and associated bookings. Dry-run database changes are rolled back. Seeding is disabled when `DEBUG=False`.

### 6. Verify

In `backend/coderev/`:

```powershell
python manage.py check
python manage.py test scheduling
```

In `frontend/`:

```powershell
npm run lint
npm run build
```

Finally, check the landing page, public booking, and host create/details flows. If setup fails, confirm that PostgreSQL is running, `.env` matches the database, migrations completed, and both application servers are running.

## Verification Status

The most recently reported backend baseline is **107/107 scheduling tests passing**, covering validation, privacy, API contracts, pagination, CSRF, timezone/DST behavior, database constraints, and concurrency. Frontend lint/build and final browser checks should be rerun after the latest source changes.

## AI Usage

AI was used substantially for implementation, architecture discussion, debugging, code review, edge-case analysis, documentation, and explanations. The developer reviewed and approved engineering decisions and remains responsible for understanding and explaining the code.

## With More Time

- Authentication and actual host authorization
- History/past reviews and slot editing or rescheduling
- Booking cancellation and recurring availability
- Optional Google Calendar or AI-assisted enhancements

## Status

The end-to-end MVP is implemented, with final frontend verification and submission cleanup remaining. **`/host` is intended for a trusted-host MVP; it is not protected by authentication.** Run only in a trusted local environment.
