# Damak Municipality - Intern Management System (IMS)

A centralized web-based Intern Management System developed for **Damak Municipality, Koshi Province, Nepal**. The platform is designed to streamline the lifecycle of student and professional internships across municipal divisions, including registration, supervisor oversight, daily logbook records, task delegation, and evaluations.

> **Current Status: Phase 1 (Foundation Phase)**
> Phase 1 delivers the modular Django architecture, settings, environment configuration, responsive Bootstrap 5 base layout, placeholder dashboards, and diagnostics test page.

---

## 🖥️ Application Preview

The Damak Municipality Intern Management System (IMS) provides key web interfaces tailored to municipal supervisors and interning students:

- **Landing Portal (`/`)**: Public overview page introducing the municipal internship program and providing navigation to login and diagnostic resources.
- **Role-Based Login (`/login/`)**: Secure authentication entry point routing supervisors and interns to their respective portals based on account role.
- **Supervisor Dashboard (`/supervisor/dashboard/`)**: Management hub for supervisors to monitor assigned interns, review pending logbooks, view daily attendance statistics, track task completion, and initiate evaluations.
- **Intern Dashboard (`/intern/dashboard/`)**: Personal workspace for interning students to check in/out for attendance, track logbook approval statuses, view assigned tasks, and monitor overall internship progress.
- **Attendance Tracker (`/intern/attendance/`, `/supervisor/attendance/`)**: Daily check-in/check-out mechanism for interns with supervisor oversight and date-range history filters.
- **Daily Logbook Portal (`/intern/logbook/`, `/supervisor/logbook/`)**: Structured activity logging system allowing interns to submit daily entries and supervisors to approve, reject, or provide feedback.
- **Task Allocation & Progress (`/intern/tasks/`, `/supervisor/tasks/`)**: Task assignment portal supporting priority levels, progress percentage updates, and deadline tracking.
- **Performance Evaluation (`/evaluations/`)**: Rating system evaluating interns across technical capabilities, punctuality, communication, and professionalism.
- **Document Repository (`/documents/`)**: Secure document storage for uploading, viewing, and managing internship verification documents and recommendation letters.

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

## 💻 Local Development Setup

Follow these steps to get the project running on your local machine from scratch.

### Step 1 — Clone the Repository

```bash
git clone <repository_url>
cd IMS-main
```

### Step 2 — Create a Python Virtual Environment

```bash
python -m venv venv
```

> Requires **Python 3.10 or higher**. Verify with `python --version`.

### Step 3 — Activate the Virtual Environment

**Windows (PowerShell):**

```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**

```cmd
.\venv\Scripts\activate.bat
```

**Linux / macOS:**

```bash
source venv/bin/activate
```

Your prompt will be prefixed with `(venv)` once activated.

### Step 4 — Install the Project Dependencies

```bash
pip install -r requirements.txt
```

This installs all packages listed in `requirements.txt`, including Django, PyMySQL, python-dotenv, Pillow, and cryptography.

### Step 5 — Configure Environment Variables

Copy the provided template to create your local `.env` file:

**Windows (PowerShell):**

```powershell
Copy-Item .env.example .env
```

**Linux / macOS:**

```bash
cp .env.example .env
```

Open `.env` in a text editor and update the values to match your local setup:

```env
# Django secret key — generate a strong random value for any real deployment
SECRET_KEY=change-me-to-a-secure-random-secret-key

# Set to True for local development
DEBUG=True

# Comma-separated list of allowed hosts
ALLOWED_HOSTS=127.0.0.1,localhost

# --- Database (choose ONE of the options below) ---

# Option A: MySQL (default — requires MySQL 8.0+ running locally)
DB_ENGINE=mysql
DB_NAME=damak_ims
DB_USER=root
DB_PASSWORD=your_mysql_password_here
DB_HOST=127.0.0.1
DB_PORT=3306

