from builtins import Exception, float, int, len, min, print, set, str

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import json
import string
import random
otp_storage = {}

app = Flask(__name__)
app.secret_key = 'medigen-ai-secret-key-2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///medigen.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_BINDS'] = {'online': 'sqlite:///online_portal.db'}

db = SQLAlchemy(app)


# ==================== MODELS ====================
import pytz
from datetime import datetime
def get_india_time():
  return datetime.now(pytz.timezone('Asia/Kolkata'))
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login_id = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    plain_password = db.Column(db.String(100))  # stored for admin view/reset
    role = db.Column(db.String(20), nullable=False)  # admin, doctor, staff, patient
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    mobile = db.Column(db.String(15))
    qualification = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=get_india_time)
    is_active = db.Column(db.Boolean, default=True)
import pytz
from datetime import datetime
def get_india_time():
  return datetime.now(pytz.timezone('Asia/Kolkata'))
class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(20), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    assigned_doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(20))
    mobile = db.Column(db.String(15))
    email = db.Column(db.String(100))
    abha_address = db.Column(db.String(100))
    address = db.Column(db.String(300))
    age = db.Column(db.Integer)
    weight = db.Column(db.Float)
    registered_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    registered_at = db.Column(db.DateTime, default=get_india_time)
    
import pytz
from datetime import datetime
def get_india_time():
  return datetime.now(pytz.timezone('Asia/Kolkata'))
class Prescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prescription_id = db.Column(db.String(20), unique=True, nullable=False)
    patient_id = db.Column(db.String(20), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    symptoms = db.Column(db.Text)
    diagnosis = db.Column(db.Text)
    medicines = db.Column(db.Text)  # JSON string
    lab_reports = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=get_india_time)
    is_finalized = db.Column(db.Boolean, default=False)
# ==================== ONLINE PRESCRIPTION MODEL ====================

class OnlinePrescription(db.Model):

    __bind_key__ = 'online'

    id = db.Column(db.Integer, primary_key=True)

    prescription_id = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    )

    patient_id = db.Column(
        db.String(20),
        nullable=False
    )

    doctor_id = db.Column(
        db.Integer,
        nullable=False
    )

    symptoms = db.Column(db.Text)

    diagnosis = db.Column(db.Text)

    medicines = db.Column(db.Text)

    lab_reports = db.Column(db.Text)

    notes = db.Column(db.Text)

    created_at = db.Column(
        db.DateTime,
        default=get_india_time
    )

    is_finalized = db.Column(
        db.Boolean,
        default=True
    )
# ==================== ONLINE PATIENT MODEL ====================
class OnlinePatient(db.Model):
    __bind_key__ = 'online'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(20), unique=True)
    name = db.Column(db.String(100))
    gender = db.Column(db.String(20))
    age = db.Column(db.Integer)
    weight = db.Column(db.Float)
    mobile = db.Column(db.String(15))
    email = db.Column(db.String(100))
    abha_address = db.Column(db.String(100))
    address = db.Column(db.String(300))
    symptoms = db.Column(db.Text)
    suggested_department = db.Column(db.String(100))
    suggested_doctor_type = db.Column(db.String(100))
    login_id = db.Column(db.String(50), unique=True)
    password_hash = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=get_india_time)
# ==================== HELPERS ====================

def generate_id(prefix, length=6):
    return prefix + ''.join(random.choices(string.digits, k=length))

def login_required(role=None):
    def decorator(f):
        from functools import wraps
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please login first.', 'error')
                return redirect(url_for('login'))
            if role and session.get('role') != role:
                flash('Access denied.', 'error')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated
    return decorator

