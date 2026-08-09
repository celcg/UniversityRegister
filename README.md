# University Register

A web application for managing university course enrollment, built with Django. Supports student and professor registration, authentication, and course management.

🔗 **Live demo:** [https://universityregister.onrender.com](https://universityregister.onrender.com)

---

## Features

- Student and professor registration with role-based access
- Professor registration requires a passkey
- Login / logout / password reset
- Course catalog browsing
- Enrollment management
- Django admin panel

---

## Tech Stack

- **Backend:** Django 6.0
- **Database:** SQLite -> PostGRE (in development)
- **Static files:** WhiteNoise
- **Deployment:** Render

---

## Local Setup

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd group
```

### 2. Create and activate virtual environment

```bash
python -m venv django_env
# Windows
django_env\Scripts\activate
# macOS/Linux
source django_env/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the root (`group/`) directory:

```env
SECRET_KEY=your-secret-key-here
PROFESSOR_REGISTRATION_PASSKEY=your-passkey-here
```

### 5. Run migrations and start the server

```bash
cd universityregister
python manage.py migrate
python manage.py runserver
```

Visit [http://localhost:8000](http://localhost:8000).

---

## Deployment (Render and Supabase)

### Environment Variables

Set these in Render → your service → **Environment**:

| Key | Value |
|-----|-------|
| `SECRET_KEY` | your Django secret key |
| `PROFESSOR_REGISTRATION_PASSKEY` | passkey for professor registration |
| `PYTHON_VERSION` | `3.12` |

### Render Settings

| Field | Value |
|-------|-------|
| **Root Directory** | *(empty)* |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `cd universityregister && python manage.py migrate && python manage.py collectstatic --noinput && gunicorn universityregister.wsgi:application` |

---
## Supabase Database
Latest Update: Migrated DB to Supabase. Now Render requires connection to Supabase-

## Project Structure

```
group/
├── .env                        # Local environment variables (not committed)
├── requirements.txt
├── Procfile
└── universityregister/
    ├── manage.py
    ├── catalog/                # Main app (models, views, urls)
    ├── templates/              # HTML templates
    └── universityregister/     # Project settings, urls, wsgi
```

---

## Creating a Superuser

```bash
cd universityregister
python manage.py createsuperuser
```

Then access the admin panel at `/admin/`.
