
## Technology Stack

- Django & Django REST Framework
- JWT Authentication
- PostgreSQL database
- Celery for background tasks (email sending)
- Swagger/OpenAPI documentation with drf-yasg


## API Endpoints

- Authentication endpoints (register, login, logout, verify-email)
- Article CRUD endpoints
- Rating endpoints
- Category endpoints

## Installation & Setup

1. Clone the repository
2. Create virtual environment and install dependencies
3. Configure database settings
4. Run migrations
5. Start development server



```markdown
# Newspaper Site

An online newspaper editing, publishing, and viewing platform built with Django REST Framework.

## Features

- User authentication with email verification
- Role-based access (Editors/Viewers)
- Article management system
- Category-based article organization
- User rating system for articles


## Technology Stack

- Django 3.2+
- Django REST Framework
- JWT Authentication
- PostgreSQL
- drf-yasg (Swagger documentation)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd newspaper_site
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
Create a `.env` file in the project root with:
```
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=your-database-url
EMAIL_HOST=your-email-host
EMAIL_PORT=your-email-port
EMAIL_HOST_USER=your-email-user
EMAIL_HOST_PASSWORD=your-email-password
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create superuser:
```bash
python manage.py createsuperuser
```

7. Start development server:
```bash
python manage.py runserver
```

8. Start Celery worker (in separate terminal):
```bash
celery -A newspaper_site worker -l info
```

## API Documentation

Access API documentation at `/swagger/` or `/redoc/` after starting the server.

## User Roles

### Editors
- Create, edit, and delete articles
- Manage categories
- Access admin dashboard

### Viewers
- Browse articles
- Rate articles
- View categories

## Project Structure

```
newspaper_site/
├── users/          # Authentication app
├── news/             # Main news application
├── templates/        # HTML templates
├── static/           # Static files
└── news_ique/   # Project configuration
```

## Future Enhancements

- Premium subscription system
- Payment gateway integration
- Advanced search functionality
- review system for articles


## License

This project is licensed under the MIT License.
```

This implementation plan provides a solid foundation for the Newspaper Site with all requested features. The system is designed to be scalable with clear separation of concerns between user roles and functionality.