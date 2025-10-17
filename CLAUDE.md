# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

LlévateloExpress is a comprehensive web platform for vehicle financing in Venezuela, built with Django backend and vanilla JavaScript frontend. The platform allows users to browse vehicles, calculate financing plans, and submit financing applications.

## Essential Commands

### Development Setup
```bash
# Navigate to project directory
cd /var/www/llevateloexpress

# Activate virtual environment
source backend_env/bin/activate

# Run migrations
python manage.py migrate

# Create superuser (for admin access)
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Run development server (local)
python manage.py runserver

# Run shell for debugging
python manage.py shell
```

### Production Management
```bash
# Restart Gunicorn service
sudo systemctl restart llevateloexpress

# Check service status
sudo systemctl status llevateloexpress

# View logs
sudo journalctl -u llevateloexpress -f

# Reload without restart (for code changes)
sudo systemctl reload llevateloexpress

# Restart entire stack
sudo systemctl restart llevateloexpress nginx
```

### Database Operations
```bash
# Make migrations for specific app
python manage.py makemigrations <app_name>

# Apply specific migration
python manage.py migrate <app_name> <migration_number>

# Show migration status
python manage.py showmigrations

# Database backup
python manage.py dumpdata > backup.json

# Load data
python manage.py loaddata <fixture_file>
```

### Static Files and Media
```bash
# Collect static files for production
python manage.py collectstatic

# Clear collected static files
python manage.py collectstatic --clear

# Fix static file permissions
sudo chown -R llevateloexpress:www-data /var/www/llevateloexpress/staticfiles/
sudo chown -R llevateloexpress:www-data /var/www/llevateloexpress/media/
```

## Architecture Overview

### Backend (Django 4.2)
The Django backend follows a modular app-based architecture:

- **llevateloexpress_backend/**: Main project configuration with settings, URLs, and WSGI/ASGI config
- **core/**: Base models and utilities shared across apps
- **products/**: Product catalog management (vehicles, motorcycles, machinery)
- **financing/**: Financing plans, calculations, and loan applications
- **users/**: User authentication, customer profiles, and account management

### Frontend Architecture
Pure JavaScript with modular design pattern:

- **HTML Templates**: Individual pages served directly (not SPA)
- **CSS**: Bootstrap 5 + custom styles in `css/styles.css`
- **JavaScript Modules**:
  - `auth.js`: Authentication and user session management
  - `api.js`: API communication layer
  - `products.js`: Product catalog functionality
  - `calculadora-credillevo.js`: Financing calculator
  - `dashboard.js`: User dashboard functionality
  - `main.js`: Global utilities and initialization

### API Structure
RESTful API using Django REST Framework:
- `/api/products/`: Product catalog endpoints
- `/api/financing/`: Financing plans and calculations
- `/api/users/`: User authentication and profile management

### Authentication System
- JWT tokens with refresh mechanism
- CSRF protection for state-changing operations
- Session-based authentication for admin panel
- Custom user model with customer profile extensions

## Key Configuration Files

- **settings.py**: Main Django settings with production/development configurations
- **.env.production**: Production environment variables (database, API keys)
- **gunicorn_conf.py**: Gunicorn WSGI server configuration
- **llevateloexpress_nginx.conf**: Nginx reverse proxy configuration
- **llevateloexpress.service**: systemd service configuration

## Database Schema

### Core Models
- **User**: Extended Django user with additional customer fields
- **Product**: Base product model with categories (motorcycle, vehicle, machinery)
- **FinancingPlan**: Different financing options (50-50, 70-30, Agricultural)
- **LoanApplication**: Customer financing requests with document uploads
- **Simulation**: Saved financing calculations

### Key Relationships
- Users can have multiple LoanApplications
- Products belong to Categories and have multiple Simulations
- FinancingPlans are used in both Simulations and LoanApplications

## Frontend-Backend Communication

### Data Flow
1. Frontend JavaScript makes authenticated requests via `api.js`
2. Django views process requests using DRF serializers
3. Database operations through Django ORM
4. JSON responses consumed by frontend for UI updates

### Authentication Flow
1. User logs in via `auth.js` → `/api/users/token/`
2. JWT tokens stored in localStorage
3. All API requests include Authorization header
4. Automatic token refresh on expiration

## Development Workflow

### Making Changes
1. **Backend Changes**: Modify Django models/views → Make migrations → Test in shell
2. **Frontend Changes**: Edit JS/CSS → Test in browser → Check console for errors
3. **Database Changes**: Always make migrations and test on development data first

### Testing
- Use Django admin at `/admin/` for data verification
- Check API endpoints via browser or curl
- Test authentication flow in browser developer tools
- Verify static files are serving correctly

### Deployment
- Use `scripts/deploy_to_server.sh` for automated deployment
- Always run migrations in production: `python manage.py migrate`
- Collect static files: `python manage.py collectstatic`
- Restart services: `sudo systemctl restart llevateloexpress`

## Important File Locations

### Configuration
- Django settings: `llevateloexpress_backend/settings.py`
- URL configuration: `llevateloexpress_backend/urls.py`
- Database migrations: `*/migrations/`

### Frontend Assets
- CSS: `css/styles.css` (main styles)
- JavaScript: `js/` directory (modular organization)
- Static files: `static/` (collected to `staticfiles/` for production)
- Images: `img/` and `media/` (user uploads)

### Templates
- HTML pages in root directory (index.html, catalogo.html, etc.)
- Django templates in `templates/` directory

### Scripts and Utilities
- Deployment scripts: `scripts/`
- Management commands: `*/management/commands/`
- Data import scripts: `scripts/import_*.py`

## Common Issues and Solutions

### Authentication Problems
- Check JWT token expiration in browser localStorage
- Verify CSRF token is being sent with POST requests
- Ensure user has proper permissions for protected endpoints

### Static Files Not Loading
- Run `python manage.py collectstatic`
- Check nginx configuration for static file serving
- Verify file permissions: `chown llevateloexpress:www-data`

### Database Issues
- Check connection settings in `.env.production`
- Verify PostgreSQL service is running
- Run migrations if models have changed

### Service Not Starting
- Check systemd service: `sudo systemctl status llevateloexpress`
- View error logs: `sudo journalctl -u llevateloexpress`
- Verify gunicorn socket permissions
- Test Django configuration: `python manage.py check`

## Production Environment

### Server Setup
- Ubuntu 20.04 with Python 3.8
- PostgreSQL 12+ for database
- Nginx for reverse proxy and static files
- Gunicorn as WSGI server
- systemd for service management

### Key Services
- `llevateloexpress.service`: Main Django application
- `nginx`: Web server and reverse proxy
- `postgresql`: Database server

### Monitoring
- Application logs: `/var/log/llevateloexpress/`
- System logs: `journalctl -u llevateloexpress`
- Nginx logs: `/var/log/nginx/`
- Database logs: PostgreSQL system logs

## Security Considerations

- All production secrets in `.env.production` (not in version control)
- HTTPS enforced via nginx configuration
- CSRF protection enabled for all forms
- JWT tokens with short expiration times
- File upload restrictions and validation
- Admin panel restricted to superusers only

## Performance Optimization

- Gunicorn with gevent workers for concurrency
- Static files served directly by nginx
- Database query optimization in Django ORM
- Frontend asset minification for production
- Caching strategy for frequent API calls
