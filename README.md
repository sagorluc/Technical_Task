# 🛒 E-Commerce API

A Django REST Framework-based e-commerce backend system featuring custom user management, product/category APIs, Stripe checkout integration, AWS S3 media storage, and more.

---

## 🚀 Features

### 1. **User Management**
- Custom user model using `email` as the primary identifier.
- Profile model with one-to-one relation to user.
- Registration with email, password, and profile info.
- JWT-based authentication (`djangorestframework-simplejwt`).


### 2. **Products & Categories**
- Product and Category models with slug generation.
- List and search products by name or description.
- Filter products by category.
- Pagination and ordering by creation date.
- Product creation with image upload and automatic user association.

### 3. **Stripe Payment Integration**
- `CartItem` model to manage shopping cart items.
- Stripe `PaymentIntent` checkout flow using `stripe` Python SDK.
- Secure client-side checkout via Stripe.js integration.

### 4. **Media Handling (AWS S3)**
- File uploads (e.g., product images, profile pictures) handled via AWS S3.
- Configured with `django-storages`, `boto3`, and `python-decouple`.
- Media files served directly from S3 bucket.

---

## 🛠 Tech Stack

- **Backend:** Django, Django REST Framework
- **Auth:** SimpleJWT
- **Payments:** Stripe SDK
- **Storage:** AWS S3 via django-storages
- **Search/Filter:** DRF + django-filter
- **Docs:** Postman (collection included)

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/sagorluc/Technical_Task.git
```

### Create and Activate Virtual Env
```bash
python -m venv venv
source venv/bin/activate   venv\Scripts\activate # on Windows
```

### Install Dependencies
```bash
pip install -r requirements.txt
```
### Create .env File
```env

SECRET_KEY=your-secret-key

# Stripe
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_PUBLISHABLE_KEY=pk_test_xxx

# AWS S3
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=ap-south-1
```
###  Run Migrations
```shell
python manage.py makemigrations
python manage.py migrate
```
### Create Superuser
```shell
python manage.py createsuperuser
```

### Run the Server
```bash
python manage.py runserver
```
### API Endpoints (Sample)
```
🔐 Auth
POST /api/accounts/signup/ — Register new user with profile

POST /api/accounts/login/ — JWT login

GET /api/accounts/profile/ — Authenticated user see the profile

PUT /api/accounts/update/ — Authenticated user update the profile

📦 Products & Categories
POST /api/products/category/create/ — Create product category (auth required)

GET /api/products/list/ — List, search, filter products (auth required)

POST /api/products/create/ — Create product (auth required)

POST /api/products/checkout/ — Checkout the cart (auth required)
```
### 📁 File Uploads
- Profile pictures: profile_pictures/ on S3
- Product images: products/ on S3



