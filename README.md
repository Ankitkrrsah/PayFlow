# PayFlow - Payment Gateway API

PayFlow is a robust, layered-architecture API for processing payments, managing merchants, and handling webhooks.

## Architecture

The application is structured in layers to keep concerns separated and maintain thin components:

- **`routers/`**: HTTP layer only (parses requests, calls services, returns responses).
- **`services/`**: Core business logic and rules.
- **`repositories/`**: Raw SQL functions (psycopg2) with no business logic.
- **`db/`**: Connection pool, cursor helpers, and redis client.
- **`schemas/`**: Pydantic models for request and response validation.
- **`core/`**: Configuration and security (JWT, hashing).
- **`middleware/`**: Cross-cutting concerns like request logging and rate-limiting.

## Local Development with Docker

To start the application locally with PostgreSQL and Redis:

```bash
docker compose up --build
```
This will automatically run database migrations on startup and launch the API at `http://localhost:8000`.

## Required Environment Variables

A `.env` file should contain at least:
```env
PG_USER=postgres
PG_PASSWORD=postgres
PG_DB=payflow
PG_HOST=postgres
PG_PORT=5432
REDIS_HOST=redis
REDIS_PORT=6379
JWT_SECRET=supersecretkey
```

## Endpoints Overview

- **Auth**
  - `POST /auth/signup`
  - `POST /auth/login`
- **Merchants**
  - `POST /merchants`
  - `GET /merchants/me`
- **Payment Links**
  - `POST /payment-links`
  - `GET /payment-links`
- **Payments (Public)**
  - `POST /payment-links/{link_id}/pay`
- **Refunds**
  - `POST /transactions/{transaction_id}/refunds`
- **Webhooks**
  - `POST /webhooks`
  - `GET /webhooks/{id}/logs`

Example Request Body (`POST /payment-links`):
```json
{
  "amount": 150.00,
  "currency": "USD",
  "description": "Premium Subscription"
}
```

Example Response:
```json
{
  "id": "uuid-here",
  "amount": 150.00,
  "currency": "USD",
  "status": "active",
  "pay_url": "https://pay.example.com/uuid-here"
}
```
