# Application Structure

## Directory Layout
```
bills_collector/
├── app.py                 # Application entry point
├── config.py             # Configuration settings
├── extensions.py         # Flask extensions
├── models.py            # Database models
├── integrations/        # External service integrations
├── routes/             # Web routes
├── tasks/              # Celery tasks
│   ├── inbox_tasks.py  # Email processing tasks
│   └── __init__.py
├── templates/          # Web templates
└── static/            # Static assets
```

## Component Descriptions

### Core Files
- `app.py`: Main application entry point
- `config.py`: Application configuration settings
- `extensions.py`: Flask extensions initialization
- `models.py`: SQLAlchemy database models

### Directories
- `integrations/`: External service integration modules
  - Google API clients
  - Email service integrations
  - OAuth handlers

- `routes/`: Web application routes
  - Authentication endpoints
  - Account management
  - Rule configuration
  - Status monitoring

- `tasks/`: Celery background tasks
  - Email processing
  - Token refresh
  - Health monitoring
  - Drive cleanup

- `templates/`: Web application templates
  - HTML templates
  - Form templates
  - Error pages

- `static/`: Static assets
  - CSS files
  - JavaScript files
  - Images
  - Other static resources 