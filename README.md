# Damak Municipality - Intern Management System (IMS)

A centralized web-based Intern Management System developed for **Damak Municipality, Koshi Province, Nepal**. The platform is designed to streamline the lifecycle of student and professional internships across municipal divisions, including registration, supervisor oversight, daily logbook records, task delegation, and evaluations.

> **Current Status: Phase 1 (Foundation Phase)**
> Phase 1 delivers the modular Django architecture, settings, environment configuration, responsive Bootstrap 5 base layout, placeholder dashboards, and diagnostics test page.

---

## 🛠️ Technology Stack

- **Backend Framework:** Python 3.10+ / Django 5.x / 6.x
- **Database:** MySQL 8.0+ (supported with PyMySQL connector; SQLite for local standalone development)
- **Frontend & UI:** HTML5, CSS3, JavaScript, Django Templates
- **CSS Framework:** Bootstrap 5.3 + Bootstrap Icons
- **Typography:** Google Fonts (Inter)
- **Configuration:** python-dotenv (environment variable management)

---

## 📋 Project Requirements

The following technologies and tools are required to run this project.

### Runtime & Framework

| Requirement | Details |
|---|---|
| **Python** | 3.10 or higher |
| **Django** | >= 5.0, < 6.1 (see `requirements.txt`) |

### Database

| Requirement | Details |
|---|---|
| **MySQL** | 8.0+ (primary production database) |
| **PyMySQL** | >= 1.1.0 — pure-Python MySQL connector used as the Django DB driver |
| SQLite | Supported as a local/standalone fallback (no extra install needed) |

### Frontend & UI Libraries

| Requirement | Details |
|---|---|
| **HTML5 / CSS3 / JavaScript** | Standard web technologies used across all templates |
| **Bootstrap 5.3** | CSS framework for responsive layout and UI components (loaded via CDN) |
| **Bootstrap Icons** | Icon library bundled with Bootstrap 5 (loaded via CDN) |
| **Chart.js** | 4.4.3 — used for dashboard data visualisations (loaded via CDN) |

### Python Package Dependencies

All Python dependencies are pinned in [`requirements.txt`](requirements.txt):

| Package | Version Constraint | Purpose |
|---|---|---|
| `Django` | >=5.0, <6.1 | Web framework |
| `python-dotenv` | >=1.0.0 | Environment variable management via `.env` |
| `pymysql` | >=1.1.0 | MySQL database connector |
| `cryptography` | >=42.0.0 | Required by PyMySQL for secure connections |
| `Pillow` | >=10.0.0 | Image handling for media uploads |
| `asgiref` | >=3.8.0 | ASGI compatibility layer (Django dependency) |
| `sqlparse` | >=0.5.0 | SQL formatting (Django dependency) |
| `tzdata` | >=2024.1 | Timezone database |

### Development Tools

| Requirement | Details |
|---|---|
| **Git** | Version control — used for source management and deployment |

---

## 📁 Project Structure

```
intern_management/
├── manage.py                     # Django management script
├── config/                       # Project configuration package
│   ├── __init__.py               # Package init & MySQL driver hook
│   ├── asgi.py                   # ASGI entry point
│   ├── settings.py               # Django configuration & DB setup
│   ├── urls.py                   # Root URL routing
│   └── wsgi.py                   # WSGI entry point
├── accounts/                     # User authentication & role portals
├── interns/                      # Intern profiles & academic registry
├── attendance/                   # Attendance check-in/out tracking
├── logbook/                      # Daily & weekly intern logbooks
├── tasks/                        # Task allocation & milestone monitoring
├── evaluations/                  # Performance reviews & certificates
├── documents/                    # Recommendation letters & ID documents
├── templates/                    # Django HTML templates
│   ├── base.html                 # Master layout (responsive sidebar & topbar)
│   ├── home.html                 # IMS landing portal page
│   ├── health.html               # System health & diagnostics page
│   ├── accounts/
│   │   └── login.html            # Role-based login page
│   └── dashboard/
│       ├── supervisor_dashboard.html  # Supervisor dashboard placeholder
│       └── intern_dashboard.html      # Intern dashboard placeholder
├── static/                       # Static assets
│   ├── css/
│   │   └── style.css             # Custom municipal IMS stylesheet
│   └── js/
│       └── main.js               # Responsive sidebar toggles & helpers
├── media/                        # User uploads (avatars, attachments)
├── requirements.txt              # Python package dependencies
├── .env.example                  # Environment variables template
├── .gitignore                    # Git ignore file for Django
└── README.md                     # Project documentation
```

---

## 🚀 Installation & Setup Guide

### 1. Prerequisites

- Python 3.10 or higher installed
- MySQL Server 8.0+ (optional for local dev if using SQLite fallback)
- Git

### 2. Clone Repository & Setup Virtual Environment

```bash
# Clone repository
git clone <repository_url>
cd IMS-main

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Windows (CMD):
.\venv\Scripts\activate.bat
# Linux / macOS:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. MySQL Database Setup

1. Open your MySQL client (e.g. MySQL Command Line Client, phpMyAdmin, or MySQL Workbench):
   ```sql
   CREATE DATABASE damak_ims CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```
2. Ensure your user has privileges on `damak_ims`:
   ```sql
   GRANT ALL PRIVILEGES ON damak_ims.* TO 'root'@'localhost';
   FLUSH PRIVILEGES;
   ```

### 5. Configure Environment Variables

Copy `.env.example` to `.env`:

```bash
# Windows (PowerShell):
Copy-Item .env.example .env

# Linux / macOS:
cp .env.example .env
```

Edit `.env` to match your local setup:

```env
SECRET_KEY=your-secure-django-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# MySQL Database Settings:
DB_ENGINE=mysql
DB_NAME=damak_ims
DB_USER=root
DB_PASSWORD=your_password
DB_HOST=127.0.0.1
DB_PORT=3306

# Or use SQLite for standalone testing:
# DB_ENGINE=sqlite
```

### 6. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create Superuser (Admin)

```bash
python manage.py createsuperuser
```

### 8. Run Development Server

```bash
python manage.py runserver
```

Access the system at `http://127.0.0.1:8000/`.

---

## 🌐 Key URLs & Endpoints

| URL Route | Page / Purpose |
|---|---|
| `http://127.0.0.1:8000/` | Home / Landing Page |
| `http://127.0.0.1:8000/login/` | Role-based Login Page |
| `http://127.0.0.1:8000/dashboard/supervisor/` | Supervisor Dashboard |
| `http://127.0.0.1:8000/dashboard/intern/` | Intern Dashboard |
| `http://127.0.0.1:8000/health/` | System Health & Diagnostics |
| `http://127.0.0.1:8000/admin/` | Django Administration Console |

---

## 📅 Roadmap: Next Phase (Phase 2)

- [ ] Custom `User` profile models with Supervisor and Intern role management.
- [ ] Intern registration, onboarding workflow, and municipal department assignment.
- [ ] Daily attendance check-in / check-out with geolocation / IP logs.
- [ ] Weekly/daily logbook submissions with supervisor review and approval cycle.
- [ ] Task management with deadlines, attachments, and status tracking.
- [ ] Mid-term & final evaluation rubrics with printable certificate generation.
