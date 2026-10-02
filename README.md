# EVE Healthcare API

A backend API for diagnostic test booking and simulated payments, built as part of the EVE Healthcare backend assignment.

The API allows users to:

- Create an account and log in using JWT authentication
- View diagnostic centres and available tests
- Check test prices at different centres
- Create and manage diagnostic test bookings
- Make simulated payments
- Handle payment webhooks
- Prevent duplicate webhook processing
- Access only their own bookings

The project is built with FastAPI, PostgreSQL and SQLAlchemy, and can be run locally or with Docker.

---

## Tech Stack

- **Python 3.12**
- **FastAPI**
- **PostgreSQL 16**
- **SQLAlchemy**
- **Pydantic**
- **JWT authentication**
- **Docker & Docker Compose**
- **Pytest**

---

## Project Structure

```text
eve-healthcare-backend/
│
├── app/
│   ├── auth.py
│   ├── bookings.py
│   ├── centres.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── payments.py
│   ├── schemas.py
│   └── seed.py
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_bookings.py
│   └── test_payments.py
│
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md