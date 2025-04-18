# Task Manager - Task Management System

A multifunctional system for managing tasks, projects, and teams, developed using Django.

## Contents

- [Features](#features)
- [Technical Stack](#technical-stack)
- [Project Architecture](#project-architecture)
- [Installation and Launch](#installation-and-launch)
- [Project Structure](#project-structure)
- [Data Models](#data-models)
- [Core Components](#core-components)
- [Extending Functionality](#extending-functionality)

## Features

### Task Management
- Create, edit, delete, and view tasks
- Various task statuses (To-do, In Progress, Done)
- Task search and filtering system
- Setting deadlines and deadline tracking
- Task priority designation

### Project Management
- Create and manage projects
- Combine tasks into projects
- Track project progress
- Statistics on completed and incomplete tasks
- Edit and delete projects

### Team Collaboration
- Create and manage teams
- Assign tasks to team members
- Shared access to projects
- Track team member activity
- Edit and delete teams

### Tagging and Categorization
- Add tags to tasks
- Convenient grouping and filtering by tags
- Quick access to related tasks

### Dashboard and Statistics
- Personal dashboard for each user
- Display tasks by urgency
- Performance statistics
- Overview of current projects and teams

## Technical Stack

- **Backend:** Django 3.2+, Python 3.8+
- **Database:** SQLite (for development), easily expandable to PostgreSQL for production
- **Frontend:** HTML, CSS, JavaScript, Bootstrap 5
- **UI Components:** Font Awesome, Bootstrap modal windows, forms
- **Authentication:** Built-in Django system with extensions
- **Developer Tools:** Django Debug Toolbar (optional)

## Project Architecture

The application is built on the Django MTV (Model-Template-View) pattern with extensions:

1. **Mixins** - for code and logic reuse
2. **Class-Based Views** - for structured request handling
3. **Modular Templates** - for reusing interface components
4. **Service Layer** - for separating business logic from views

## Installation and Launch

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- virtualenv (optional, but recommended)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd task_manager
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   
   For Windows:
   ```bash
   venv\Scripts\activate
   ```
   
   For Linux/Mac:
   ```bash
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Apply migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   Open your browser and go to: http://127.0.0.1:8000/

## Project Structure

```
task_manager/
│
├── task_manager/          # Main Django project
│   ├── settings.py        # Project settings
│   ├── urls.py            # Main URL routes
│   ├── wsgi.py            # WSGI configuration
│   └── asgi.py            # ASGI configuration
│
├── tasks/                 # Task management application
│   ├── migrations/        # Database migrations
│   ├── templates/         # HTML templates
│   ├── templatetags/      # Custom template tags
│   ├── forms.py           # Forms for data handling
│   ├── mixins.py          # Mixins for views
│   ├── models.py          # Data models
│   ├── urls.py            # App URL routes
│   ├── views.py           # Basic views
│   ├── task_views.py      # Views for tasks
│   ├── project_views.py   # Views for projects
│   ├── team_views.py      # Views for teams
│   ├── auth_views.py      # Views for authentication
│   └── services.py        # Service layer
│
├── templates/             # General project templates
│   ├── base.html          # Base template
│   ├── components/        # Reusable UI components
│   ├── layouts/           # Page layouts
│   └── ...                # Other templates
│
├── static/                # Static files (CSS, JS, images)
│   ├── css/               # Styles
│   ├── js/                # JavaScript
│   └── images/            # Images
│
├── manage.py              # Django management script
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

## Data Models

### Task
- title - Task title
- description - Description
- status - Status (to_do, in_progress, done)
- priority - Priority (low, medium, high)
- deadline - Completion deadline
- created_by - Creator
- assigned_to - Assignee
- project - Project
- tags - Tags
- created_at - Creation date
- updated_at - Update date

### Project
- name - Project name
- description - Description
- created_by - Creator
- created_at - Creation date
- updated_at - Update date

### Team
- name - Team name
- description - Description
- members - Team members
- projects - Team projects
- created_at - Creation date

### Tag
- name - Tag name
- color - Color (for display)

## Core Components

### Mixins (mixins.py)
Mixins are used for code reuse in views. Main mixins:

- **TaskPermissionMixin** - Managing access rights to tasks
- **ProjectAccessMixin** - Checking access to projects
- **EntityFormMixin** - Common methods for entity forms
- **TaskQuerysetMixin** - Frequently used task queries
- **FormUserKwargsMixin** - Passing user to forms
- **OwnershipMixin** - Automatic creator assignment
- **FilterMixin** - Handling filters in ListView
- **DeleteConfirmationMixin** - Object deletion confirmation
- **StatsMixin** - Adding statistics to context

### Views
The project uses Django Class-Based Views for request handling:

- **TaskViews** - Views for working with tasks
- **ProjectViews** - Views for working with projects
- **TeamViews** - Views for working with teams
- **AuthViews** - Views for authentication

### Forms (forms.py)
Forms for data management:

- **TaskForm** - Form for creating and editing tasks
- **ProjectForm** - Project form
- **TeamForm** - Team form
- **TaskFilterForm** - Form for filtering tasks
- **RegisterForm** - User registration form

### Templates
The project uses a modular template system with component division:

- **base.html** - Main template
- **components/** - Reusable components (breadcrumbs, cards, etc.)
- **layouts/** - Page layouts
- **tasks/** - Templates for tasks
- **projects/** - Templates for projects
- **teams/** - Templates for teams
- **auth/** - Authentication templates

## Extending Functionality

### Adding New Entity Types
1. Create a model in `models.py`
2. Create forms in `forms.py`
3. Create views in a new file, such as `new_entity_views.py`
4. Add URL routes in `urls.py`
5. Create templates in the appropriate folder

### Implementing New Features
1. For common logic, use mixins in `mixins.py`
2. For business logic, create functions in `services.py`
3. For custom tags, use `templatetags/`

### Configuring Access Rights
1. Use `TaskPermissionMixin` as an example
2. For more complex scenarios, consider Django Permissions or django-guardian

---

## Conclusion

Task Manager is a powerful and flexible application for managing tasks and projects. It is suitable for both personal use and small teams. The application architecture is based on Django best practices and allows for easy functionality extension when needed.

If you have questions or suggestions, feel free to create issues or pull requests in the project repository.
