from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime

from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)    

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="user")  # 'user' or 'admin'

    applications = db.relationship("Application", backref="user", lazy=True)


class Application(db.Model):
    __tablename__ = "applications"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    address = db.Column(db.String(255), nullable=False)
    nationality = db.Column(db.String(100), nullable=False)
    passport_type = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default="Submitted")

    documents = db.relationship("Document", backref="application", lazy=True)
    appointment = db.relationship("Appointment", backref="application", uselist=False)
    payment = db.relationship("Payment", backref="application", uselist=False)


class Document(db.Model):
    __tablename__ = "documents"
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey("applications.id"), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_name = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)


class Appointment(db.Model):
    __tablename__ = "appointments"
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey("applications.id"), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False)
    appointment_time = db.Column(db.String(20), nullable=False)
    location = db.Column(db.String(150), nullable=False)


class Payment(db.Model):
    __tablename__ = "payments"
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey("applications.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default="Pending")  # Pending / Success / Failed
    method = db.Column(db.String(50))
    transaction_id = db.Column(db.String(100))
    paid_at = db.Column(db.DateTime)


def allowed_file(filename):
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in app.config["ALLOWED_EXTENSIONS"]


@app.context_processor
def inject_globals():
    """Inject common globals into all templates."""
    return {"datetime": datetime}


def current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return User.query.get(user_id)


def login_required(view_func):
    from functools import wraps

    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please log in to continue", "warning")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)

    return wrapped


def admin_required(view_func):
    from functools import wraps

    @wraps(view_func)
    def wrapped(*args, **kwargs):
        user = current_user()
        if not user or user.role != "admin":
            flash("Admin access required", "danger")
            return redirect(url_for("index"))
        return view_func(*args, **kwargs)

    return wrapped

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm = request.form.get("confirm_password")

        if not all([name, email, password, confirm]):
            flash("All fields are required", "danger")
            return redirect(url_for("register"))

        if password != confirm:
            flash("Passwords do not match", "danger")
            return redirect(url_for("register"))

        existing = User.query.filter_by(email=email).first()
        if existing:
            flash("Email already registered", "warning")
            return redirect(url_for("register"))

        user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
        )
        db.session.add(user)
        db.session.commit()

        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            flash("Invalid email or password", "danger")
            return redirect(url_for("login"))

        session["user_id"] = user.id
        session["role"] = user.role
        flash("Logged in successfully", "success")

        if user.role == "admin":
            return redirect(url_for("admin_dashboard"))
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out", "info")
    return redirect(url_for("index"))

@app.route("/dashboard")
@login_required
def dashboard():
    user = current_user()
    application = (
        Application.query.filter_by(user_id=user.id)
        .order_by(Application.created_at.desc())
        .first()
    )
    return render_template("dashboard.html", user=user, application=application)