# ==================== ROUTES ====================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_id = request.form.get('login_id')
        password = request.form.get('password')
        role = request.form.get('role')
        
        user = User.query.filter_by(login_id=login_id, role=role, is_active=True).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['login_id'] = user.login_id
            session['role'] = user.role
            session['name'] = user.name
            
            if role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif role == 'doctor':
                return redirect(url_for('doctor_dashboard'))
            elif role == 'staff':
                return redirect(url_for('staff_dashboard'))
            elif role == 'patient':
                return redirect(url_for('patient_dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    role = session.get('role')
    if role == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif role == 'doctor':
        return redirect(url_for('doctor_dashboard'))
    elif role == 'staff':
        return redirect(url_for('staff_dashboard'))
    elif role == 'patient':
        return redirect(url_for('patient_dashboard'))
    return redirect(url_for('login'))

# ==================== ADMIN ROUTES ====================

@app.route('/admin')
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    doctors = User.query.filter_by(role='doctor', is_active=True).all()
    staff = User.query.filter_by(role='staff', is_active=True).all()
    patients = Patient.query.all()
    prescriptions = Prescription.query.all()
    
    return render_template('admin/dashboard.html', 
                         doctors=doctors, staff=staff, 
                         patients=patients, prescriptions=prescriptions)

@app.route('/admin/register-doctor', methods=['GET', 'POST'])
def admin_register_doctor():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        qualification = request.form.get('qualification')
        role = request.form.get('role', 'doctor')
        login_id = request.form.get('login_id', '').strip()
        password = request.form.get('password', '').strip()
        
        if not login_id or not password:
            flash('Login ID and Password are required.', 'error')
            return render_template('admin/register_user.html')
        
        # Check if login_id already exists
        existing = User.query.filter_by(login_id=login_id).first()
        if existing:
            flash(f'Login ID "{login_id}" already exists. Please choose a different one.', 'error')
            return render_template('admin/register_user.html')
        
        user = User(
            login_id=login_id,
            password_hash=generate_password_hash(password),
            plain_password=password,
            role=role,
            name=name,
            email=email,
            mobile=mobile,
            qualification=qualification
        )
        db.session.add(user)
        db.session.commit()
        
        flash(f'{"Doctor" if role == "doctor" else "Staff"} registered successfully! Login ID: {login_id}', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/register_user.html')

@app.route('/admin/edit-user/<int:user_id>', methods=['GET', 'POST'])
def admin_edit_user(user_id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        new_login_id = request.form.get('login_id', '').strip()
        user.name = request.form.get('name')
        user.email = request.form.get('email')
        user.mobile = request.form.get('mobile')
        user.qualification = request.form.get('qualification')
        
        # Check if new login_id is taken by another user
        if new_login_id and new_login_id != user.login_id:
            conflict = User.query.filter_by(login_id=new_login_id).first()
            if conflict:
                flash(f'Login ID "{new_login_id}" is already taken.', 'error')
                return render_template('admin/edit_user.html', user=user)
            user.login_id = new_login_id
        
        new_password = request.form.get('new_password', '').strip()
        if new_password:
            user.password_hash = generate_password_hash(new_password)
            user.plain_password = new_password
        
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    
    return render_template('admin/edit_user.html', user=user)
@app.route('/admin/delete-user/<int:user_id>')
def admin_delete_user(user_id):
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    user = User.query.get_or_404(user_id)
    if user.role == 'admin':
        flash('Admin cannot be deleted!', 'error')
        return redirect(url_for('admin_dashboard'))
    db.session.delete(user)
    db.session.commit()
    flash('User deleted permanently!', 'success')
    return redirect(url_for('admin_dashboard'))

 # ==================== ONLINE PATIENT ROUTES ====================
@app.route('/online-register', methods=['GET', 'POST'])
def online_register():
    if request.method == 'POST':
        name = request.form.get('name')
        gender = request.form.get('gender')
        age = request.form.get('age')
        weight = request.form.get('weight')
        mobile = request.form.get('mobile')
        email = request.form.get('email')
        abha_address = request.form.get('abha_address')
        address = request.form.get('address')
        symptoms = request.form.get('symptoms')
        login_id = request.form.get('login_id').strip()
        password = request.form.get('password').strip()
        existing = OnlinePatient.query.filter_by(
            login_id=login_id
        ).first()
        if existing:
            flash('Login ID already exists.', 'error')
            return redirect(url_for('online_register'))
        # AI Suggestion
        symptoms_lower = symptoms.lower()
        department = "General Medicine"
        doctor_type = "MBBS Doctor"
        if 'heart' in symptoms_lower or 'chest' in symptoms_lower:
            department = "Cardiology"
            doctor_type = "Cardiologist"
        elif 'skin' in symptoms_lower or 'allergy' in symptoms_lower:
            department = "Dermatology"
            doctor_type = "Skin Specialist"
        elif 'child' in symptoms_lower or 'baby' in symptoms_lower:
            department = "Pediatrics"
            doctor_type = "Child Specialist"
        elif 'eye' in symptoms_lower:
            department = "Ophthalmology"
            doctor_type = "Eye Specialist"
        elif 'bone' in symptoms_lower or 'joint' in symptoms_lower:
            department = "Orthopedic"
            doctor_type = "Orthopedic Doctor"
        patient = OnlinePatient(
            patient_id=generate_id('ONL'),
            name=name,
            gender=gender,
            age=int(age) if age else None,
            weight=float(weight) if weight else None,
            mobile=mobile,
            email=email,
            abha_address=abha_address,
            address=address,
            symptoms=symptoms,
            suggested_department=department,
            suggested_doctor_type=doctor_type,
            login_id=login_id,
            password_hash=generate_password_hash(password))
        db.session.add(patient)
        db.session.commit()
        flash('Online Registration Successful!', 'success')
        return redirect(url_for('online_register'))
    return render_template('online/register.html')
 # ==================== ONLINE LOGIN ====================

@app.route('/online-login', methods=['GET', 'POST'])
def online_login():

    if request.method == 'POST':

        login_id = request.form.get('login_id', '').strip()
        password = request.form.get('password', '').strip()

        patient = OnlinePatient.query.filter_by(
            login_id=login_id
        ).first()

        if patient and check_password_hash(
            patient.password_hash,
            password
        ):

            session['online_patient_id'] = patient.id
            session['online_login_id'] = patient.login_id
            session['online_name'] = patient.name

            flash('Login Successful!', 'success')

            return redirect(url_for('online_dashboard'))

        else:

            flash('Invalid Login ID or Password', 'error')

    return render_template('online/login.html')


# ==================== ONLINE DASHBOARD ====================

@app.route('/online-dashboard')
def online_dashboard():

    if 'online_patient_id' not in session:
        return redirect(url_for('online_login'))

    patient = OnlinePatient.query.get(
        session['online_patient_id']
    )

    prescriptions = OnlinePrescription.query.filter_by(
        patient_id=patient.patient_id,
        is_finalized=True
    ).order_by(
        OnlinePrescription.created_at.desc()
    ).all()

    for p in prescriptions:

        try:
            p.medicines_list = json.loads(
                p.medicines
            ) if p.medicines else []

        except:
            p.medicines_list = []

        doctor = User.query.get(p.doctor_id)

        p.doctor_name = doctor.name if doctor else 'Unknown'

        p.doctor_qualification = (
            doctor.qualification if doctor else ''
        )

    return render_template(
        'online/dashboard.html',
        patient=patient,
        prescriptions=prescriptions
    )

# ==================== STAFF ROUTES ====================

@app.route('/staff')
def staff_dashboard():
    if session.get('role') != 'staff':
        return redirect(url_for('login'))
    
    patients = Patient.query.filter_by(registered_by=session['user_id']).all()
    return render_template('staff/dashboard.html', patients=patients)

@app.route('/staff/register-patient', methods=['GET', 'POST'])
def staff_register_patient():

    if session.get('role') not in ['staff', 'doctor']:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        gender = request.form.get('gender')
        mobile = request.form.get('mobile')
        email = request.form.get('email')
        abha_address = request.form.get('abha_address')
        address = request.form.get('address')
        age = request.form.get('age')
        weight = request.form.get('weight')
        assigned_doctor_id = request.form.get('assigned_doctor_id')
        login_id = request.form.get('login_id', '').strip()
        password = request.form.get('password', '').strip()
        
        if not login_id or not password:
            flash('Login ID and Password are required for patient registration.', 'error')
            return render_template('staff/register_patient.html',doctors=User.query.filter_by(
        role='doctor',
        is_active=True).all()) 

        # Check uniqueness
        existing = User.query.filter_by(login_id=login_id).first()
        if existing:
            flash(f'Login ID "{login_id}" already exists. Choose a different one.', 'error')
            return render_template('staff/register_patient.html',doctors=User.query.filter_by(
        role='doctor',
        is_active=True).all())
        
        # Create user account for patient
        user = User(
            login_id=login_id,
            password_hash=generate_password_hash(password),
            plain_password=password,
            role='patient',
            name=name,
            email=email,
            mobile=mobile
        )
        db.session.add(user)
        db.session.flush()
        today_count = Patient.query.count() + 1
        patient = Patient(
            patient_id=login_id,
            user_id=user.id,
            assigned_doctor_id=int(assigned_doctor_id) if assigned_doctor_id else None,
            name=name,
            gender=gender,
            mobile=mobile,
            email=email,
            abha_address=abha_address,
            address=address,
            age=int(age) if age else None,
            weight=float(weight) if weight else None,
            registered_by=session['user_id']
        )
        db.session.add(patient)
        db.session.commit()
        
        flash(f'Patient registered successfully! Token Number: {today_count}', 'success')
        if session.get('role') == 'doctor':
         return redirect(url_for('doctor_dashboard'))
        return redirect(url_for('staff_dashboard'))
    return render_template(
    'staff/register_patient.html',
    doctors=User.query.filter_by(
        role='doctor',
        is_active=True
    ).all()
)

@app.route('/edit_patient/<int:id>', methods=['GET', 'POST'])
def edit_patient(id):
    if session.get('role') != 'staff':
        return redirect(url_for('login'))
    patient = Patient.query.get(id)
    if request.method == 'POST':
        patient.name = request.form.get('name')
        patient.gender = request.form.get('gender')
        patient.mobile = request.form.get('mobile')
        patient.email = request.form.get('email')
        patient.abha_address = request.form.get('abha_address')
        patient.address = request.form.get('address')
        patient.age = request.form.get('age')
        patient.weight = request.form.get('weight')
        db.session.commit()
        flash('Patient updated successfully!', 'success')
        return redirect(url_for('staff_dashboard'))
    return render_template(
        'staff/edit_patient.html',
        patient=patient)
@app.route('/staff/clear-dashboard')
def clear_staff_dashboard():
    if session.get('role') != 'staff':
        return redirect(url_for('login'))
    patients = Patient.query.filter_by(
        registered_by=session['user_id']
    ).all()
    for patient in patients:
        patient.registered_by = None
    db.session.commit()
    flash('Dashboard cleared successfully!', 'success')
    return redirect(url_for('staff_dashboard'))
# ==================== SEARCH ONLINE PATIENT ====================
@app.route('/doctor/search-online-patient', methods=['GET', 'POST'])
def search_online_patient():

    if session.get('role') != 'doctor':
        return redirect(url_for('login'))

    patient_id = request.values.get('patient_id')

    online_patient = OnlinePatient.query.filter_by(
        patient_id=patient_id
    ).first()

    patients = Patient.query.filter_by(
        assigned_doctor_id=session['user_id']
    ).filter(
        ~Patient.patient_id.in_(
            db.session.query(Prescription.patient_id)
            .filter_by(doctor_id=session['user_id'])
        )
    ).all()

    prescriptions = Prescription.query.filter_by(
        doctor_id=session['user_id']
    ).all()

    if not online_patient:

        flash('Online patient not found', 'error')

        return render_template(
            'doctor/dashboard.html',
            patients=patients,
            prescriptions=prescriptions
        )

    return render_template(
        'doctor/dashboard.html',
        patients=patients,
        prescriptions=prescriptions,
        online_patient=online_patient
    )

    
# ==================== WRITE ONLINE PRESCRIPTION ====================

@app.route('/doctor/write-online-prescription/<patient_id>', methods=['GET', 'POST'])
def write_online_prescription(patient_id):

    if session.get('role') != 'doctor':
        return redirect(url_for('login'))

    patient = OnlinePatient.query.filter_by(
        patient_id=patient_id
    ).first_or_404()

    doctor = User.query.get(session['user_id'])

    if request.method == 'POST':

        symptoms = request.form.get('symptoms')

        diagnosis = request.form.get('diagnosis')

        medicines_json = request.form.get(
            'medicines_json',
            '[]'
        )

        lab_reports = request.form.get('lab_reports')

        notes = request.form.get('notes')

        prescription_id = generate_id('ONRX')

        prescription = OnlinePrescription(

            prescription_id=prescription_id,

            patient_id=patient.patient_id,

            doctor_id=session['user_id'],

            symptoms=symptoms,

            diagnosis=diagnosis,

            medicines=medicines_json,

            lab_reports=lab_reports,

            notes=notes,

            is_finalized=True
        )

        db.session.add(prescription)

        db.session.commit()

        flash(
            'Online prescription created successfully!',
            'success'
        )

        return redirect(url_for('doctor_dashboard'))

    return render_template(
        'doctor/write_prescription.html',
        patient=patient,
        doctor=doctor
    )


# ==================== DOCTOR ROUTES ====================

@app.route('/doctor')
def doctor_dashboard():
    if session.get('role') != 'doctor':
        return redirect(url_for('login'))
    patients = Patient.query.filter_by(
    assigned_doctor_id=session['user_id']
).filter(
    ~Patient.patient_id.in_(
        db.session.query(Prescription.patient_id)
        .filter_by(doctor_id=session['user_id'])
    )
).all()

    prescriptions = Prescription.query.filter_by(doctor_id=session['user_id']).all()
    return render_template('doctor/dashboard.html', patients=patients, prescriptions=prescriptions)

@app.route('/doctor/write-prescription/<patient_id>', methods=['GET', 'POST'])
def write_prescription(patient_id):
    if session.get('role') != 'doctor':
        return redirect(url_for('login'))
    
    patient = Patient.query.filter_by(patient_id=patient_id).first_or_404()
    doctor = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        symptoms = request.form.get('symptoms')
        diagnosis = request.form.get('diagnosis')
        medicines_json = request.form.get('medicines_json', '[]')
        lab_reports = request.form.get('lab_reports')
        notes = request.form.get('notes')
        
        prescription_id = generate_id('RX')
        
        prescription = Prescription(
            prescription_id=prescription_id,
            patient_id=patient_id,
            doctor_id=session['user_id'],
            symptoms=symptoms,
            diagnosis=diagnosis,
            medicines=medicines_json,
            lab_reports=lab_reports,
            notes=notes,
            is_finalized=True
        )
        db.session.add(prescription)
        db.session.commit()
        
        flash(f'Prescription {prescription_id} created successfully!', 'success')
        return redirect(url_for('doctor_dashboard'))
    
    return render_template('doctor/write_prescription.html', patient=patient, doctor=doctor)

@app.route('/doctor/ai-suggest', methods=['POST'])
def ai_suggest():
    """AI suggestion endpoint - uses Claude API for medicine suggestions"""
    if session.get('role') != 'doctor':
        return jsonify({'error': 'Unauthorized'}), 401
    
    symptoms = request.json.get('symptoms', '')
    
    # Medicine database for suggestions
    medicine_db = {
        'fever': [ 
        {'name': 'Paracetamol 500mg','dosage': '1 tablet','frequency': 'TDS','duration': '5 days'},
        { 'name': 'Dolo 650mg','dosage': '1 tablet','frequency': 'TDS','duration': '5 days'},
        {'name': 'Crocin Advance','dosage': '1 tablet','frequency': 'TDS','duration': '5 days'},
        {'name': 'Calpol 650mg','dosage': '1 tablet','frequency': 'TDS','duration': '5 days' },
         {'name': 'PCM Syrup','dosage': '10ml','frequency': 'TDS','duration': '3 days'},
         {'name': 'Ibuprofen 400mg','dosage': '1 tablet','frequency': 'BD after food','duration': '3 days'}
  ],
        'cold': [
            {'name': 'Cetirizine 10mg', 'dosage': '1 tablet', 'frequency': 'OD (once a day)', 'duration': '5 days'},
            {'name': 'Ambroxol 30mg', 'dosage': '1 tablet', 'frequency': 'TDS', 'duration': '5 days'},
        ],
        'cough': [
            {'name': 'Dextromethorphan 15mg', 'dosage': '10ml syrup', 'frequency': 'TDS', 'duration': '5 days'},
            {'name': 'Guaifenesin 200mg', 'dosage': '1 tablet', 'frequency': 'BD', 'duration': '5 days'},
        ],
        'headache': [
            {'name': 'Aspirin 650mg', 'dosage': '1 tablet', 'frequency': 'BD', 'duration': '3 days'},
            {'name': 'Diclofenac 50mg', 'dosage': '1 tablet', 'frequency': 'BD after food', 'duration': '5 days'},
        ],
        'stomach': [
            {'name': 'Pantoprazole 40mg', 'dosage': '1 tablet', 'frequency': 'OD before breakfast', 'duration': '7 days'},
            {'name': 'Domperidone 10mg', 'dosage': '1 tablet', 'frequency': 'TDS before meals', 'duration': '5 days'},
            {'name': 'ORS Sachets', 'dosage': '1 sachet in 1L water', 'frequency': 'As needed', 'duration': '3 days'},
        ],
        'infection': [
            {'name': 'Amoxicillin 500mg', 'dosage': '1 capsule', 'frequency': 'TDS', 'duration': '7 days'},
            {'name': 'Azithromycin 500mg', 'dosage': '1 tablet', 'frequency': 'OD', 'duration': '5 days'},
        ],
        'diabetes': [
            {'name': 'Metformin 500mg', 'dosage': '1 tablet', 'frequency': 'BD with meals', 'duration': '30 days'},
        ],
        'hypertension': [
            {'name': 'Amlodipine 5mg', 'dosage': '1 tablet', 'frequency': 'OD morning', 'duration': '30 days'},
            {'name': 'Telmisartan 40mg', 'dosage': '1 tablet', 'frequency': 'OD morning', 'duration': '30 days'},
        ],
        'pain': [
            {'name': 'Tramadol 50mg', 'dosage': '1 capsule', 'frequency': 'BD', 'duration': '5 days'},
            {'name': 'Aceclofenac 100mg', 'dosage': '1 tablet', 'frequency': 'BD after food', 'duration': '5 days'},
        ],
        'vitamin': [
            {'name': 'Vitamin D3 60000 IU', 'dosage': '1 sachet', 'frequency': 'Once a week', 'duration': '8 weeks'},
            {'name': 'Vitamin B Complex', 'dosage': '1 tablet', 'frequency': 'OD', 'duration': '30 days'},
            {'name': 'Multivitamin tablet', 'dosage': '1 tablet', 'frequency': 'OD after breakfast', 'duration': '30 days'},
        ],
        'allergy': [
            {'name': 'Levocetirizine 5mg', 'dosage': '1 tablet', 'frequency': 'OD at night', 'duration': '7 days'},
            {'name': 'Montelukast 10mg', 'dosage': '1 tablet', 'frequency': 'OD at night', 'duration': '7 days'},
        ],
    }
    
    symptoms_lower = symptoms.lower()
    suggested_medicines = []
    
    keywords = {
        'fever': ['fever', 'bukhar', 'temperature', 'temp'],
        'cold': ['cold', 'sardi', 'runny nose', 'nasal', 'sneezing'],
        'cough': ['cough', 'khansi', 'throat'],
        'headache': ['headache', 'sir dard', 'migraine'],
        'stomach': ['stomach', 'pet dard', 'vomiting', 'diarrhea', 'acidity', 'gastric'],
        'infection': ['infection', 'bacterial', 'throat infection', 'uti'],
        'diabetes': ['diabetes', 'sugar', 'blood sugar'],
        'hypertension': ['bp', 'blood pressure', 'hypertension'],
        'pain': ['pain', 'dard', 'joint pain', 'body ache'],
        'vitamin': ['weakness', 'kamzori', 'fatigue', 'vitamin deficiency'],
        'allergy': ['allergy', 'rash', 'itching', 'skin allergy'],
    }
    
    added = set()
    for category, kws in keywords.items():
        for kw in kws:
            if kw in symptoms_lower and category not in added:
              meds = medicine_db.get(category, [])

        if meds:

                random_meds = random.sample(
                    meds,
                    min(3, len(meds))
                )

                suggested_medicines.extend(random_meds)

        added.add(category)
        break


    # Always add some basic supportive care
    if not suggested_medicines:
        suggested_medicines = [
            {'name': 'Paracetamol 500mg', 'dosage': '1 tablet', 'frequency': 'TDS if needed', 'duration': '3 days'},
            {'name': 'Vitamin C 500mg', 'dosage': '1 tablet', 'frequency': 'OD', 'duration': '7 days'},
        ]
    
    return jsonify({
        'success': True,
        'medicines': suggested_medicines[:6],  # Max 6 suggestions
        'message': f'AI suggested {len(suggested_medicines[:6])} medicines based on symptoms'
    })

# ==================== PATIENT ROUTES ====================

@app.route('/patient')
def patient_dashboard():
    if session.get('role') != 'patient':
        return redirect(url_for('login'))
    
    patient = Patient.query.filter_by(patient_id=session['login_id']).first()
    prescriptions = Prescription.query.filter_by(
        patient_id=session['login_id'], is_finalized=True
    ).order_by(Prescription.created_at.desc()).all()
    
    # Parse medicines for each prescription
    for p in prescriptions:
        try:
            p.medicines_list = json.loads(p.medicines) if p.medicines else []
        except:
            p.medicines_list = []
        doctor = User.query.get(p.doctor_id)
        p.doctor_name = doctor.name if doctor else 'Unknown'
        p.doctor_qualification = doctor.qualification if doctor else ''
    
    return render_template('patient/dashboard.html', patient=patient, prescriptions=prescriptions)
 
# opd_slip rout
@app.route('/patient/opd-slip/<patient_id>')
def patient_opd_slip(patient_id):

    patient = Patient.query.filter_by(patient_id=patient_id).first()

    if not patient:
        flash('Patient not found')
        return redirect('/patient')

    return render_template(
        'patient_opd_slip.html',
        patient=patient
    )
# ==================== DOCTOR VIEW PRESCRIPTION ====================

@app.route('/doctor/prescription/<prescription_id>')
def doctor_view_prescription(prescription_id):

    if session.get('role') != 'doctor':
        return redirect(url_for('login'))

    prescription = Prescription.query.filter_by(
        prescription_id=prescription_id
    ).first_or_404()

    patient = Patient.query.filter_by(
        patient_id=prescription.patient_id
    ).first()

    doctor = User.query.get(prescription.doctor_id)

    try:
        medicines = json.loads(prescription.medicines) if prescription.medicines else []
    except:
        medicines = []

    return render_template(
        'patient/prescription.html',
        prescription=prescription,
        patient=patient,
        doctor=doctor,
        medicines=medicines
    )
# ==================== EDIT PRESCRIPTION ====================

@app.route('/doctor/edit-prescription/<prescription_id>', methods=['GET', 'POST'])
def edit_prescription(prescription_id):

    if session.get('role') != 'doctor':
        return redirect(url_for('login'))

    prescription = Prescription.query.filter_by(
        prescription_id=prescription_id,
        doctor_id=session['user_id']
    ).first_or_404()

    patient = Patient.query.filter_by(
        patient_id=prescription.patient_id
    ).first()

    doctor = User.query.get(session['user_id'])

    if request.method == 'POST':

        prescription.symptoms = request.form.get('symptoms')
        prescription.diagnosis = request.form.get('diagnosis')
        prescription.medicines = request.form.get('medicines_json', '[]')
        prescription.lab_reports = request.form.get('lab_reports')
        prescription.notes = request.form.get('notes')

        db.session.commit()

        flash('Prescription updated successfully!', 'success')

        return redirect(url_for('doctor_dashboard'))

    return render_template(
        'doctor/write_prescription.html',
        patient=patient,
        doctor=doctor,
        prescription=prescription,
        edit_mode=True
    )
@app.route('/patient/prescription/<prescription_id>')
def view_prescription(prescription_id):
    if session.get('role') != 'patient':
        return redirect(url_for('login'))
    
    prescription = Prescription.query.filter_by(
        prescription_id=prescription_id,
        patient_id=session['login_id']
    ).first_or_404()
    
    patient = Patient.query.filter_by(patient_id=session['login_id']).first()
    doctor = User.query.get(prescription.doctor_id)
    
    try:
        medicines = json.loads(prescription.medicines) if prescription.medicines else []
    except:
        medicines = []
    
    return render_template('patient/prescription.html',
                         prescription=prescription,
                         patient=patient,
                         doctor=doctor,
                         medicines=medicines)
@app.route('/print-opd-slip/<int:id>')
def print_opd_slip(id):

    if session.get('role') != 'staff':
        return redirect(url_for('login'))

    patient = Patient.query.get_or_404(id)

    doctor = None

    if patient.assigned_doctor_id:
        doctor = User.query.get(patient.assigned_doctor_id)

    return render_template(
        'staff/opd_slip.html',
        patient=patient,
        doctor=doctor
    )
# ==================== ONLINE VIEW PRESCRIPTION ====================

@app.route('/online/prescription/<prescription_id>')
def online_view_prescription(prescription_id):

    if 'online_patient_id' not in session:
        return redirect(url_for('online_login'))

    prescription = OnlinePrescription.query.filter_by(
        prescription_id=prescription_id
    ).first_or_404()

    patient = OnlinePatient.query.filter_by(
        patient_id=prescription.patient_id
    ).first()

    doctor = User.query.get(
        prescription.doctor_id
    )

    try:
        medicines = json.loads(
            prescription.medicines
        ) if prescription.medicines else []

    except:
        medicines = []

    return render_template(
        'patient/prescription.html',
        prescription=prescription,
        patient=patient,
        doctor=doctor,
        medicines=medicines
    )

# ==================== API ROUTES ====================

@app.route('/api/patients')
def api_patients():
    if session.get('role') not in ['admin', 'doctor', 'staff']:
        return jsonify({'error': 'Unauthorized'}), 401
    
    query = request.args.get('q', '').lower()
    patients = Patient.query.all()
    
    if query:
        patients = [p for p in patients if query in p.name.lower() or query in p.patient_id.lower()]
    
    return jsonify([{
        'id': p.patient_id,
        'name': p.name,
        'age': p.age,
        'mobile': p.mobile
    } for p in patients])
# ============online user password forgot====================
# ============ ONLINE FORGOT PASSWORD ====================

@app.route('/online-forgot-password', methods=['GET', 'POST'])
def online_forgot_password():

    if request.method == 'POST':

        step = request.form.get('step')

        # STEP 1 → FIND USER
        if step == 'find':

            login_id = request.form.get('login_id').strip()

            patient = OnlinePatient.query.filter_by(
                login_id=login_id
            ).first()

            if patient:

                otp = random.randint(100000, 999999)

                otp_storage[login_id] = otp

                print(f"\n🔐 ONLINE OTP for {login_id}: {otp}\n")

                return render_template(
                    'online/forgot_password.html',
                    step='otp',
                    login_id=login_id
                )

            flash('Login ID not found.', 'error')

        # STEP 2 → VERIFY OTP
        elif step == 'otp':

            login_id = request.form.get('login_id')

            entered_otp = request.form.get('otp')

            saved_otp = otp_storage.get(login_id)

            if saved_otp and str(saved_otp) == str(entered_otp):

                return render_template(
                    'online/forgot_password.html',
                    step='reset',
                    login_id=login_id
                )

            flash('Invalid OTP', 'error')

        # STEP 3 → CHANGE PASSWORD
        elif step == 'reset':

            login_id = request.form.get('login_id')

            new_password = request.form.get('new_password')

            patient = OnlinePatient.query.filter_by(
                login_id=login_id
            ).first()

            if patient:

                patient.password_hash = generate_password_hash(
                    new_password
                )

                db.session.commit()

                otp_storage.pop(login_id, None)

                flash('Password Changed Successfully!', 'success')

                return redirect(url_for('online_login'))

    return render_template(
        'online/forgot_password.html',
        step='find'
    )

# ==================== FORGOT PASSWORD ====================

# ==================== FORGOT PASSWORD ====================

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():

    if request.method == 'POST':

        login_id = request.form.get('login_id', '').strip()

        role = request.form.get('role', '').strip()

        user = User.query.filter_by(
            login_id=login_id,
            role=role,
            is_active=True
        ).first()

        if user:

            otp = random.randint(100000, 999999)

            otp_storage[login_id] = otp

            print(f"\n🔐 OTP for {login_id}: {otp}\n")

            flash(
                'OTP Generated Successfully. Check Terminal.',
                'success'
            )

            return render_template(
                'forgot_password.html',
                step='otp',
                login_id=login_id,
                role=role
            )

        else:

            flash(
                'No account found with this Login ID and Role combination.',
                'error'
            )

    return render_template(
        'forgot_password.html',
        step='find'
    )

# ==================== VERIFY OTP ====================

@app.route('/verify-otp', methods=['POST'])
def verify_otp():

    login_id = request.form.get('login_id')

    role = request.form.get('role')

    entered_otp = request.form.get('otp')

    saved_otp = otp_storage.get(login_id)

    if saved_otp and str(saved_otp) == str(entered_otp):

        user = User.query.filter_by(
            login_id=login_id,
            role=role,
            is_active=True
        ).first()

        flash(
            'OTP Verified Successfully',
            'success'
        )

        return render_template(
            'forgot_password.html',
            step='reset',
            user=user,
            login_id=login_id,
            role=role
        )

    flash(
        'Invalid OTP.',
        'error'
    )

    return render_template(
        'forgot_password.html',
        step='otp',
        login_id=login_id,
        role=role
    )

# ==================== RESET PASSWORD ====================

@app.route('/reset-password', methods=['POST'])
def reset_password():

    login_id = request.form.get('login_id', '').strip()

    role = request.form.get('role', '').strip()

    new_password = request.form.get('new_password', '').strip()

    confirm_password = request.form.get('confirm_password', '').strip()

    if not new_password or len(new_password) < 4:

        flash(
            'Password must be at least 4 characters.',
            'error'
        )

        user = User.query.filter_by(
            login_id=login_id
        ).first()

        return render_template(
            'forgot_password.html',
            step='reset',
            user=user,
            login_id=login_id,
            role=role
        )

    if new_password != confirm_password:

        flash(
            'Passwords do not match.',
            'error'
        )

        user = User.query.filter_by(
            login_id=login_id
        ).first()

        return render_template(
            'forgot_password.html',
            step='reset',
            user=user,
            login_id=login_id,
            role=role
        )

    user = User.query.filter_by(
        login_id=login_id,
        role=role,
        is_active=True
    ).first()

    if user:

        user.password_hash = generate_password_hash(new_password)

        user.plain_password = new_password

        db.session.commit()

        otp_storage.pop(login_id, None)

        flash(
            'Password changed successfully! Please login with your new password.',
            'success'
        )

        return redirect(url_for('login'))

    flash(
        'Something went wrong. Please try again.',
        'error'
    )

    return redirect(url_for('forgot_password'))

# ==================== INIT ====================

def init_db():
    with app.app_context():
        db.create_all(bind_key=None)
        db.create_all(bind_key='online')
        
        # Create default admin if not exists
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            admin = User(
                login_id='ADMIN001',
                password_hash=generate_password_hash('admin123'),
                plain_password='admin123',
                role='admin',
                name='Super Admin',
                email='admin@medigen.ai',
                mobile='9999999999'
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Default Admin Created: Login ID: ADMIN001, Password: admin123")

if __name__ == '__main__':
    init_db()
    print("\n🏥 MediGen-AI Server Starting...")
    print("🌐 Open in browser: http://127.0.0.1:5000")
    print("👤 Admin Login: ADMIN001 / admin123\n")
    app.run(debug=True, host='127.0.0.1', port=5000)