# Option B: SQLite (zero-config fallback — no MySQL installation needed)
# DB_ENGINE=sqlite
```

### Step 6 — Configure the MySQL Database

> **Skip this step entirely if you chose `DB_ENGINE=sqlite` in Step 5.**

Open a MySQL client (MySQL Command Line Client, MySQL Workbench, or phpMyAdmin) and run:

```sql
CREATE DATABASE damak_ims CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
GRANT ALL PRIVILEGES ON damak_ims.* TO 'root'@'localhost';
FLUSH PRIVILEGES;
```

- The database name must be `damak_ims` to match the default value in `.env.example` and `settings.py`.
- The project uses **PyMySQL** as the MySQL connector; it is installed automatically via `requirements.txt` and registered via `config/__init__.py` — no additional MySQL client libraries are required.

### Step 7 — Run Django Migrations

Apply all existing database migrations to create the required tables:

```bash
python manage.py migrate
```

> Do **not** run `makemigrations` on a freshly cloned repository — migration files are already included in the project.

### Step 8 — Create a Django Superuser

Create an admin account to access the Django administration console:

```bash
python manage.py createsuperuser
```

Follow the prompts to set a username, email address, and password.

### Step 9 — Start the Django Development Server

```bash
python manage.py runserver
```

The server will start and display output similar to:

```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

### Step 10 — Open the Application in the Browser

| URL | Page |
|---|---|
| `http://127.0.0.1:8000/` | Home / Landing Page |
| `http://127.0.0.1:8000/login/` | Role-based Login Page |
| `http://127.0.0.1:8000/admin/` | Django Administration Console |
| `http://127.0.0.1:8000/health/` | System Health & Diagnostics |

Log in to the admin console at `http://127.0.0.1:8000/admin/` using the superuser credentials you created in Step 8.

---

## 👔 Supervisor Workflow

This section describes the end-to-end workflow available to a Supervisor user in the current implementation.

---

### 1. Supervisor Logs Into the System

The supervisor navigates to the login page and authenticates using their registered **email address and password**.

- Login page: `http://127.0.0.1:8000/login/`
- The system uses Django's authentication backend. Email is the unique identifier (not username).
- On successful login, the `dashboard_redirect` view detects the user's `SUPERVISOR` role and redirects automatically to the Supervisor Dashboard.
- An incorrect credential returns a generic error message (the system does not reveal whether an email exists).

---

### 2. Supervisor Accesses the Dashboard

After login, the supervisor is directed to the Supervisor Dashboard.

- URL: `http://127.0.0.1:8000/supervisor/dashboard/`
- The dashboard is protected by the `@supervisor_required` decorator; intern-role users and unauthenticated users are blocked.
- The dashboard displays a real-time summary panel including:
  - **Total assigned interns** count
  - **Today's attendance snapshot** — present, on leave, and absent counts for the current date
  - **Pending logbook submissions** count (with a list of the 5 most recent pending logs)
  - **Task statistics** — total, pending, in-progress, completed, and overdue task counts
  - **Evaluation statistics** — number of interns evaluated vs. not yet evaluated

---

### 3. Supervisor Views Assigned Interns

The supervisor can browse the full list of interns assigned to them.

- URL: `http://127.0.0.1:8000/supervisor/interns/`
- Only internships belonging to the logged-in supervisor are shown (server-side enforced).
- The list supports:
  - **Keyword search** — by intern name, email, intern ID, or position
  - **Status filter** — Pending, Active, Completed, Cancelled
  - **Department filter** — by municipal department
- Each intern row displays computed internship progress metrics (working-day-based progress percentage via `calculate_internship_progress`).

---

### 4. Supervisor Monitors Internship Progress

Internship progress is surfaced at multiple points in the system.

- The **My Interns** list (`/supervisor/interns/`) shows per-intern progress metrics calculated from start date, expected end date, and working days completed.
- The **Supervisor Dashboard** aggregates progress indicators across all assigned interns through task and evaluation statistics.
- The supervisor can also view their own profile at `http://127.0.0.1:8000/supervisor/profile/` and update their designation, department, phone, and profile photo.

---

### 5. Supervisor Monitors Intern Attendance

The supervisor has read and write access to attendance records for their assigned interns.

- **Attendance list** URL: `http://127.0.0.1:8000/supervisor/attendance/`
  - Displays all attendance records strictly scoped to the supervisor's assigned interns.
  - Supports filtering by intern name/ID, attendance status (Present, Absent, Leave), and date.
