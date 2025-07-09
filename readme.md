# Gleen

**Self-Hosted Lightweight Issue Tracker**

## Overview

Gleen is a Django-based, self-hosted issue management system built with HTMX for dynamic frontend interactions. Designed for small to mid-sized teams, it provides an intuitive interface for reporting, assigning, tracking, and resolving issues within private organizational networks.

## Key Features

- **Organization Setup**: Configure organization name, logo, and motto on first run.
- **Role-Based Access**: Three predefined roles (Admin, Developer, Reporter) with clear permissions.
- **Plan Management**: Create multiple plans (projects) to organize related issues.
- **Issue Lifecycle**: CRUD operations on issues with statuses (Backlog, In Progress, In Review, Done).
- **Kanban Board**: Visualize workflow stages and move issues via drag-and-drop.
- **Tabular View**: Detailed issue table with filtering, sorting, and inline editing (HTMX).
- **Reporting Dashboard**: Graphical charts for issue status distribution and team performance.
- **Self-Hosted**: Deploy on private servers to ensure data privacy and control.

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/your-org/gleen.git
   cd gleen
   ```

2. **Create and activate a virtual environment**:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:

   - Copy `.env.example` to `.env` and update settings (database URL, secret key).

5. **Run migrations**:

   ```bash
   python manage.py migrate
   ```

6. **Create superuser**:

   ```bash
   python manage.py createsuperuser
   ```

7. **Start the development server**:

   ```bash
   python manage.py runserver
   ```

## Usage

- Navigate to `http://localhost:8000` and follow the setup wizard to configure your organization and admin user.
- Access the dashboard to create plans, report issues, and manage workflows.

## Configuration

- **Settings**: Modify `settings.py` or use environment variables for:
  - `DATABASE_URL` (PostgreSQL recommended in production)
  - `SECRET_KEY`
  - `ALLOWED_HOSTS`
- **Static Files**: Collect static assets with:
  ```bash
  python manage.py collectstatic
  ```

## Tech Stack

- **Backend**: Django (Python)
- **Frontend**: HTMX, HTML5, CSS3 (Tailwind CSS optional)
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Server**: Gunicorn, Nginx

## Contributing

Contributions are welcome! Please:

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/YourFeature`).
3. Commit your changes (`git commit -m 'Add YourFeature'`).
4. Push to the branch (`git push origin feature/YourFeature`).
5. Open a pull request.

## License

This project is licensed under the MIT License. See `LICENSE` for details.

---

*Gleen empowers teams with a private, efficient issue tracking solution.*

