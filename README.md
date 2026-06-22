# VillageBid - Agricultural Auction Platform

**Live Marketplace for Livestock, Farm Equipment & Agricultural Products**

![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![Python](https://img.shields.io/badge/Python-3.13.5-blue)
![Django](https://img.shields.io/badge/Django-6.0.6-darkgreen)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3.3-purple)

---

## 📚 Project Overview

VillageBid is a comprehensive Django-based auction and marketplace platform designed for agricultural products, livestock, and farm equipment. It features advanced seller verification, real-time bidding, secure payments, and a professional admin dashboard.

### Key Features

**Marketplace**
- Product listing with advanced filtering (category, location, price, condition)
- 12 products per page with pagination
- Image gallery with primary image selection
- Comprehensive product details and specifications
- SEO-optimized product pages
- Favorites/wishlist functionality

**Auction System**
- Live auction listings with real-time bid tracking
- Reserve price support with reserve met indicator
- Automatic bid increment validation
- Time remaining display (days/hours/minutes)
- Winning bid tracking
- Won auctions history for buyers

**Seller System**
- Professional seller verification badge ✓
- Seller rating system (0-5 stars with reviews)
- Product count and seller statistics
- Seller suspension capability
- Seller profile with business information
- Total revenue tracking

**Reviews & Ratings**
- Product ratings (1-5 stars)
- Verified purchase tracking
- Communication and shipping ratings
- Helpful/unhelpful vote tracking
- Seller response capability
- Review moderation system

**Payment Integration**
- Razorpay payment gateway integration
- Multiple payment methods (UPI, credit/debit card, wallet)
- Payment status tracking
- Order management with shipping
- Refund capability
- Tax and commission tracking

**Admin Interface**
- Advanced product management with bulk actions
- User and seller management
- Auction control and monitoring
- Review moderation dashboard
- Payment and order tracking
- Bid management and status updates
- Custom admin actions with notifications

**Modern UI/UX**
- Bootstrap 5.3.3 responsive design
- Mobile-first design approach
- Sticky navigation
- Card-based layouts
- Status color coding
- Font Awesome 6.4.0 icons
- Smooth animations and transitions
- Form validation with error display

---

## 🏗️ Project Architecture

### Directory Structure

```
village_bid_approval/
├── config/                 # Django settings and URLs
│   ├── settings.py        # Main configuration
│   ├── urls.py            # URL routing
│   ├── wsgi.py            # WSGI application
│   └── asgi.py            # ASGI application
│
├── accounts/              # User authentication & profiles
│   ├── models.py          # User, Profile models
│   ├── views.py           # Login, signup, logout
│   ├── forms.py           # User forms
│   └── admin.py           # Advanced user admin
│
├── products/              # Product marketplace
│   ├── models.py          # Product, ProductImage models
│   ├── views.py           # Product CRUD & listing
│   ├── forms.py           # Product forms with validation
│   └── admin.py           # Product admin with bulk actions
│
├── auctions/              # Auction system
│   ├── models.py          # Auction model
│   ├── views.py           # Auction list, detail, bidding
│   └── admin.py           # Auction admin
│
├── bids/                  # Auction bidding
│   ├── models.py          # Bid model with status tracking
│   ├── views.py           # Bid management
│   └── admin.py           # Bid admin
│
├── reviews/               # Reviews & ratings
│   ├── models.py          # Review model with ratings
│   ├── views.py           # Review creation
│   └── admin.py           # Review moderation
│
├── payments/              # Payment processing
│   ├── models.py          # Payment, Order models
│   ├── views.py           # Payment views
│   └── admin.py           # Payment admin
│
├── categories/            # Product categories
│   ├── models.py          # Category model
│   └── admin.py           # Category management
│
├── dashboard/             # User dashboards
│   ├── models.py          # Dashboard models
│   └── views.py           # Seller/buyer dashboards
│
├── templates/             # HTML templates
│   ├── base/base.html     # Master template with navbar
│   ├── accounts/          # Login/signup templates
│   ├── products/          # Product templates
│   ├── auctions/          # Auction templates
│   ├── core/              # Home page
│   └── dashboard/         # Dashboard templates
│
├── static/                # Static files
│   ├── css/main.css       # Custom styles
│   └── js/                # JavaScript files
│
├── media/                 # User uploads
│
├── requirements.txt       # Python dependencies
├── manage.py              # Django management
└── db.sqlite3            # Development database
```

### Technology Stack

**Backend**
- Django 6.0.6 - Web framework
- Python 3.13.5 - Language runtime
- PostgreSQL - Production database (SQLite for dev)
- Redis 7.0+ - Caching and Celery broker
- Celery 5.4.0 - Async task queue

**Frontend**
- Bootstrap 5.3.3 - CSS framework
- Font Awesome 6.4.0 - Icons
- Poppins Font - Typography
- Pillow 12.2.0 - Image processing

**Integrations**
- Razorpay 1.0.0 - Payment gateway
- Cloudinary + cloudinary_storage - Media hosting
- Django Channels 4.3.2 - WebSocket support
- Django REST Framework + JWT 5.5.1 - API

**Development**
- django-environ 0.13.0 - Environment variables
- Black - Code formatting
- Pytest - Testing framework

---

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- PostgreSQL 12+
- Redis 6.0+
- Git

### Installation

1. **Clone Repository**
   ```bash
   git clone https://github.com/yourusername/village_bid_approval.git
   cd village_bid_approval
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1  # Windows
   # or
   source venv/bin/activate      # Linux/Mac
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run Migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create Superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start Development Server**
   ```bash
   python manage.py runserver
   ```

Visit `http://localhost:8000` to see the application!

---

## 📊 Database Models

### User & Authentication
- **User**: Extended Django user with seller fields (rating, verification, suspension)
- **Profile**: Additional user info (location, notification preferences, business details)

### Products
- **Product**: Marketplace listings with status, SEO fields, views/likes tracking
- **ProductImage**: Product images with primary/secondary selection, alt text, ordering
- **Category**: Product categories with slug for URL-friendly names

### Auctions
- **Auction**: Auction listings linked to products with reserve price, seller/winner
- **Bid**: Individual auction bids with status tracking (active/outbid/winning/won)

### Reviews & Ratings
- **Review**: Product and seller reviews with communication/shipping ratings

### Payments
- **Payment**: Payment records with Razorpay integration
- **Order**: Order tracking with shipping information

### Relationships
- **Favorite**: User favorites/wishlist
- **Notification**: System notifications for users
- **Message**: User-to-user messaging

---

## 🔐 Security Features

- Django security middleware
- CSRF protection on all forms
- SQL injection prevention via ORM
- XSS protection with template escaping
- Password hashing with PBKDF2
- Session security with secure cookies
- Input validation on all forms
- Rate limiting on login attempts
- Admin interface protection

---

## ✅ Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test products

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html

# Performance testing
python manage.py shell
>>> from django.test.utils import override_settings
>>> # Run queries and measure time
```

---

## 📖 API Endpoints (Optional)

If REST API is needed, all models have serializers ready:

```bash
# User endpoints
GET    /api/users/profile/
PATCH  /api/users/profile/

# Product endpoints
GET    /api/products/
POST   /api/products/
GET    /api/products/<id>/
PATCH  /api/products/<id>/
DELETE /api/products/<id>/

# Auction endpoints
GET    /api/auctions/
GET    /api/auctions/<id>/
POST   /api/auctions/<id>/bids/

# Review endpoints
POST   /api/reviews/
GET    /api/reviews/?product=<id>
```

---

## 🐛 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Static files not loading | Run `python manage.py collectstatic` |
| Database errors | Check PostgreSQL is running, run migrations |
| Image upload fails | Check Cloudinary credentials or local media folder permissions |
| Email not sending | Verify SMTP settings in .env |
| Redis connection error | Ensure Redis server is running on localhost:6379 |

---

## 📝 Development Workflow

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/auction-improvements
   ```

2. **Make Changes**
   - Update models
   - Create migrations: `python manage.py makemigrations`
   - Create views/forms
   - Add templates

3. **Test Locally**
   ```bash
   python manage.py runserver
   python manage.py test
   ```

4. **Code Style**
   ```bash
   black .
   flake8 .
   ```

5. **Commit & Push**
   ```bash
   git add .
   git commit -m "Feature: Description"
   git push origin feature/auction-improvements
   ```

6. **Create Pull Request**
   - Document changes
   - Link to issue
   - Request review

---

## 🚀 Deployment

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for comprehensive deployment instructions.

**Quick Deploy**
```bash
# Production settings
export DEBUG=False
export ALLOWED_HOSTS=yourdomain.com

# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Start Gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

---

## 📚 Documentation

- [Deployment Guide](DEPLOYMENT_GUIDE.md) - Production setup
- [API Documentation](API.md) - Endpoint reference
- [Contributing Guide](CONTRIBUTING.md) - Development guidelines
- [Architecture Overview](ARCHITECTURE.md) - System design

---

## 👥 Team & Contribution

This project is maintained by the development team. Contributions are welcome!

### Contributing Steps
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write/update tests
5. Submit a pull request

---

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 💬 Support

For issues, questions, or suggestions:
- Email: support@villagebid.com
- GitHub Issues: [Report Bug](https://github.com/yourusername/village_bid_approval/issues)
- Discord: [Join Community](https://discord.gg/villagebid)

---

## 🙏 Acknowledgments

- Bootstrap team for responsive framework
- Django community for excellent documentation
- Font Awesome for beautiful icons
- Razorpay for payment integration

---

**Last Updated**: June 19, 2026  
**Version**: 1.0.0  
**Status**: ✅ Production Ready
