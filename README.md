# Student Grade Management System

A comprehensive web application built with Flask for managing student grades, assignments, and academic performance tracking.

## Features

- **User Authentication System**
  - Secure login and registration
  - Role-based access control (Students, Teachers, Administrators)
  - Password protection and session management

- **Dashboard Interface**
  - Customized views for different user roles
  - Student performance overview
  - Grade visualization and statistics

- **Grade Management**
  - Record and track student grades
  - Assignment submission and grading
  - Progress tracking and reporting

## Technology Stack

- **Backend**
  - Flask 3.0.0 (Python web framework)
  - SQLAlchemy (Database ORM)
  - Flask-Login (User session management)
  - Flask-WTF (Form handling and validation)

- **Frontend**
  - HTML5/CSS3
  - JavaScript
  - Bootstrap (Responsive design)

- **Database**
  - SQLite (Development)
  - Supports database migrations using Flask-Migrate

## Project Structure

```
project/
├── app/                    # Application package
│   ├── __init__.py        # Application factory
│   ├── auth.py            # Authentication routes
│   ├── models.py          # Database models
│   ├── routes.py          # Main application routes
│   ├── static/            # Static files (CSS, JS)
│   └── templates/         # HTML templates
├── migrations/            # Database migrations
├── instance/             # Instance-specific files
├── venv/                 # Virtual environment
├── config.py             # Configuration settings
├── init_db.py           # Database initialization
├── requirements.txt      # Project dependencies
└── run.py               # Application entry point
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd project-directory
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory with the following:
```
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key
```

5. Initialize the database:
```bash
python init_db.py
```

6. Run database migrations:
```bash
flask db upgrade
```

## Running the Application

1. Start the development server:
```bash
flask run
```

2. Access the application at `http://localhost:5000`

## Development

- Database migrations can be created using:
```bash
flask db migrate -m "Migration message"
flask db upgrade
```

- The application uses SQLite for development. For production, consider using a more robust database like PostgreSQL.

## Security

- Passwords are securely hashed using Werkzeug's security features
- CSRF protection is enabled for all forms
- Session management is handled securely through Flask-Login
- Environment variables are used for sensitive configuration

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
