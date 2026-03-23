-- Run this in MySQL to set up the database before starting the app
-- mysql -u root -p < setup_mysql.sql

CREATE DATABASE IF NOT EXISTS nmits_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'nmits_user'@'localhost' IDENTIFIED BY 'YourStrongPassword123!';
GRANT ALL PRIVILEGES ON nmits_db.* TO 'nmits_user'@'localhost';
FLUSH PRIVILEGES;

-- Tables are auto-created by Flask-SQLAlchemy on first run.
-- This script only creates the DB and user.

SELECT 'nmits_db created and user granted.' AS status;
