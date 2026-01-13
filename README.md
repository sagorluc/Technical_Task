# MarketLink Backend

MarketLink is a Django-based backend system for a marketplace connecting customers, vendors, and admin. It supports service management, orders, payments via Stripe, and background processing using Celery and Redis.
---

### Table of Contents

1. [Requirements](#requirements)
2. [Project Setup](#project-setup)
    - Manual Setup
    - Docker Setup
    - Docker Compose Setup

3. [Running the Project](#running-the-project)
4. [API Endpoints](#api-endpoints)
    - Accounts
    - Vendors
    - Services
    - Orders
    - Payments

5. [Celery Tasks](#celery-tasks)
6. [Stripe Integration](#stripe-integration)
7. [Ngrok](#ngrok)

### Requirements
- Python 3.12
- PostgreSQL 15+
- Redis
- Stripe account
- Docker & Docker Compose (optional for containerized setup)

---

### Project Setup
1. ***Manual Setup***
    1. Clone the repository:
    ```bash
        git clone https://github.com/sagorluc/Technical_Task.git
        cd SoftVence
    ```
    2. Create virtual environment:
    ```bash
        # Linux
        python -m venv venv
        source venv/bin/activate
    ```
    3. Install dependencies:
    ```bash
        pip install -r requirements.txt
    ```
    4. Set up `.env` file:
    ```bash
        DEBUG=1
        SECRET_KEY='your-secret-key'
        SERVER_TYPE=localhost

        # Database
        DB_NAME=
        DB_USER=
        DB_PASSWORD=
        DB_HOST=
        DB_PORT=

        # Redis
        REDIS_URL=

        # Stripe
        STRIPE_SECRET_KEY=sk_test_...
        STRIPE_PUBLISHABLE_KEY=pk_test_...
        STRIPE_WEBHOOK_SECRET=whsec_...

        # CSRF
        CSRF_TRUSTED_ORIGINS=https://<ngrok-url>

        DOMAIN=
    ```
    5. Apply migrations:
    ```bash
        python3 manage.py makemigrations
        python3 manage.py migrate
    ```
    6. Create a superuser (optional):
    ```bash
        python3 manage.py createsuperuser
    ```
    7. Run development server:
    ```bash
        python3 manage.py runserver
    ```
    8. Run Celery worker server (in separate terminals):
    ```bash
        celery -A marketlink worker -l info
    ```

2. ***Docker Setup***
    1. Build Docker image:
    ```bash
        docker build -t marketlink:latest .
    ```
    2. Run Docker container:
    ```bash
        docker run -p 8000:8000 --env-file .env marketlink:latest
    ```
    3. Access project at: http://localhost:8000


3. ***Docker Compose Setup***
    1. Start services:
    ```bash
        docker-compose up --build
    ```
    2. Services included:
        - **web:** Django application
        - **celery:** Celery worker
        - **redis:** Redis broker
    3. Access Django: http://localhost:8000
    4. Access Ngrok web interface (if configured): http://localhost:4040

---

### Running the Project
1. **Django server:**
```bash
    python3 manage.py runserver
```
2. **Celery worker:**
```bash
    celery -A marketlink worker -l info
```
3. **Swagger UI:** http://localhost:8000/api/schema/docs/
Update your base domain to point to the ngrok URL:
```bash
https://<ngrok-id>.ngrok-free.dev/api/schema/docs/
```
4. **Stripe webhook testing (via ngrok):**
```bash
    # open linux terminal then type (ngrok required in your system)
    ngrok http http://127.0.0.1:8000
```
Update your Stripe webhook to point to the ngrok URL:
```bash
https://<ngrok-id>.ngrok-free.dev/payments/stripe/webhook/
```

---

### API Endpoints

1. Accounts <br>

| Endpoint                      | Method | Description                     |
| ----------------------------- | ------ | ------------------------------- |
| `/accounts/admin/sign-up/`    | POST   | Create admin user               |
| `/accounts/vendor/sign-up/`   | POST   | Create vendor user              |
| `/accounts/customer/sign-up/` | POST   | Create customer user            |
| `/accounts/log-in/`           | POST   | Authenticate and get JWT tokens |

2. Vendors <br>

| Endpoint         | Method     | Description                                                                        | Permissions                                                   |
| ---------------- | ---------- | ---------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| `/vendors/`      | **GET**    | List vendor profiles. Admins see all vendors, vendors see their own profile only.  | Admin, Vendor (Authenticated)                                 |
| `/vendors/<id>/` | **GET**    | Retrieve a specific vendor business profile by ID.                                 | Admin, Vendor (Authenticated)                                 |
| `/vendors/`      | **POST**   | Create a new vendor business profile. Only vendors can create.                     | Vendor only                                                   |
| `/vendors/<id>/` | **PUT**    | Update an existing vendor profile fully.                                           | Vendor (own profile), Admin                                   |
| `/vendors/<id>/` | **PATCH**  | Partially update an existing vendor profile (e.g., only address or business name). | Vendor (own profile), Admin                                   |
| `/vendors/<id>/` | **DELETE** | Delete a vendor profile.                                                           | Admin (typically), optionally Vendor (own profile if allowed) |



3. Services <br>

**Vendor & Admin CRUD**

| Endpoint          | Method     | Description                                                            | Permissions                 |
| ----------------- | ---------- | ---------------------------------------------------------------------- | --------------------------- |
| `services/services/`      | **GET**    | List services. Admin sees all services, Vendor sees own services only. | Admin, Vendor               |
| `services/services/<id>/` | **GET**    | Retrieve a specific service by ID.                                     | Admin, Vendor (own service) |
| `services/services/`      | **POST**   | Create a new service. Only vendors can create.                         | Vendor only                 |
| `services/services/<id>/` | **PUT**    | Update an existing service fully.                                      | Vendor (own service), Admin |
| `services/services/<id>/` | **PATCH**  | Partially update an existing service.                                  | Vendor (own service), Admin |
| `services/services/<id>/` | **DELETE** | Delete a service.                                                      | Vendor (own service), Admin |

**Service Variants (Vendor & Admin CRUD)**

| Endpoint                 | Method     | Description                                                                          | Permissions                 |
| ------------------------ | ---------- | ------------------------------------------------------------------------------------ | --------------------------- |
| `services/service-variant/`      | **GET**    | List all service variants. Admin sees all, Vendor sees own variants only.            | Admin, Vendor               |
| `services/service-variant/<id>/` | **GET**    | Retrieve a specific service variant by ID.                                           | Admin, Vendor (own variant) |
| `services/service-variant/`      | **POST**   | Create a new service variant. Vendor can only create variants for their own service. | Vendor only                 |
| `services/service-variant/<id>/` | **PUT**    | Update an existing service variant fully.                                            | Vendor (own variant), Admin |
| `services/service-variant/<id>/` | **PATCH**  | Partially update an existing service variant.                                        | Vendor (own variant), Admin |
| `services/service-variant/<id>/` | **DELETE** | Delete a service variant.                                                            | Vendor (own variant), Admin |

**Customer-facing endpoints**

| Endpoint                   | Method  | Description                                                                 | Permissions   |
| -------------------------- | ------- | --------------------------------------------------------------------------- | ------------- |
| `/services/customer/list/` | **GET** | List all approved services. Only customers can access.                      | Customer only |
| `/services/customer/<id>/` | **GET** | Retrieve details of a specific approved service. Only customers can access. | Customer only |

**Admin Approve/Unapprove Service**
| Endpoint                        | Method    | Description                                                         | Permissions |
| ------------------------------- | --------- | ------------------------------------------------------------------- | ----------- |
| `/services/admin/<id>/approve/` | **PATCH** | Approve or unapprove a service. Only admin can perform this action. | Admin only  |


**Notes:**
- `ServiceViewSet` and `ServiceVariantViewSet` handle full CRUD for vendors and admin.
- `ServiceCustomerListView` and `ServiceCustomerRetrieveView` expose read-only approved services for customers.
- `ServiceAdminApproveAPIView` allows admin to ***approve/unapprove*** services via a PATCH request.

- Serializers:
    - `ServiceCreateUpdateSerializer` → for create/update by vendor/admin
    - `ServiceRetriveListSerializer` → for list/retrieve (vendors and customers)
    - `ServiceVariantCreateUpdateSerializer` → for create/update variants
    - `ServiceVariantResponseSerializer` → for list/retrieve variants



4. Orders <br>

| Endpoint            | Method   | Description                                                                                                           | Permissions                 | Notes                                                                                                                                           |
| ------------------- | -------- | --------------------------------------------------------------------------------------------------------------------- | --------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `/orders/create/` | **POST** | Create a repair order for a service variant provided by a vendor. Handles payment creation using **Stripe Checkout**. | Authenticated Customer only | Request body: `{ "vendor_id": int, "variant_id": int }`. Returns `order_id` and `checkout_url` for Stripe payment. Minimum order amount is ৳60. |

**Notes:**
1. Customer selects a service variant from a vendor.
2. POST request to /payments/create/ creates a RepairOrder in pending status.
3. Stripe Checkout Session is created with metadata for order_id.
4. Payment record is stored in the Payment model with pending status.
5. Customer is redirected to the Stripe checkout URL (checkout_url).
6. After successful payment, a Stripe webhook updates the order status to paid and triggers Celery 
    - tasks:
        - send_invoice → generates invoice
        - start_processing → marks order as processing then completed

**Request Example**
```json
POST /payments/create/
{
"vendor_id": 1,
"variant_id": 2
}
```
**Response Example**
```json
{
"success": true,
"data": {
    "order_id": "7ab8fac1-0905-424f-ad2a-38a534a3d530",
    "checkout_url": "https://checkout.stripe.com/pay/cs_test_..."
}
}
```

5. Payments <br>

    1. **Create Repair Order**

    Already described in the previous request.
    Endpoint: /payments/create/ (POST) – Customers create a repair order and receive a Stripe Checkout URL.

    2. **Stripe Webhook**  
    
    | Endpoint                    | Method   | Description                                                                                                                                         | Permissions                         | Notes                                                                                |
    | --------------------------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------- | ------------------------------------------------------------------------------------ |
    | `/payments/stripe/webhook/` | **POST** | Handles Stripe payment events (both mobile **PaymentIntent** and web **Checkout Session**). Updates the order status and triggers background tasks. | AllowAny (Stripe sends the request) | Used for payment confirmation. Supports idempotency (prevents duplicate processing). |

    **Workflow:**

    1. Stripe sends a webhook event to /payments/stripe/webhook/.
    2. Webhook validates the signature using STRIPE_WEBHOOK_SECRET.
    3. Checks if the event was already processed (PaymentEvent table).
    4. Handles two types of events:
        - Mobile / PaymentIntent: payment_intent.succeeded
        - Web / Checkout Session: checkout.session.completed
    5. Updates the corresponding RepairOrder status to paid.
    6. Triggers Celery tasks:
        - send_invoice(order_id) → Generates invoice for the order
        - start_processing(order_id) → Marks order as processing, waits 30 seconds, then marks as completed.
    7. Logs important actions using Django logger.

---

### Celery Tasks

| Task                         | Description                                                                                                                                      |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| `send_invoice(order_id)`     | Generates the invoice for a `RepairOrder`. Currently a placeholder for future implementation.                                                    |
| `start_processing(order_id)` | Simulates the order processing workflow. Updates `RepairOrder` status: `processing` → `completed`. Waits 30 seconds to simulate processing time. |

**Request Example (Webhook)** <br>
Stripe automatically sends JSON payloads.<br> 
**Example** for `checkout.session.completed`:
```json
{
  "id": "evt_1N0xxxxxx",
  "type": "checkout.session.completed",
  "data": {
    "object": {
      "id": "cs_test_123456",
      "metadata": {
        "order_id": "7ab8fac1-0905-424f-ad2a-38a534a3d530"
      },
      "amount_total": 5000
    }
  }
}
```
**Response**
```json
{
  "message": "OK"
}
```
**Notes:**
- This endpoint is meant to be called only by Stripe.
- Idempotency ensures the same event is never processed twice.
- Updates RepairOrder and triggers Celery tasks asynchronously.

---

### Stripe Integration
- Use your Stripe secret key in .env.
- For testing webhooks locally, use ngrok to expose the local server.
- Update Stripe webhook URL with ngrok public URL.
- Minimum amount for Stripe payment: ৳60 (as configured).

---

### Ngrok
- Used to expose local Django app for Stripe webhook testing.
- Access Ngrok UI: http://localhost:4040
- Update .env with Ngrok URL in CSRF_TRUSTED_ORIGINS.
