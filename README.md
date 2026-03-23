# 🌐 NMITS — Network Monitoring & Issue Ticketing System

A full-stack web application for monitoring network devices and managing IT support tickets.
Built with **Flask**, **MySQL**, and a custom dark-terminal UI.

---

## 📁 Project Structure

```
nmits/
├── app.py               # Main Flask application & all routes
├── config.py            # Configuration (MySQL / SQLite / env vars)
├── models.py            # SQLAlchemy database models
├── forms.py             # WTForms form definitions
├── network_monitor.py   # Ping utility + APScheduler background job
├── requirements.txt     # Python dependencies
├── setup_mysql.sql      # MySQL DB & user setup script
├── gunicorn.conf.py     # Gunicorn settings (production)
├── Procfile             # Render / Heroku start command
├── render.yaml          # Render deployment config
├── .env.example         # Environment variable template
├── .gitignore
├── templates/
│   ├── base.html        # Shared layout (sidebar, nav, flash)
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html   # Live status grid + quick ping
│   ├── devices.html     # Device management table
│   ├── device_logs.html # Per-device ping history
│   ├── tickets.html     # Ticket list with filters
│   └── ticket_detail.html  # Ticket view, comments, status update
└── static/
    ├── css/style.css    # Full custom dark-terminal stylesheet
    └── js/main.js       # Modal toggle, keyboard shortcuts, auto-refresh
```

---

## ⚙️ Libraries to Install

```
Flask==3.0.3
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.3
Flask-WTF==1.2.1
WTForms==3.1.2
Werkzeug==3.0.3
ping3==4.0.4
APScheduler==3.10.4
python-dotenv==1.0.1
mysql-connector-python==8.4.0
PyMySQL==1.1.1
cryptography==42.0.8
gunicorn==22.0.0
```

Install all at once:
```bash
pip install -r requirements.txt
```

---

## 🚀 Local Setup (Step-by-Step)

### 1. Clone / Download the project
```bash
cd nmits
```

### 2. Create a virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up MySQL
```bash
mysql -u root -p < setup_mysql.sql
```
This creates the `nmits_db` database and a dedicated `nmits_user`.

### 5. Configure environment variables
```bash
cp .env.example .env
```
Edit `.env`:
```
SECRET_KEY=any-random-string-here
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=nmits_user
MYSQL_PASSWORD=YourStrongPassword123!
MYSQL_DATABASE=nmits_db
```
> **SQLite fallback**: If you skip MySQL config, the app automatically uses `instance/nmits.db` (SQLite).

### 6. Run the application
```bash
python app.py
```
Visit: **http://localhost:5000**

---

## 🔐 Default Credentials

| Username | Password   | Role  |
|----------|------------|-------|
| `admin`  | `admin123` | Admin |

> Change this immediately in production!

---

## 🌟 Features

### Dashboard
- Live device status grid (🟢 UP / 🔴 DOWN)
- Quick ping tool — enter any IP/domain for instant check
- Recent tickets summary
- Stats: total devices, online, offline, open tickets
- Auto-refresh every 30 seconds via AJAX

### Network Devices
- Add devices by IP address or domain name
- Manual ping button per device
- View full ping history (last 100 checks)
- Admin can delete devices
- Background scheduler pings all devices every 60 seconds

### Ticketing System
- Create tickets with title, description, priority, and linked device
- Priority levels: Low / Medium / High / Critical
- Status lifecycle: Open → In Progress → Closed
- Filter tickets by status
- Comments on tickets
- Admin can update status; users see their own tickets

### Authentication
- User registration and login
- Role-based access: Admin vs User
- Password hashing with Werkzeug
- Session management via Flask-Login

---

## ☁️ Deploy to Render

1. Push project to a GitHub repository
2. Go to [render.com](https://render.com) → New → Web Service
3. Connect your GitHub repo
4. Render auto-detects `render.yaml`
5. Set environment variables in the Render dashboard:
   - `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`
   - Or use Render's managed PostgreSQL (update `SQLALCHEMY_DATABASE_URI` accordingly)
6. Deploy!

---

## 🔧 Customisation Tips

| What | Where |
|------|-------|
| Change poll interval | `start_scheduler(app, interval_seconds=60)` in `app.py` |
| Add email alerts | Extend `network_monitor.py` with `smtplib` |
| Add latency chart | Use `/api/stats` endpoint + Chart.js on dashboard |
| Add more roles | Extend `User.role` field and route guards |
| Change theme colours | CSS variables at top of `static/css/style.css` |

---

## 📌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/ping` | Ping a host `{"host": "8.8.8.8"}` |
| GET  | `/api/devices/status` | JSON list of all devices + latest status |
| GET  | `/api/stats` | Latency chart data (last 24 h) |
