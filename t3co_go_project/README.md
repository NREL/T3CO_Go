# T3CO Go Django Application

This is a Django application for the T3CO Go project, which allows users to interact with and visualize Total Cost of Ownership (TCO) analyses. The application is designed to be user-friendly and easily deployable, providing a seamless experience for users to input vehicle and scenario assumptions.

## Features

- User-friendly interface for TCO analysis
- Visualization of TCO results
- Integration with existing T3CO Go functionalities
- Support for vehicle and scenario input assumption files
- Easy deployment options

## Project Structure

The project is organized as follows:

```
t3co_go_django/
├── manage.py                # Command-line utility for managing the Django project
├── requirements.txt         # List of dependencies for the application
├── t3co_go_django/         # Main Django project directory
│   ├── __init__.py
│   ├── settings.py          # Configuration settings for the Django project
│   ├── urls.py              # URL routing for the Django project
│   ├── wsgi.py              # WSGI entry point for the project
│   └── asgi.py              # ASGI entry point for the project
├── t3co_app/               # Application for TCO analysis
│   ├── __init__.py
│   ├── admin.py             # Admin site configuration
│   ├── apps.py              # Application configuration
│   ├── models.py            # Data models for the application
│   ├── views.py             # View functions for handling requests
│   ├── urls.py              # URL routing for the t3co_app
│   ├── forms.py             # Forms for user input
│   ├── serializers.py       # Serializers for data conversion
│   ├── migrations/          # Database migrations
│   ├── templates/           # HTML templates for rendering views
│   └── static/              # Static files (CSS, JS, images)
├── api/                     # API endpoints for TCO analyses
│   ├── __init__.py
│   ├── views.py             # API view functions
│   ├── urls.py              # URL routing for API endpoints
│   └── serializers.py       # Serializers for API data
├── core/                    # Core functionalities and utilities
│   ├── __init__.py
│   ├── utils.py             # Utility functions
│   ├── t3co_integration.py   # Integration with T3CO library
│   └── file_handlers.py     # File handling functions
├── static/                  # Additional static files
├── media/                   # Directory for uploaded files
├── demo_inputs/             # Input assumption files for vehicles and scenarios
├── templates/               # Base templates for the project
├── locale/                  # Localization files
├── tests/                   # Unit tests for the application
├── docs/                    # Documentation for the project
├── scripts/                 # Scripts for setup and building
├── pyproject.toml           # Project configuration file
├── Dockerfile                # Docker image instructions
└── docker-compose.yml       # Docker Compose configuration
```

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/NREL/t3co_go.git
   cd t3co_go_django
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run database migrations:
   ```
   python manage.py migrate
   ```

4. Start the development server:
   ```
   python manage.py runserver
   ```

5. Access the application at `http://127.0.0.1:8000/`.

## Deployment

The application can be easily deployed using Docker. Refer to the `Dockerfile` and `docker-compose.yml` for instructions on building and running the application in a containerized environment.

## Executable File

There are plans to create an executable file for Windows and Mac that will launch the web application with the necessary inputs and editing capabilities, utilizing the local machine's computational resources. This will simplify the user experience further by allowing users to run the application without needing to set up a development environment.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License

This project is licensed under the BSD-3-Clause License. See the LICENSE file for more details.