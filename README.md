# Expense Tracker (Django REST + React)

![CI](https://github.com/Lukegbb/expense-tracker-fullstack/actions/workflows/ci.yml/badge.svg)

A full stack personal finance app to track **income and expenses**, with monthly reports and charts.
Back end in **Django REST Framework + PostgreSQL**, front end in **React (Vite) + Recharts**, JWT authentication, Docker and CI on GitHub Actions.

## Features

**API (Django REST Framework)**
- JWT authentication (access + refresh tokens) and user registration
- New users get a starter set of categories (Salary, Rent, Groceries, Transport, Leisure)
- Categories (income / expense, colour) and transactions – each user only sees their own data
- Filtering by category, type, date range and amount; search and ordering; pagination
- **Reports:** monthly summary (income, expenses, balance, spending by category) and 6-month trend
- Validation: positive amounts, ownership checks, categories in use can't be deleted
- OpenAPI docs with Swagger UI at `/api/docs/`
- 11 automated API tests, run in CI against PostgreSQL

**Front end (React)**
- Login / sign-up with automatic token refresh
- Dashboard with month picker and income/expense filter
- Summary cards, pie chart (spending by category) and bar chart (last 6 months)
- Add and delete transactions

## Tech stack

Python 3.12 · Django 5 · Django REST Framework · Simple JWT · django-filter · drf-spectacular · PostgreSQL · React 18 · Vite · Recharts · Docker · GitHub Actions

## Getting started

### 1. API + database (Docker)

```bash
git clone https://github.com/Lukegbb/expense-tracker-fullstack.git
cd expense-tracker-fullstack
docker compose up --build
```

API: http://localhost:8000 · Docs: http://localhost:8000/api/docs/

### 2. Front end

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 – requests to `/api` are proxied to the Django API.

### Running the API without Docker (SQLite)

```bash
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Tests

```bash
cd backend
python manage.py test
```

## API overview

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register/` | Create an account |
| POST | `/api/auth/token/` · `/api/auth/token/refresh/` | Get / refresh JWT |
| GET / POST | `/api/categories/` | List / create categories |
| PATCH / DELETE | `/api/categories/{id}/` | Update / delete a category |
| GET / POST | `/api/transactions/` | List (filters below) / create transactions |
| GET / PATCH / DELETE | `/api/transactions/{id}/` | Retrieve / update / delete |
| GET | `/api/reports/summary/?month=2026-10` | Monthly totals and spending by category |
| GET | `/api/reports/monthly/?months=6` | Income vs expenses per month |

Transaction filters: `category`, `kind` (income/expense), `date_from`, `date_to`, `min_amount`, `max_amount`, `search`, `ordering`.

## Project structure

```
├── backend/
│   ├── config/              # settings, URLs
│   └── expenses/
│       ├── models.py        # Category, Transaction
│       ├── serializers.py   # validation + default categories on sign-up
│       ├── filters.py       # django-filter FilterSet
│       ├── views.py         # ViewSets + report endpoints
│       └── tests/           # API tests
├── frontend/
│   └── src/
│       ├── api.js           # fetch wrapper with JWT refresh
│       └── components/      # Dashboard, charts, forms, list
├── docker-compose.yml
└── .github/workflows/ci.yml
```
