from flask import Flask,render_template,request,session,redirect,flash,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login  import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user,logout_user,login_manager,LoginManager
from flask_login import login_required,current_user
from sqlalchemy import text
import MySQLdb

#my db connection
local_server=True

app = Flask(__name__)
app.secret_key="parth"

#unique user access
login_manager=LoginManager(app)
login_manager.login_view='login'
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# app.config['SQLALCHEMY_DATABASE_URI']='mysql://username:password@localhost/databas_table_name'
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost/hms'
db=SQLAlchemy(app)
#here we will create db models that is tables
class Test(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100))

class Medicine(db.Model):
    mid = db.Column(db.Integer, primary_key=True)
    medicine = db.Column(db.String(50), unique=True)
    dosage = db.Column(db.String(50))
    availability = db.Column(db.Boolean(20))

class User(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(50),unique=True)
    email=db.Column(db.String(50),unique=True)
    password=db.Column(db.String(1000))
class Patients(db.Model):
    pid=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(50))
    name=db.Column(db.String(50))
    gender=db.Column(db.String(50))
    slot=db.Column(db.String(50))
    disease=db.Column(db.String(50))
    time=db.Column(db.String(50),nullable=False)
    date=db.Column(db.String(50),nullable=False)
    dept=db.Column(db.String(50))
    number=db.Column(db.String(50))

class Doctors(db.Model):
    did=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(50))
    doctorname=db.Column(db.String(50))
    dept=db.Column(db.String(50))

class Prescription(db.Model):
    prid = db.Column(db.Integer, primary_key=True)
    patientname = db.Column(db.String(50), nullable=False)  # Patient name
    email = db.Column(db.String(50), nullable=False)  # Patient email (not unique anymore)
    doctorname = db.Column(db.String(50), nullable=False)  # Doctor name
    prescription = db.Column(db.Text, nullable=False)  # Prescription details
  


    

# here we pass endpoints and run fn
@app.route("/")
def index():
    return render_template('index.html')

from flask import request, render_template, flash, redirect, url_for
from sqlalchemy import text

   
ADMIN_EMAILS = ["admin@nitdelhi.ac.in", "doctor@nitdelhi.ac.in"]

@app.route('/addstaff', methods=['GET', 'POST'])
@login_required
def doctors():
    
    if current_user.email not in ADMIN_EMAILS:
        flash("Access denied. Only admins can add doctor details.", "danger")
        return redirect(url_for('index'))

    if request.method == "POST":
        email = request.form.get('email')
        doctorname = request.form.get('doctorname')
        dept = request.form.get('dept')

        if email and doctorname and dept:
            try:
                
                with db.engine.begin() as conn:
                    conn.execute(
                        text("INSERT INTO doctors (email, doctorname, dept) VALUES (:email, :doctorname, :dept)"),
                        {"email": email, "doctorname": doctorname, "dept": dept}
                    )
                flash("Doctor information has been stored successfully!", "primary")
            except Exception as e:
                flash(f"An error occurred: {str(e)}", "danger")
        else:
            flash("All fields are required.", "warning")
        
        return redirect(url_for('doctors'))

    return render_template('doctor.html')

from flask import request, render_template, flash, redirect, url_for
from sqlalchemy import text
from flask_login import login_required
@app.route('/staff')
def staff():
    
    doctors = Doctors.query.all()
    return render_template('staff.html', doctors=doctors)



@app.route('/patients', methods=['GET', 'POST'])
@login_required
def patient():
    
    with db.engine.connect() as conn:
        doct = conn.execute(text("SELECT * FROM doctors")).fetchall()

    if request.method == "POST":
        email = request.form.get('email')
        name = request.form.get('name')
        gender = request.form.get('gender')
        slot = request.form.get('slot')
        disease = request.form.get('disease')
        time = request.form.get('time')
        date = request.form.get('date')
        dept = request.form.get('dept')
        number = request.form.get('number')

        if all([email, name, gender, slot, disease, time, date, dept, number]):
            try:
                with db.engine.begin() as conn:
                    conn.execute(text("""
                        INSERT INTO patients (email, name, gender, slot, disease, time, date, dept, number)
                        VALUES (:email, :name, :gender, :slot, :disease, :time, :date, :dept, :number)
                    """), {
                        "email": email,
                        "name": name,
                        "gender": gender,
                        "slot": slot,
                        "disease": disease,
                        "time": time,
                        "date": date,
                        "dept": dept,
                        "number": number
                    })

               

                flash("Booking Confirmed", "info")
                return redirect(url_for('patient'))  
            except Exception as e:
                flash(f"An error occurred: {str(e)}", "danger")
        else:
            flash("All fields are required.", "warning")

    return render_template('patient.html', doct=doct)


@app.route("/bookings")
@login_required
def bookings():
    if current_user.email in ADMIN_EMAILS:  
        
        with db.engine.connect() as connection:
            result = connection.execute(text("SELECT * FROM patients")).fetchall()
    else:
        
        em = current_user.email
        with db.engine.connect() as connection:
            result = connection.execute(text("SELECT * FROM patients WHERE email = :email"), {"email": em}).fetchall()

    return render_template('booking.html', query=result)

