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

The project is built with FastAPI, PostgreSQL and SQLAlchemy. It can be run locally or using Docker.

---

## Tech Stack

- Python 3.12
- FastAPI
- PostgreSQL 16
- SQLAlchemy
- Pydantic
- JWT authentication
- Docker & Docker Compose
- Pytest

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
```

---

## Main Features

### Authentication

- User signup and login
- Password validation
- JWT-based authentication
- Protected booking and payment endpoints
- Passwords are stored as hashes instead of plain text

### Diagnostic Centres & Tests

- View available diagnostic centres
- View available diagnostic tests
- View tests available at each centre
- Centre-specific test pricing

### Bookings

- Create diagnostic test bookings
- Validate centre/test availability
- Validate appointment time
- Calculate booking amount using server-side pricing
- View bookings
- Cancel bookings
- Users can only access their own bookings

### Payments

- Simulated successful payments
- Simulated failed payments
- Booking status is updated based on the payment result
- Mock provider payment IDs are generated for payments

### Payment Webhooks

- Webhook endpoint for payment status updates
- Webhook event ID tracking
- Idempotent webhook processing
- Repeated webhook events are not processed again

---

## API Endpoints & Example Requests

### Authentication

#### Signup

```http
POST /auth/signup
```

Example request:

```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "Password@123"
}
```

#### Login

```http
POST /auth/login
```

Example request:

```json
{
  "email": "john@example.com",
  "password": "Password@123"
}
```

The response contains a JWT access token.

---

### Diagnostic Centres

#### Get all centres

```http
GET /centres
```

#### Get a specific centre

```http
GET /centres/{centre_id}
```

#### Get available tests

```http
GET /tests
```

---

### Bookings

Booking endpoints require authentication.

#### Create booking

```http
POST /bookings
Authorization: Bearer <access_token>
```

Example request:

```json
{
  "centre_id": 1,
  "test_id": 1,
  "appointment_datetime": "2026-12-15T10:30:00"
}
```

The booking amount is calculated by the server using the selected centre/test combination.

Example response:

```json
{
  "id": 1,
  "centre_id": 1,
  "test_id": 1,
  "appointment_datetime": "2026-12-15T10:30:00",
  "amount": "500.00",
  "status": "PENDING"
}
```

#### Get current user's bookings

```http
GET /bookings
Authorization: Bearer <access_token>
```

#### Get a specific booking

```http
GET /bookings/{booking_id}
Authorization: Bearer <access_token>
```

#### Cancel a booking

```http
PATCH /bookings/{booking_id}/cancel
Authorization: Bearer <access_token>
```

---

### Payments

#### Create simulated payment

```http
POST /payments
Authorization: Bearer <access_token>
```

Successful payment:

```json
{
  "booking_id": 1,
  "simulate_success": true
}
```

Failed payment:

```json
{
  "booking_id": 1,
  "simulate_success": false
}
```

#### Payment webhook

```http
POST /payments/webhook
```

Example request:

```json
{
  "event_id": "evt_test_001",
  "provider_payment_id": "mock_12345",
  "status": "SUCCESS"
}
```

If the same `event_id` is received again, the API detects that the event has already been processed and does not process it a second time.

---

## Database / Schema Design

The application uses PostgreSQL with SQLAlchemy ORM.

The main entities are:

### User

Stores registered user information.

```text
User
- id
- name
- email
- password_hash
- created_at
```

### DiagnosticCentre

Stores diagnostic centre information.

```text
DiagnosticCentre
- id
- name
- location
- created_at
```

### DiagnosticTest

Stores diagnostic test information.

```text
DiagnosticTest
- id
- name
- description
- created_at
```

### CentreTest

Maps tests to diagnostic centres and stores the price for each centre/test combination.

```text
CentreTest
- id
- centre_id
- test_id
- price
```

The combination of `centre_id` and `test_id` is unique.

### Booking

Stores the user's diagnostic test booking.

```text
Booking
- id
- user_id
- centre_id
- test_id
- appointment_datetime
- amount
- status
- created_at
- updated_at
```

### Payment

Stores payment information associated with a booking.

```text
Payment
- id
- booking_id
- provider_payment_id
- event_id
- amount
- status
- created_at
- updated_at
```

A booking can have at most one payment.

---

## Running Locally

### 1. Create a virtual environment

Windows:

```powershell
python -m venv venv
```

Activate it:

```powershell
venv\Scripts\activate
```

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file using `.env.example` as a template.

Example:

```env
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/eve_healthcare
JWT_SECRET=change-this-secret
```

Make sure PostgreSQL is running before starting the API.

### 4. Start the API

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/health
```

---

## Running with Docker

The project includes a Dockerfile and Docker Compose configuration.

### Build the containers

```bash
docker compose build
```

### Start the application

```bash
docker compose up -d
```

### Check the containers