@app.route("/application", methods=["GET", "POST"])
@login_required
def application_form():
    user = current_user()

    if request.method == "POST":
        full_name = request.form.get("full_name")
        dob = request.form.get("dob")
        address = request.form.get("address")
        nationality = request.form.get("nationality")
        passport_type = request.form.get("passport_type")

        if not all([full_name, dob, address, nationality, passport_type]):
            flash("All fields are required", "danger")
            return redirect(url_for("application_form"))

        try:
            dob_date = datetime.strptime(dob, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid date format", "danger")
            return redirect(url_for("application_form"))

        application = Application(
            user_id=user.id,
            full_name=full_name,
            dob=dob_date,
            address=address,
            nationality=nationality,
            passport_type=passport_type,
            status="Submitted",
        )
        db.session.add(application)
        db.session.commit()

        # Handle multiple file uploads (optional)
        files = request.files.getlist("documents")
        upload_folder = app.config["UPLOAD_FOLDER"]
        os.makedirs(upload_folder, exist_ok=True)

        for f in files:
            if f and allowed_file(f.filename):
                filename = secure_filename(f.filename)
                stored_name = f"app_{application.id}_{filename}"
                path = os.path.join(upload_folder, stored_name)
                f.save(path)

                doc = Document(
                    application_id=application.id,
                    filename=stored_name,
                    original_name=filename,
                )
                db.session.add(doc)

        db.session.commit()

        flash("Application submitted successfully", "success")
        return redirect(url_for("appointment", application_id=application.id))

    return render_template("application_form.html", user=user)


@app.route("/appointment/<int:application_id>", methods=["GET", "POST"])
@login_required
def appointment(application_id):
    application = Application.query.get_or_404(application_id)
    if application.user_id != session.get("user_id"):
        flash("Unauthorized", "danger")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        date_str = request.form.get("appointment_date")
        time_str = request.form.get("appointment_time")
        location = request.form.get("location")

        if not all([date_str, time_str, location]):
            flash("All fields are required", "danger")
            return redirect(url_for("appointment", application_id=application.id))

        try:
            date_val = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Invalid date format", "danger")
            return redirect(url_for("appointment", application_id=application.id))

        if application.appointment:
            application.appointment.appointment_date = date_val
            application.appointment.appointment_time = time_str
            application.appointment.location = location
        else:
            appt = Appointment(
                application_id=application.id,
                appointment_date=date_val,
                appointment_time=time_str,
                location=location,
            )
            db.session.add(appt)

        db.session.commit()
        flash("Appointment scheduled", "success")
        return redirect(url_for("payment", application_id=application.id))

    return render_template("appointment.html", application=application)


@app.route("/payment/<int:application_id>", methods=["GET", "POST"])
@login_required
def payment(application_id):
    application = Application.query.get_or_404(application_id)
    if application.user_id != session.get("user_id"):
        flash("Unauthorized", "danger")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        amount = request.form.get("amount")
        method = request.form.get("method")

        try:
            amount_val = float(amount)
        except (TypeError, ValueError):
            flash("Invalid amount", "danger")
            return redirect(url_for("payment", application_id=application.id))

        if not method:
            flash("Please select payment method", "danger")
            return redirect(url_for("payment", application_id=application.id))

        if application.payment:
            pay = application.payment
            pay.amount = amount_val
            pay.method = method
            pay.status = "Success"  # Simulated success
            pay.transaction_id = f"TXN{int(datetime.utcnow().timestamp())}{application.id}"
            pay.paid_at = datetime.utcnow()
        else:
            pay = Payment(
                application_id=application.id,
                amount=amount_val,
                method=method,
                status="Success",  # Simulated success
                transaction_id=f"TXN{int(datetime.utcnow().timestamp())}{application.id}",
                paid_at=datetime.utcnow(),
            )
            db.session.add(pay)

        application.status = "Under Review"
        db.session.commit()

        flash("Payment completed (simulated)", "success")
        return redirect(url_for("status", application_id=application.id))

    default_amount = 1500.0
    return render_template("payment.html", application=application, default_amount=default_amount)


@app.route("/status")
@login_required
def status_list():
    user = current_user()
    applications = (
        Application.query.filter_by(user_id=user.id)
        .order_by(Application.created_at.desc())
        .all()
    )
    return render_template("status.html", applications=applications)


@app.route("/status/<int:application_id>")
@login_required
def status(application_id):
    application = Application.query.get_or_404(application_id)
    if application.user_id != session.get("user_id"):
        flash("Unauthorized", "danger")
        return redirect(url_for("status_list"))
    return render_template("status.html", applications=[application])


@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    applications = Application.query.order_by(Application.created_at.desc()).all()
    return render_template("admin_dashboard.html", applications=applications)


@app.route("/admin/application/<int:application_id>", methods=["GET", "POST"])
@admin_required
def admin_review(application_id):
    application = Application.query.get_or_404(application_id)

    if request.method == "POST":
        new_status = request.form.get("status")
        if new_status:
            application.status = new_status
            db.session.commit()
            flash("Status updated", "success")
            return redirect(url_for("admin_review", application_id=application.id))

    return render_template("admin_review.html", application=application)


@app.route("/uploads/<path:filename>")
@admin_required
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.cli.command("init-db")
def init_db_command():
    """Initialize the database (creates tables)."""
    db.create_all()
    print("Database initialized.")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        admin_email = "admin@gmail.com"
        existing_admin = User.query.filter_by(email=admin_email).first()
        if not existing_admin:
            admin_user = User(
                name="Administrator",
                email=admin_email,
                password_hash=generate_password_hash("admin123"),
                role="admin",
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Created default admin user admin@gmail.com / admin123")
    app.run(debug=True)