- **Add attendance / leave record** URL: `http://127.0.0.1:8000/supervisor/attendance/create/`
  - The supervisor can log an attendance or leave record on behalf of an assigned intern.
  - A security check prevents submission for interns not assigned to the supervisor.
- **Edit attendance record** URL: `http://127.0.0.1:8000/supervisor/attendance/<id>/edit/`
  - The supervisor can correct an existing attendance record.
- The **Supervisor Dashboard** (`/supervisor/dashboard/`) also shows the live today's attendance counts.

---

### 6. Supervisor Reviews Daily Logbook Submissions

The supervisor reviews, approves, and rejects daily log entries submitted by their assigned interns.

- **Logbook list** URL: `http://127.0.0.1:8000/supervisor/logbook/`
  - Lists all daily log entries scoped to the supervisor's assigned interns.
  - Supports search by intern name, intern ID, or log title, plus filters for intern, status, and date.
  - Displays a pending-count badge showing how many logs await review.
- **Log detail / review** URL: `http://127.0.0.1:8000/supervisor/logbook/<id>/`
  - Shows full log details including title, date, hours worked, activities, and any existing feedback.
  - The supervisor can submit written feedback.
- **Approve log** URL: `http://127.0.0.1:8000/supervisor/logbook/<id>/approve/` (POST)
  - Transitions log status: **Pending → Approved**. Optional feedback can be saved.
- **Reject log** URL: `http://127.0.0.1:8000/supervisor/logbook/<id>/reject/` (POST)
  - Transitions log status: **Pending → Rejected**. Supervisor feedback is **required** for rejection so the intern can resubmit.
- Security is enforced server-side: a supervisor can only act on logs belonging to their assigned interns.

---

### 7. Supervisor Manages Intern Tasks

The supervisor creates, edits, and tracks tasks assigned to their interns.

- **Task list** URL: `http://127.0.0.1:8000/supervisor/tasks/`
  - Lists all tasks for the supervisor's assigned interns.
  - Supports search by task title or intern name/ID, and filters by intern, priority, and status.
  - Overdue tasks (past due date and not completed) are identified by a special filter.
- **Create task** URL: `http://127.0.0.1:8000/supervisor/tasks/create/`
  - The supervisor assigns a new task to one of their interns, setting title, description, priority, and due date.
  - Task is created with status **Pending** and progress **0%**.
- **Task detail** URL: `http://127.0.0.1:8000/supervisor/tasks/<id>/`
  - Full read-only view of the task including current status, progress percentage, and priority.
- **Edit task** URL: `http://127.0.0.1:8000/supervisor/tasks/<id>/edit/`
  - The supervisor can update the task title, description, due date, or priority.
- The **Supervisor Dashboard** also shows task summary statistics (total, pending, in-progress, completed, overdue).

---

### 8. Supervisor Evaluates Assigned Interns

The supervisor creates and manages formal performance evaluations for their assigned interns.

- **Evaluation list** URL: `http://127.0.0.1:8000/evaluations/supervisor/evaluations/`
  - Lists all internships assigned to the supervisor with evaluation status (evaluated / not yet evaluated).
- **Create evaluation** URL: `http://127.0.0.1:8000/evaluations/supervisor/evaluations/create/<internship_id>/`
  - The supervisor submits a formal evaluation for an intern's internship.
  - Context data (task completion counts, log approval counts) is shown during evaluation creation.
  - Only one evaluation per internship is allowed; attempting to create a duplicate redirects to the existing evaluation.
- **Evaluation detail** URL: `http://127.0.0.1:8000/evaluations/supervisor/evaluations/<id>/`
  - Read view of a submitted evaluation.
- **Edit evaluation** URL: `http://127.0.0.1:8000/evaluations/supervisor/evaluations/<id>/edit/`
  - The supervisor can update a previously submitted evaluation.
- The **Supervisor Dashboard** shows a live count of evaluated vs. unevaluated interns.

---

### 9. Supervisor Views and Manages Intern Documents

The supervisor can view and manage documents associated with their assigned interns.

- **Document list** URL: `http://127.0.0.1:8000/documents/`
  - Supervisors see documents for all their assigned interns (scoped server-side by assignment).
  - Supports filtering by intern and document category.