```bash
docker compose ps
```

The API will be available at:

```text
http://localhost:8000
```

Swagger:

```text
http://localhost:8000/docs
```

Health check:

```text
http://localhost:8000/health
```

To stop the containers:

```bash
docker compose down
```

---

## Seed Data

The project includes seed data for development and testing.

The seed data contains diagnostic tests such as:

- Complete Blood Count
- HbA1c
- Lipid Profile
- Thyroid Profile

It also includes example diagnostic centres in:

- New Delhi
- Noida

The centre/test combinations contain sample prices which are used when creating bookings.

---

## Payment Flow

The payment system is simulated because no real payment gateway is required for this assignment.

### Step 1 - Create a booking

```text
POST /bookings
```

A new booking starts with:

```text
PENDING
```

### Step 2 - Create a simulated payment

```text
POST /payments
```

Example:

```json
{
  "booking_id": 1,
  "simulate_success": true
}
```

The payment is then marked as either:

```text
SUCCESS
```

or:

```text
FAILED
```

The corresponding booking is updated accordingly.

### Step 3 - Payment webhook

The payment provider can send:

```text
POST /payments/webhook
```

Example:

```json
{
  "event_id": "evt_test_001",
  "provider_payment_id": "mock_12345",
  "status": "SUCCESS"
}
```

The webhook updates the payment and booking.

If the same event is sent again, the stored `event_id` is used to detect the duplicate event.

---

## Validation & Edge Cases

The API handles several invalid scenarios, including:

- Invalid login credentials
- Invalid booking IDs
- Unauthenticated booking requests
- Accessing another user's booking
- Invalid centre/test combinations
- Booking an appointment in the past
- Paying for a cancelled booking
- Paying for a booking that is no longer pending
- Invalid payment status
- Unknown payment/provider IDs
- Repeated webhook events

---

## Important Assumptions

- The payment provider is simulated because no real payment gateway was required.
- Payment success/failure is controlled using the `simulate_success` field.
- Each booking can have at most one payment.
- The booking amount is always taken from the server-side centre/test pricing.
- Users can only access their own bookings.
- Appointment times must be in the future when creating a booking.
- A payment can only be created for a booking with `PENDING` status.
- Webhook `event_id` values are treated as unique identifiers for webhook events.
- Repeated webhook events with the same event ID are treated as already processed.
- Seed data is provided for development and testing.
- PostgreSQL is used as the database for both local development and Docker.

---

## Testing

The project uses `pytest` with a separate PostgreSQL test database.

Run:

```bash
pytest -v
```

The test suite currently covers:

- User signup
- User login
- Successful booking
- Authentication requirement for bookings
- Invalid centre/test combinations
- Successful payment
- Failed payment
- Invalid payment booking
- Payment webhook processing
- Webhook idempotency

Current result:

```text
10 passed
```

The test database is separate from the development database so automated tests do not interfere with development data.

---

## Design Decisions

### Server-side pricing

The client does not provide the booking amount.

The API gets the price from the configured centre/test combination and stores that value in the booking.

This prevents the client from simply sending a different price.

### Ownership checks

Booking queries use the authenticated user's ID where required.

This prevents one user from accessing another user's booking.

### Webhook idempotency

The webhook stores the provider's `event_id`.

When another request arrives with the same event ID, the API detects that it has already been processed.

This prevents duplicate processing when a payment provider retries webhook delivery.

### Separate test database

Automated tests use a separate PostgreSQL database so test data does not interfere with the development database.

---

## Environment Variables

The application uses the following environment variables:

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `JWT_SECRET` | Secret used for signing JWT tokens |

The real `.env` file should never be committed to the repository.

Use `.env.example` as the template for the required environment variables.

---

## API Documentation

FastAPI automatically generates OpenAPI documentation.

Once the application is running:

```text
http://localhost:8000/docs
```

can be used to explore and test the API.

The OpenAPI schema is also available at:

```text
http://localhost:8000/openapi.json
```

---

## What I Would Improve With More Time

If this project were taken further beyond the assignment, I would consider:

- Adding Alembic migrations instead of relying on `create_all()` for schema creation.
- Adding more comprehensive test coverage for validation and authorization edge cases.
- Adding structured application logging and better error monitoring.
- Adding rate limiting to authentication and payment endpoints.
- Adding payment webhook signature verification for a real payment provider.
- Adding pagination for centre, test and booking listing endpoints.
- Adding refresh tokens and token revocation for a production authentication system.
- Adding proper production configuration and secret management.
- Adding CI checks for tests, formatting and linting.

---

## Notes

This project intentionally keeps the implementation relatively small and modular.

The focus was on the core backend requirements:

- Authentication
- Database modelling
- Diagnostic test bookings
- Payment simulation
- Payment webhooks
- Webhook idempotency
- Validation
- Authorization
- Automated testing
- Docker support
