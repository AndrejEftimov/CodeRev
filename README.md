# CodeRev

CodeRev is a small internal scheduling app for focused, synchronous code-review sessions. A host developer publishes review availability, and teammates can reserve an available ReviewSlot instead of coordinating manually or interrupting ongoing work.

Built for the TeamLift Product Engineer Internship Challenge.

## Features

- Public chronological ReviewSlot timeline
- Book available review sessions with name, email, topic, and optional context
- Clear available, taken, and started slot states
- Host ReviewSlot creation and management under `/host`
- Host List, Columns, and Sections presentation modes
- Safe deletion flow for available and booked ReviewSlots
- PostgreSQL-backed overlap and double-booking protection
- Timezone-aware scheduling with UUID-based public resource identifiers

## Tech Stack

- **Frontend:** React, JavaScript, Vite
- **Backend:** Django, Python
- **Database:** PostgreSQL
- **ORM:** Django ORM
- **Linting:** ESLint

## Project Structure

```text
CodeRev/
├── frontend/   # React + Vite client
└── backend/    # Django + PostgreSQL API
```

## Local Setup

### Backend

1. Create `backend/coderev/.env` from the provided `.env.example`.
2. Configure the Django secret key and PostgreSQL connection values.
3. Ensure PostgreSQL is running and the configured database/user are available.
4. From `backend/coderev/`, apply migrations and start Django:

```bash
python manage.py migrate
python manage.py runserver
```

### Frontend

From `frontend/`:

```bash
npm install
npm run dev
```

## Verification

The backend is finalized for the MVP and currently passes:

```text
python manage.py check
python manage.py test scheduling
85/85 tests passing
```

The suite covers validation, lifecycle behavior, privacy, PostgreSQL constraints, API contracts, timezone handling, deletion, and concurrency-sensitive booking/overlap cases.

## AI Usage

AI was used substantially during development for implementation, architecture discussion, debugging, code review, edge-case analysis, documentation, and explanation. Product and engineering decisions were reviewed and approved by the developer, with the goal of keeping the resulting code understandable and explainable.

## With More Time

Possible next improvements include:

- Authentication and real host authorization
- Host history / past reviews
- Booking-developer cancellation
- ReviewSlot editing and rescheduling
- Recurring availability
- Optional Google Calendar or AI-assisted enhancements

## Status

The backend MVP is complete and verified. Responsive frontend implementation for desktop and mobile is the current development phase.
