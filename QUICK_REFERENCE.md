# VillageBid Development Quick Reference

**Fast reference for common development tasks**

---

## 🚀 Startup Commands

```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Start development server
python manage.py runserver

# Run in different port
python manage.py runserver 0.0.0.0:8080

# Start with external access
python manage.py runserver 0.0.0.0:8000
```

---

## 📦 Dependency Management

```bash
# Install requirements
pip install -r requirements.txt

# Add new package
pip install package-name
pip freeze > requirements.txt

# Upgrade all packages
pip install --upgrade -r requirements.txt

# List installed packages
pip list
```

---

## 🗄️ Database Commands

```bash
# Create migrations after model changes
python manage.py makemigrations

# Show pending migrations
python manage.py showmigrations

# Apply migrations
python manage.py migrate

# Migrate specific app
python manage.py migrate products

# Rollback to previous migration
python manage.py migrate products 0002

# See SQL for migration
python manage.py sqlmigrate products 0003

# Backup database
python manage.py dumpdata > backup.json

# Restore database
python manage.py loaddata backup.json

# Database shell
python manage.py dbshell
```

---

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run specific app
python manage.py test products

# Run specific test class
python manage.py test products.tests.ProductViewTests

# Run with verbosity
python manage.py test --verbosity=2

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report in htmlcov/

# Test specific feature
python manage.py test products.tests -k "list"
```

---

## 👤 User Management

```bash
# Create superuser
python manage.py createsuperuser

# Change password
python manage.py changepassword username

# Clear sessions
python manage.py clearsessions

# Django shell for manual operations
python manage.py shell
>>> from accounts.models import User
>>> user = User.objects.get(username='testuser')
>>> user.is_staff = True
>>> user.save()
```

---

## 📁 Static Files

```bash
# Collect static files
python manage.py collectstatic

# Collect without confirmation
python manage.py collectstatic --noinput

# Find static files
python manage.py findstatic css/main.css

# Clear collected static files
python manage.py collectstatic --clear --noinput
```

---

## 🐛 Debugging

```bash
# System check
python manage.py check

# Check specific app
python manage.py check products

# See all settings
python manage.py diffsettings

# Print settings
python manage.py shell
>>> from django.conf import settings
>>> print(settings.INSTALLED_APPS)

# Debug SQL queries (development only)
# Add to settings.py:
# LOGGING = {
#     'version': 1,
#     'handlers': {'console': {'class': 'logging.StreamHandler'}},
#     'loggers': {'django.db.backends': {'handlers': ['console'], 'level': 'DEBUG'}},
# }
```

---

## 🔄 Cache Management

```bash
# Clear Redis cache
redis-cli FLUSHALL

# Or in Django shell
python manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()
```

---

## 📝 Code Quality

```bash
# Format code with Black
black .

# Check code style
flake8 .

# Sort imports
isort .

# Type checking (if using types)
mypy .
```

---

## 🛠️ Useful Django Extensions

```bash
# Install django-extensions
pip install django-extensions

# Then use:
python manage.py shell_plus  # Enhanced shell

# Generate ER diagram (requires graphviz)
python manage.py graph_models -a -o er_diagram.png

# Show database queries
python manage.py sqlshow products
```

---

## 📊 View Database

```bash
# List all tables
python manage.py dbshell
# Then: \dt (PostgreSQL) or .tables (SQLite)

# View table structure
python manage.py dbshell
# Then: \d+ table_name (PostgreSQL) or PRAGMA table_info(table_name) (SQLite)

# Run custom SQL
python manage.py dbshell
# Then: SELECT * FROM products_product LIMIT 10;
```

---

## 🔐 Security Checks

```bash
# Run Django security checks
python manage.py check --deploy

# Check for security issues
# Install: pip install bandit
bandit -r . -ll

# Check for vulnerable dependencies
# Install: pip install safety
safety check
```

---

## 📈 Performance Testing

```bash
# Generate query profiling
# Install: pip install django-debug-toolbar
# Already in requirements.txt

# Use Django Debug Toolbar in development
# Add to INSTALLED_APPS and middleware

# Measure query count
python manage.py shell
>>> from django.test.utils import CaptureQueriesContext
>>> from django.db import connection
>>> with CaptureQueriesContext(connection) as context:
...     # Your code here
>>> print(f"Queries: {len(context)}")
```

---

## 🚢 Deployment Checklist

```bash
# 1. System health check
python manage.py check --deploy

# 2. Collect static files
python manage.py collectstatic --noinput

# 3. Run migrations
python manage.py migrate

# 4. Create backup
python manage.py dumpdata > pre_deploy_backup.json

# 5. Verify tests pass
python manage.py test

# 6. Check security
python manage.py check --deploy

# 7. Monitor error logs
tail -f logs/django.log
```

---

## 📱 Mobile Development

```bash
# Test on local network
python manage.py runserver 0.0.0.0:8000

# Then visit: http://<your-computer-ip>:8000 from mobile device
# Find IP: ipconfig (Windows) or ifconfig (Linux/Mac)

# Disable SSL check for local testing
# In settings.py during development:
CSRF_TRUSTED_ORIGINS = ['http://192.168.1.100:8000']
```

---

## 🔗 Useful URLs

| Path | Purpose |
|------|---------|
| `/` | Home page |
| `/products/` | Product listing |
| `/products/create/` | Create product |
| `/products/<id>/` | Product detail |
| `/auctions/` | Auction listing |
| `/auctions/<id>/` | Auction detail |
| `/auctions/my-bids/` | User's bids |
| `/dashboard/` | User dashboard |
| `/admin/` | Admin interface |
| `/accounts/login/` | Login |
| `/accounts/signup/` | Register |

---

## 💾 Backup & Restore

```bash
# Backup entire database
python manage.py dumpdata --indent 2 > full_backup.json

# Backup specific app
python manage.py dumpdata products --indent 2 > products_backup.json

# Restore from backup
python manage.py loaddata full_backup.json

# Restore specific app
python manage.py loaddata products_backup.json

# Backup PostgreSQL (if using)
pg_dump villagebid > backup.sql

# Restore PostgreSQL
psql villagebid < backup.sql
```

---

## 🎯 Common Errors & Fixes

```bash
# No such table error
python manage.py migrate

# Module not found
pip install -r requirements.txt

# Port already in use
python manage.py runserver 8001

# Static files not loading
python manage.py collectstatic --noinput

# Template not found
# Check: TEMPLATES setting in settings.py
# Ensure template is in correct app's templates folder

# Import error
# Run: python manage.py check
# Verify INSTALLED_APPS in settings.py
```

---

## 🔗 Helpful Links

- Django Docs: https://docs.djangoproject.com/
- Project Repo: https://github.com/yourusername/village_bid_approval
- Issues: https://github.com/yourusername/village_bid_approval/issues
- Admin Panel: http://localhost:8000/admin/

---

**Last Updated**: June 19, 2026