@app.route("/search", methods=['POST', 'GET'])
@login_required
def search():
    if request.method == "POST":
        query = request.form.get('search')

        name_match = Doctors.query.filter_by(doctorname=query).all()
        med_match=Medicine.query.filter_by(medicine=query).all()
        if name_match:
            flash("Medical Staff is available", "info")
        
        elif med_match:
            flash("Medicine is available", "info")
        else:
            flash("No matching staff or medicine found", "danger")

    return render_template('index.html')


@app.route("/edit/<string:pid>", methods=['POST', 'GET'])
@login_required
def edit(pid):
    posts = Patients.query.filter_by(pid=pid).first()
    
    if request.method == "POST":
        posts.email = request.form.get('email')
        posts.name = request.form.get('name')
        posts.gender = request.form.get('gender')
        posts.slot = request.form.get('slot')
        posts.disease = request.form.get('disease')
        posts.time = request.form.get('time')
        posts.date = request.form.get('date')
        posts.dept = request.form.get('dept')
        posts.number = request.form.get('number')

        db.session.commit()
        flash("Slot updated successfully", "success")
        return redirect('/bookings')
    
    return render_template('edit.html', posts=posts)


@app.route("/delete/<string:pid>", methods=['POST', 'GET'])
@login_required
def delete(pid): 
    patient = Patients.query.get(pid)
    if patient:
        db.session.delete(patient)
        db.session.commit()
        flash("Slot Deleted Successfully","danger")
    return redirect("/bookings")
    
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == "POST":
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            flash("Email Already Exists", "warning")
            return render_template('signup.html')

        encpassword = generate_password_hash(password)

        
        new_user = User(username=username, email=email, password=encpassword)
        db.session.add(new_user)
        db.session.commit()  

        flash("Signup successful! Please log in.", "success")
        return render_template('login.html')

    return render_template('signup.html')

@app.route("/login",methods=['POST','GET'])
def login():
    if request.method == "POST":
        
        email = request.form.get('email')
        password = request.form.get('password')
        user=User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password,password):
            login_user(user)
            flash("Login successful","primary")
            return redirect(url_for('index'))
        else:
            flash("invalid credentials","danger")
            return render_template('login.html')
   
    return render_template('login.html')
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logout successful","warning")
    return redirect(url_for('login'))
@app.route('/faclities')
def faclities():
    return render_template('faclities.html')
@app.route("/medicines", methods=["GET", "POST"])
@login_required
def medicines():
    if request.method == "POST":
        
        if current_user.email not in ADMIN_EMAILS:
            flash("Only admins can update medicine availability.", "danger")
            return redirect(url_for('medicines'))

        
        medicines = Medicine.query.all()

        for medicine in medicines:
            checkbox_name = f"medicine_{medicine.mid}"
            
            medicine.availability = checkbox_name in request.form

        db.session.commit()
        flash("Medicine availability updated successfully!", "success")

    
    medicines = Medicine.query.all()
    return render_template("medicines.html", medicines=medicines, is_admin=current_user.email in ADMIN_EMAILS)




@app.route("/view_prescription", methods=["GET"])
@login_required
def view_prescription():
    
    if current_user.email in ADMIN_EMAILS:
        flash("Access denied. Only patients can view prescriptions.", "danger")
        return redirect(url_for('index'))

    
    prescriptions = Prescription.query.filter_by(email=current_user.email).all()

    return render_template("view_prescription.html", prescriptions=prescriptions)


@app.route("/edit_prescription", methods=["GET", "POST"])
@login_required
def edit_prescription():
    
    if current_user.email not in ADMIN_EMAILS:
        flash("Access denied. Only doctors can create or edit prescriptions.", "danger")
        return redirect(url_for('index'))

    if request.method == "POST":
        
        patient_email = request.form.get('email')
        patient_name = request.form.get('name')
        prescription_text = request.form.get('prescription')
        doctorname = current_user.username  

        if patient_email and patient_name and prescription_text:
            try:
                
                new_prescription = Prescription(
                    email=patient_email,
                    patientname=patient_name,
                    doctorname=doctorname,
                    prescription=prescription_text
                )
                db.session.add(new_prescription)
                db.session.commit()
                flash("Prescription saved successfully!", "success")
            except Exception as e:
                flash(f"An error occurred: {str(e)}", "danger")
            
            return redirect(url_for('edit_prescription'))
        else:
            flash("All fields are required.", "warning")

    return render_template("edit_prescription.html")
@app.route("/about_us")
def aboutus():
    return render_template('aboutus.html')

@app.route("/Hospitals")
def hospital():
    return render_template('hospital.html')
@app.route("/Aminents")
def aminent():
    return render_template('aminent.html')
@app.route("/Events")
def event():
    return render_template('events.html')
    
@app.route('/test')
def test():
    
    
    
    try:
        Test.query.all()
        return 'My database is Connected'
    except:
        return ' my db is not connected'

app.run(debug=True)
