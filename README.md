# ICT Equipment Rental Management System

A modern web-based ICT Equipment Rental Management System built with **Django** to digitize and streamline the management of ICT equipment borrowing, issuance, returns, and inventory tracking within educational institutions.

> **Case Study:** Federal University Dutse (FUD) ICT Centre

---

## 📖 Overview

The ICT Equipment Rental Management System replaces traditional paper-based equipment lending with a secure, centralized, and efficient digital solution.

The system enables students and staff to request ICT equipment while providing ICT administrators with complete control over equipment inventory, approvals, issuance, returns, and reporting.

---

## ✨ Features

### Authentication

* Secure authentication system
* Custom User Model
* Role-based authorization
* User registration
* Login & logout
* User profile management

### User Roles

#### Administrator (ICT Officer)

* Manage equipment inventory
* Add, edit and delete equipment
* View all rental requests
* Approve or reject requests
* Issue equipment
* Process equipment returns
* Track active rentals
* View rental history
* Generate reports
* Monitor dashboard statistics

#### Students

* Register account
* Browse available equipment
* Submit rental requests
* Track request status
* View active rentals
* View rental history
* Manage profile

#### Staff

* Login securely
* Request equipment
* Track requests
* View active rentals
* View rental history
* Manage profile

---

## 🔄 Rental Workflow

The system follows a real-world ICT Centre equipment lending process.

```text
Student/Staff
        │
        ▼
Submit Request
        │
        ▼
Pending Approval
        │
        ▼
Administrator Review
        │
        ▼
Approve / Reject
        │
        ▼
Issue Equipment
        │
        ▼
Active Rental
        │
        ▼
Equipment Return
        │
        ▼
Inventory Updated
```

---

## 📦 Equipment Categories

The system supports management of various ICT assets including:

* Laptops
* Projectors
* Printers
* Scanners
* Cameras
* Networking Devices

---

## 🛠 Tech Stack

### Backend

* Python 3.x
* Django 5.x

### Frontend

* HTML5
* CSS3
* Bootstrap 5
* Bootstrap Icons
* JavaScript

### Database

* SQLite (Development)
* PostgreSQL (Production Ready)

### Image Handling

* Pillow

---

## 📂 Project Structure

```text
fud-equiptrack/

├── accounts/
├── equipment/
├── rentals/
├── reports/
├── templates/
├── static/
├── media/
├── config/
├── manage.py
└── requirements.txt
```

---

## 🚀 Installation

### Clone the Repository

```bash
git clone https://github.com/Mansur-WP/fud-equiptrack.git
```

```bash
cd fud-equiptrack
```

---

### Create Virtual Environment

Windows

```bash
python -m venv venv
```

Activate

```bash
venv\Scripts\activate
```

Linux / macOS

```bash
python3 -m venv venv
```

```bash
source venv/bin/activate
```

---

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

### Apply Migrations

```bash
python manage.py makemigrations
```

```bash
python manage.py migrate
```

---

### Create Superuser

```bash
python manage.py createsuperuser
```

---

### Run Development Server

```bash
python manage.py runserver
```

Visit

```
http://127.0.0.1:8000/
```

---

## 🧪 Environment setup

### 1) Create a `.env` file

```bash
# copy the example env file
# Windows (PowerShell)
Copy-Item .env.example .env

# or Windows (cmd)
copy .env.example .env

# Linux/macOS
cp .env.example .env
```

Edit `.env` as needed.

### 2) Notes about development vs production

- **Development (default):** `DJANGO_DEBUG=true` and `SECRET_KEY` uses a safe default.
- **Production:** set `DJANGO_DEBUG=false` and provide `DJANGO_SECRET_KEY` via environment variables.

---

## 🧪 Running Tests

Run Django system checks

```bash
python manage.py check
```

Run project tests

```bash
python manage.py test
```


---

## 📊 Core Modules

* Authentication Module
* Equipment Management
* Rental Request Management
* Approval Workflow
* Equipment Issuance
* Active Rentals
* Equipment Return
* Rental History
* Reporting
* Dashboard

---

## 🔒 Security Features

* Role-based access control
* Login required protection
* Administrator-only management actions
* CSRF protection
* Form validation
* Secure password hashing
* Permission-based views

---

## 🎯 Objectives

* Replace manual record keeping
* Prevent duplicate bookings
* Improve equipment tracking
* Maintain accurate inventory
* Streamline approval workflow
* Provide transparent rental history
* Generate management reports

---

## 📸 Screenshots

Add screenshots of:

* Home Page
* Login
* Registration
* Administrator Dashboard
* Student Dashboard
* Equipment Management
* Request Management
* Active Rentals
* Return Equipment
* Reports

---

## 📈 Future Improvements

* Email notifications
* QR Code equipment check-in/check-out
* Barcode support
* PDF report generation
* Excel export
* Equipment maintenance scheduling
* Audit logs
* SMS notifications

---

## 🤝 Contributing

Contributions are welcome.

1. Fork the repository
2. Create a feature branch

```bash
git checkout -b feature/new-feature
```

3. Commit your changes

```bash
git commit -m "Add new feature"
```

4. Push to your branch

```bash
git push origin feature/new-feature
```

5. Open a Pull Request

---

## 📄 License

This project is released under the MIT License.

---


## 👨‍💻 Developer

**Mansur Nasir**

Software Engineer | Python & Django Developer

This project was developed as a custom software solution for a final-year project titled:

> **Design and Implementation of an ICT Equipment Rental Management System: A Case Study of Federal University Dutse (FUD)**

The application was designed and implemented using Django, following modern software engineering principles, role-based access control, and a complete ICT equipment rental workflow.

---

## 📌 Project Note

This repository contains the software implementation developed to support the academic research project. It demonstrates the practical implementation of an ICT Equipment Rental Management System and may be adapted for use in other educational institutions or organizations requiring equipment inventory and rental management.
