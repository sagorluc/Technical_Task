# 🛒 E-Commerce API With OAuth2.0, JWT, Stripe, S3 Bucket Storeage

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
- **Auth2:** OAuth2.0
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


# Google OAuth
This Django project includes a complete authentication system with support for Google OAuth via django-allauth. Follow the steps below to set up and run the project on your local machine.

### Install the package
```shell
pip install django-allauth # if doesn't need social account
pip install "django-allauth[socialaccount]" # if need social account
```

### ⚙️ Environment Variables
Create a .env file in the project root:
```.env
GOOGLE_OAUTH_CLIENT_ID=your-google-client-id
GOOGLE_OAUTH_SECRET_ID=your-google-secret-id
```

### ⚙️ Installed Apps & Middleware
The following apps and middleware are used for Google OAuth:
```INSTALLED_APPS```
```python
"allauth",
"allauth.account",
"allauth.socialaccount",
"allauth.socialaccount.providers.google",
"allauth.socialaccount.providers.github",  # login with github account
"allauth.socialaccount.providers.twitter", # login with twitter/(X) account
```
```MIDDLEWARE```
```python
"allauth.account.middleware.AccountMiddleware",
```
```TEMPLATES > context_processors```
```python
'django.template.context_processors.request',
```
```⚙️ OAuth Configuration```
```python
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': config("GOOGLE_OAUTH_CLIENT_ID"),
            'secret': config("GOOGLE_OAUTH_SECRET_ID"),
            'key': ''
        },
        'SCOPE': {
            'profile',
            'email',
        },
        'AUTH_PARAMS': {
            'access_type': 'online',
            'prompt': 'consent',
        }
    }
}

SOCIALACCOUNT_LOGIN_ON_GET = True
SOCIALACCOUNT_AUTO_SIGNUP = True            # For autometically sign-in
SOCIALACCOUNT_UNIQUE_EMAIL = True           # Unique email for each account
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True   # authenticated with valid email
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True  
SOCIALACCOUNT_EMAIL_VERIFICATION = None # no need to verified every-time if already verified one time. 
```

### 🔐 Google OAuth Setup
1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one.
3. Navigate to:
   - ```sql
        APIs & Services → Credentials → Create Credentials → OAuth client ID
     ```
4. Choose ```Web application```, set redirect URI to:
   - ```sql
        http://localhost:8000/accounts/google/login/callback/
     ```
5. Copy the ```client_id``` and ```secret```, and place them in your ```.env```.
   - 🔗 Reference: [AllAuth Google Setup Guide](https://docs.allauth.org/en/latest/installation/quickstart.html)
  
#### Migrate the database:
```python
python manage.py migrate

then

python manage.py runserver
```
  
### 📚 Documentation
- [Django AllAuth Docs](https://docs.allauth.org/en/latest/installation/quickstart.html)
- [Google Cloud Console](https://console.cloud.google.com/)


# Static & Media Storage with S3
This Django project uses Amazon S3 for serving both static files and media uploads via the django-storages package. Static files are served publicly, while media files can be customized for private or public access.

### ⚙️ Configuration
The ```STORAGES``` setting in ```settings.py``` is configured as follows:
```python
STORAGES = {
    "default": {
        # Custom backend for media files
        "BACKEND": "s3_storages.storages.CustomMediaS3Boto3Storage",
        "OPTIONS": {
            "access_key": config("AWS_S3_STORAGE_ACCESS_KEY"),
            "secret_key": config("AWS_S3_STORAGE_SECRET_KEY"),
            "bucket_name": config("AWS_S3_STORAGE_BUCKET_NAME"),
            "endpoint_url": config("AWS_S3_STORAGE_ENDPOINT_URL"),
            "custom_domain": config("AWS_S3_STORAGE_CUSTOM_DOMAIN"),
            "location": "media",
        },
    },
    "staticfiles": {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "access_key": config("AWS_S3_STORAGE_ACCESS_KEY"),
            "secret_key": config("AWS_S3_STORAGE_SECRET_KEY"),
            "bucket_name": config("AWS_S3_STORAGE_BUCKET_NAME"),
            "endpoint_url": config("AWS_S3_STORAGE_ENDPOINT_URL"),
            "location": "static",
            "default_acl": "public-read",
        },
    },
}
```
### 🗂 Folder Structure in S3
Your bucket should include two main folders:

- ``media/`` → For user-uploaded content ```(e.g., profile images, documents)```
- ```static/``` → For static assets ```(e.g., CSS, JS, images)```

### 📥 Required Environment Variables
Place these in your ```.env``` file:
```.env
AWS_S3_STORAGE_ACCESS_KEY=your-access-key
AWS_S3_STORAGE_SECRET_KEY=your-secret-key
AWS_S3_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_STORAGE_ENDPOINT_URL=https://your-region.amazonaws.com
AWS_S3_STORAGE_CUSTOM_DOMAIN=your-cloudfront-domain-or-s3-url
```

### 📦 Install Dependencies
Make sure you have ```boto3``` and ```django-storages``` installed:
```bash
pip install boto3 django-storages
pip install django-storages[s3]
```
This will upload all your ```static``` files to the ```S3 bucket``` under the ```static/ folder```.

### 📄 Documentation
- Django settings docs: [Read docs](https://docs.djangoproject.com/en/5.2/ref/settings/)
- Django-storages docs: [Read docs](https://django-storages.readthedocs.io/en/latest/)

