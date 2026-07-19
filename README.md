# 🏥 MediGen-AI
**A Secure Hybrid Healthcare Portal with Rule-Based Smart Prescription & E-Pharmacy Integration**

MCA Project | Ravi Ranjan Kumar | Aryabhatta Knowledge University, Patna
Session 2024-2026| ID 1107 | Roll 05|Registration 24326711023

Guided by Dr. Amit Shukla Sir
---

## ⚡ Quick Setup (Local Server)

### Step 1 — Install Python
Download Python 3.10+ from: https://www.python.org/downloads/
✅ During install, check "Add Python to PATH"

### Step 2 — Open Terminal / CMD in this folder
Right-click the `medigen-ai` folder → "Open in Terminal"

### Step 3 — Install Dependencies
```
pip install -r requirements.txt
```

### Step 4 — Run the Server
```
python app.py
```

### Step 5 — Open Browser
Go to: **http://127.0.0.1:5000**

---

## 🔑 Default Login Credentials

| Role | Login ID | Password |
|------|----------|----------|
| **Admin** | ADMIN001 | admin123 |
| Doctor | (given by Admin) | (given by Admin) |
| Staff | (given by Admin) | (given by Admin) |
| Patient | (given by Staff) | (given by Staff) |

---

## 📋 How to Use

### Admin Workflow:
1. Login with ADMIN001 / admin123
2. Go to "Add Doctor/Staff" → register doctors with name, qualification, mobile, email
3. Login ID & Password are auto-generated — note them for the person

### Medical Staff Workflow:
1. Login with Staff credentials
2. Click "Register Patient" → fill all patient details
3. Patient ID & Password are shown after successful registration
4. Give these credentials to the patient

### Doctor Workflow:
1. Login with Doctor credentials
2. See patient list on dashboard
3. Click "Write Prescription" for a patient
4. Enter symptoms → Click "🤖 AI Suggest Medicines" for auto-fill
5. Review & edit medicines if needed
6. Click "Finalize & Sign Prescription"

### Patient Workflow:
1. Login with Patient ID & Password given by staff
2. View prescriptions on dashboard
3. Click "View" to see full prescription with doctor's digital signature
4. Click NetMeds/PharmEasy links to order medicines online
5. Click "Print" to save/print prescription

---

## 🛠 Tech Stack
- **Backend**: Python 3 + Flask
- **Database**: SQLite (auto-created on first run)
- **Frontend**: HTML5 + CSS3 + Vanilla JS
- **AI**: Rule-based medicine suggestion engine

## 📁 Project Structure

mediGen-AI/
├─ __pycache__/
│  └─ app.cpython-312.pyc
├─ {templates,static/
│  └─ {css,js,images},instance}/
├─ instance/
│  ├─ medigen.db
│  └─ online_portal.db
├─ static/
│  ├─ css/
│  ├─ images/
│  └─ js/
├─ templates/
│  ├─ admin/
│  │  ├─ dashboard.html
│  │  ├─ edit_user.html
│  │  └─ register_user.html
│  ├─ doctor/
│  │  ├─ dashboard.html
│  │  └─ write_prescription.html
│  ├─ online/
│  │  ├─ dashboard.html
│  │  ├─ forgot_password.html
│  │  ├─ login.html
│  │  ├─ opd_slip.html
│  │  └─ register.html
│  ├─ patient/
│  │  ├─ dashboard.html
│  │  └─ prescription.html
│  ├─ staff/
│  │  ├─ dashboard.html
│  │  ├─ edit_patient.html
│  │  ├─ opd_slip.html
│  │  └─ register_patient.html
│  ├─ base.html
│  ├─ forgot_password.html
│  ├─ index.html
│  └─ login.html
├─ app.py
├─ README.md
└─ requirements.txt

