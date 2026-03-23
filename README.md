# 🌐 NMITS — Network Monitoring & Issue Ticketing System

A full-stack web application for monitoring network devices and managing IT support tickets.
Built with Flask, MySQL, and a custom dark-terminal UI.

📁 Project Structure

```
nmits/
├── app.py              
├── config.py           
├── models.py           
├── forms.py             
├── network_monitor.py   
├── requirements.txt    
├── setup_mysql.sql     
├── gunicorn.conf.py    
├── Procfile            
├── render.yaml         
├── .env.example         
├── .gitignore
├── templates/
│   ├── base.html        
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html   
│   ├── devices.html     
│   ├── device_logs.html 
│   ├── tickets.html    
│   └── ticket_detail.html 
└── static/
    ├── css/style.css    
    └── js/main.js       

⚙️ Libraries to Install

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
## 🔐 Default Credentials

| Username | Password   | Role  |
|----------|------------|-------|
| `admin`  | `admin123` | Admin |

> Change this immediately in production!



🌟 Features

Dashboard
- Live device status grid (🟢 UP / 🔴 DOWN)
- Quick ping tool — enter any IP/domain for instant check
- Recent tickets summary
- Stats: total devices, online, offline, open tickets
- Auto-refresh every 30 seconds via AJAX

Network Devices
- Add devices by IP address or domain name
- Manual ping button per device
- View full ping history (last 100 checks)
- Admin can delete devices
- Background scheduler pings all devices every 60 seconds

Ticketing System
- Create tickets with title, description, priority, and linked device
- Priority levels: Low / Medium / High / Critical
- Status lifecycle: Open → In Progress → Closed
- Filter tickets by status
- Comments on tickets
- Admin can update status; users see their own tickets

Authentication
- User registration and login
- Role-based access: Admin vs User
- Password hashing with Werkzeug
- Session management via Flask-Login