- **Upload document for intern** URL: `http://127.0.0.1:8000/documents/upload/` or `http://127.0.0.1:8000/documents/supervisor/upload/<intern_id>/`
  - The supervisor can upload a document (e.g., recommendation letter, ID document) on behalf of an assigned intern.
  - Security check prevents uploading for interns not assigned to the supervisor.
- **Download document** URL: `http://127.0.0.1:8000/documents/<id>/download/`
  - Serves the file only if the supervisor is confirmed as the responsible supervisor for that intern (IDOR-protected).
- **Delete document** URL: `http://127.0.0.1:8000/documents/<id>/delete/` (POST)
  - Removes the document record and its physical file from media storage.

---

## 🎓 Intern Workflow

This section describes the end-to-end workflow available to an Intern user in the current implementation.

---

### 1. Intern Logs Into the System

The intern navigates to the login page and authenticates using their registered **email address and password**.

- Login page: `http://127.0.0.1:8000/login/`
- The system uses Django's authentication backend. Email is the unique identifier (not username).
- On successful login, the `dashboard_redirect` view detects the user's `INTERN` role and redirects automatically to the Intern Dashboard.
- An incorrect credential returns a generic error message (the system does not reveal whether an email exists).

---

### 2. Intern Accesses the Dashboard

After login, the intern is directed to the Intern Dashboard.

- URL: `http://127.0.0.1:8000/intern/dashboard/`
- The dashboard is protected by the `@intern_required` decorator; supervisor-role users and unauthenticated users are blocked.
- The dashboard displays a personalised summary including:
  - **Today's attendance status** — whether the intern has checked in, checked out, or has no record for today
  - **Attendance statistics** — total working days, present count, leave count, and absent count
  - **Logbook statistics** — total logs submitted, approved, pending, and rejected
  - **Task statistics** — total, pending, in-progress, completed, and overdue task counts
  - **Latest evaluation** — a summary of the supervisor's evaluation if one has been submitted

---

### 3. Intern Views Internship Information and Profile

The intern can view their personal profile and internship placement details.

- **My Profile** URL: `http://127.0.0.1:8000/intern/profile/`
  - Displays personal details: name, intern ID, phone, college, program, semester/year, and address.
  - The intern can update editable fields (phone, college, program, semester/year, address, and profile photo).
  - Protected fields (intern ID, supervisor, department, dates, status) are read-only and cannot be modified by the intern.
- **My Internship** URL: `http://127.0.0.1:8000/intern/internship/`
  - Displays internship placement details: department, supervisor, position, start date, expected end date, and current status.
  - Shows computed progress metrics based on working days (Monday–Friday) elapsed versus the total internship duration.

---

### 4. Intern Records and Checks Attendance

The intern records their own daily attendance directly from the system.

- **Today's Attendance** URL: `http://127.0.0.1:8000/intern/attendance/`
  - Displays the current date's attendance record — status, check-in time, and check-out time.
  - Shows a weekend indicator on Saturdays and Sundays when attendance cannot be marked.
  - Displays attendance summary statistics (total working days, present, leave, absent).
- **Check In** (POST): `http://127.0.0.1:8000/intern/attendance/mark/`
  - Marks the intern as Present for today and records the current time as the check-in time.
  - Validates that the current date falls within the active internship period.
  - Prevents duplicate check-in if a record already exists for today.
- **Check Out** (POST): `http://127.0.0.1:8000/intern/attendance/checkout/`
  - Records the current time as the check-out time on the existing today's attendance record.
  - Requires a prior check-in record for today.
- **Attendance History** URL: `http://127.0.0.1:8000/intern/attendance/history/`
  - Lists all past attendance records for the logged-in intern, ordered by date (most recent first).
  - Supports filtering by status (Present, Leave, Absent) and by month (YYYY-MM format).

---

### 5. Intern Creates and Submits Daily Logbook Entries

The intern submits a daily log entry for each working day to record activities and hours worked.

- **My Logbook** URL: `http://127.0.0.1:8000/intern/logbook/`
  - Lists all the intern's own logbook entries ordered by date (most recent first).
  - Displays logbook statistics: total logs, approved, pending, rejected, and total hours logged.
  - Supports filtering by status (Pending, Approved, Rejected) and by month.
