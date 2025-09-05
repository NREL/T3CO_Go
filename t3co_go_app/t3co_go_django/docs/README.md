# T3CO Go Django Application

## Overview
The T3CO Go Django application is designed to provide users with an interactive platform for analyzing and visualizing the Total Cost of Ownership (TCO) of vehicles. This application aims to simplify the user experience while maintaining all functionalities of the existing T3CO Go Streamlit app.

## Features
- User-friendly interface for TCO analysis.
- Upload and manage vehicle and scenario input assumption files.
- Visualize TCO analyses results.
- Responsive design for various devices.

## Installation
1. Clone the repository:
   ```
   git clone https://github.com/NREL/t3co_go.git
   cd t3co_go_django
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Run database migrations:
   ```
   python manage.py migrate
   ```

5. Start the development server:
   ```
   python manage.py runserver
   ```

## Usage
- Access the application at `http://127.0.0.1:8000/`.
- Users can log in or register to access the TCO analysis features.
- Upload vehicle and scenario files from the `/demo_inputs` directory.
- Navigate through the dashboard to perform analyses and view results.

## Deployment
The application can be deployed using Docker. Ensure Docker is installed and run:
```
docker-compose up --build
```

## Executable File
The feasibility of converting this application into an executable file for Windows and Mac is being explored. The goal is to create a standalone application that launches a web server locally, allowing users to interact with the TCO analyses without needing to install Python or dependencies manually.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.

## License
This project is licensed under the BSD-3-Clause License. See the LICENSE file for details.