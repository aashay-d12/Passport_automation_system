# Passport_automation_system
Passport Automation System – A web portal for seamless passport application, appointment scheduling, document upload, payment processing, and real-time status tracking with admin verification.

# 🛂 Passport Automation System

A **Flask-based web application** that automates the passport application process.  
The system enables users to register, submit passport applications, upload documents, schedule appointments, make payments, and track application status, while administrators can review applications and update their status through a secure admin dashboard.

---

## 📌 Key Features

### 👤 User Features
- Secure user registration and login
- Online passport application submission
- Personal details and passport type selection
- Document upload (PDF, JPG, PNG)
- Appointment scheduling (date, time, center)
- Simulated online payment
- Real-time application status tracking

### 🛠️ Admin Features
- Admin authentication
- View all submitted applications
- Review applicant details and uploaded documents
- Update application status:
  - Submitted
  - Under Review
  - Approved
  - Rejected

---

## 🔄 Application Workflow

1. User registers and logs in
2. User submits passport application details
3. User uploads documents
4. User schedules appointment
5. User completes payment (simulated)
6. Application moves to **Under Review**
7. Admin reviews and updates application status
8. User tracks status from dashboard

---

## 🧱 Tech Stack

| Layer | Technology |
|------|------------|
| Backend | Flask (Python) |
| Database | SQLite (SQLAlchemy ORM) |
| Frontend | HTML, CSS, Jinja2 Templates |
| Authentication | Session-based |
| File Upload | Flask + Werkzeug |
| Deployment Ready | Render / Localhost |

---

## 📁 Project Structure

Passport-Automation-System/
│
├── app.py
├── config.py 
├── database.sql 
├── passport.db 
│
├── templates/ 
├── static/
│ └── uploads/ 
│
├── README.md
└── requirements.txt

---

## 🗄️ Database Schema

### Tables
- `users`
- `applications`
- `documents`
- `appointments`
- `payments`

Relationships are managed using **SQLAlchemy ORM** with foreign key constraints.

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.9+
- pip
- Virtual environment (recommended)

---

```bash
1️⃣ Clone Repository
git clone https://github.com/your-username/passport-automation-system.git
cd passport-automation-system
2️⃣ Create Virtual Environment
bash
Copy code
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
3️⃣ Install Dependencies
bash
Copy code
pip install flask flask-sqlalchemy werkzeug
4️⃣ Initialize Database
bash
Copy code
flask init-db
Or simply run the app once (tables auto-create).

5️⃣ Run the Application
python app.py
Access the app at:
http://127.0.0.1:5000
```

## 🔐 Default Admin Credentials

Field	    Value
Email	    admin@gmail.com
Password	admin123

⚠️ Change these credentials in production

## 📂 File Upload Configuration

Max file size: 10 MB

Allowed formats:
PDF
JPG
JPEG
PNG
Upload path: static/uploads/

## 📊 Application Status Flow

Submitted → Under Review → Approved / Rejected

## 🔮 Future Enhancements

Email & SMS notifications
Online payment gateway integration
Role-based access control (RBAC)
Biometric verification
QR-based application tracking
Admin analytics dashboard

## 📜 License

This project is intended for academic and learning purposes.

## 👨‍💻 Author

Aashay D
Computer Science Student
GitHub: https://github.com/your-username

## ⭐ If you like this project, please consider giving it a star!