- **Create Log Entry** URL: `http://127.0.0.1:8000/intern/logbook/create/`
  - The intern submits a new daily log containing: date, activity title, description, skills learned, challenges encountered, and hours worked.
  - A new log is created with status **Pending**, awaiting supervisor review.
  - An attendance warning is shown if no Present record exists for the selected date.
  - Only one log entry per date is allowed; attempting to create a duplicate redirects to the existing entry.
  - Weekend dates (Saturday/Sunday) are rejected by the model's validation.
- **Log Detail** URL: `http://127.0.0.1:8000/intern/logbook/<id>/`
  - Read-only view of a specific log entry. Shows supervisor feedback if the log has been reviewed.
- **Edit Log Entry** URL: `http://127.0.0.1:8000/intern/logbook/<id>/edit/`
  - The intern can edit a log that is in **Pending** or **Rejected** status.
  - Saving a **Rejected** log resubmits it, resetting the status back to **Pending**.
  - **Approved** logs cannot be edited.

---

### 6. Intern Views Assigned Tasks and Updates Task Progress

The intern views tasks assigned by their supervisor and reports progress on each task.

- **My Tasks** URL: `http://127.0.0.1:8000/intern/tasks/`
  - Lists all tasks assigned to the logged-in intern.
  - Supports search by task title and filtering by priority (Low, Medium, High) and status (Pending, In Progress, Completed, Overdue).
- **Task Detail / Update Progress** URL: `http://127.0.0.1:8000/intern/tasks/<id>/`
  - Displays full task details: title, description, priority, start date, due date, current status, progress percentage, and any supervisor comments.
  - The intern can update the progress percentage (0–100) and the task status.
  - Setting progress to 100% automatically transitions the task status to **Completed**.
  - Setting progress above 0% on a Pending task automatically transitions status to **In Progress**.
  - Interns can only access and update their own tasks.

---

### 7. Intern Views Their Evaluation and Scores

The intern can view the formal performance evaluation submitted by their supervisor.

- **My Evaluation** URL: `http://127.0.0.1:8000/evaluations/intern/evaluation/`
  - Displays the supervisor's evaluation for the intern's current internship.
  - The evaluation includes scores (rated 1–5) across eight criteria: technical skills, communication, punctuality, problem solving, professionalism, work quality, learning ability, and discipline.
  - Shows the calculated overall score (average of all eight criteria), the supervisor's final recommendation, and written comments (strengths, areas for improvement, and overall comments).
  - If no evaluation has been submitted by the supervisor yet, the page indicates that the evaluation is pending.

---

### 8. Intern Tracks Internship Progress

The intern can view a consolidated progress overview of their entire internship.

- **My Progress** URL: `http://127.0.0.1:8000/evaluations/intern/progress/`
  - Displays a unified progress dashboard covering four areas:
    - **Internship timeline** — total working days, working days completed, remaining working days, and overall time progress percentage (Monday–Friday based).
    - **Attendance summary** — total working days, present count, leave count, absent count, and attendance percentage.
    - **Logbook summary** — total logs submitted, approved, pending, rejected, and total hours logged.
    - **Task summary** — total tasks assigned, completed tasks, and average task progress percentage.
  - Also shows the evaluation summary if one has been submitted by the supervisor.

---

### 9. Intern Uploads and Manages Internship Documents

The intern can upload and manage their own internship-related documents.

- **My Documents** URL: `http://127.0.0.1:8000/documents/`
  - Lists all documents uploaded by or for the logged-in intern.
  - Supports filtering by document category (Identity/Citizenship, Academic Document, Internship Letter, Project Report, Completion Certificate, Other).
- **Upload Document** URL: `http://127.0.0.1:8000/documents/upload/`
  - The intern uploads a document for themselves, providing a title, category, file, and an optional description/notes.
  - Uploaded files are stored securely in the server's media directory.
- **Download Document** URL: `http://127.0.0.1:8000/documents/<id>/download/`
  - Serves the file as a download. Access is restricted to the document's owner intern (IDOR-protected; interns cannot download documents belonging to other interns).
- **Delete Document** URL: `http://127.0.0.1:8000/documents/<id>/delete/` (POST)
  - Removes the document record from the database and deletes the physical file from media storage.
  - Access is restricted to the document's owner intern.

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
