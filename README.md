# Jewellery E-commerce Django Project (Full)

This project includes:
- Product listing with filters (category, metal type) and search
- Add to cart, update quantity, remove item
- Wishlist (add/remove)
- Checkout with Razorpay (frontend checkout + server-side signature verification)
- Password reset via email (Django's password-reset flow using SMTP configured via .env)
- Admin to manage products and categories

## Setup

1. Create virtualenv and activate it
2. Install requirements:
   pip install -r requirements.txt
3. Create .env file with at least these keys:
   SECRET_KEY=change-me
   DEBUG=1
   RAZORPAY_KEY_ID=rzp_test_xxx
   RAZORPAY_KEY_SECRET=rzp_secret_xxx
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-email-password-or-app-password
   EMAIL_USE_TLS=1
   DEFAULT_FROM_EMAIL=your-email@gmail.com

For Gmail, you should use an App Password (if 2FA enabled) or enable less secure apps (not recommended).

4. Run migrations:
   python manage.py makemigrations
   python manage.py migrate

5. Create superuser:
   python manage.py createsuperuser

6. Run server:
   python manage.py runserver

7. Admin: /admin/ — add Categories and Products (slug must be unique). Add images using admin (Pillow required).

## Notes

- The Razorpay keys must be correct; use test keys for development.
- Password reset emails will be sent using the SMTP settings you provide.
