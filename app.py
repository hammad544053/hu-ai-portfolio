import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# Automatically load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = Flask(__name__)

# Security & Vercel deployment variables
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'hammad_ultra_secure_portfolio_key_2026')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///portfolio.db')
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'webp'}
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)

# Email Configuration pulled securely from Environment Variables
MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'hk0448455@gmail.com').strip()
# Strips whitespace or spaces if copied directly from Google Security Manager
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '1234567891011').replace(" ", "").strip()

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# --- DATABASE MODELS ---
class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)


class SiteConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    site_title = db.Column(db.String(100), default="HU.AI")
    hero_name = db.Column(db.String(100), default="Hammad Ullah")
    hero_subtitle = db.Column(db.Text,
                              default="Architecting production-ready Deep Learning, Computer Vision pipelines, and Generative AI frameworks that drive real enterprise value.")
    about_text = db.Column(db.Text,
                           default="7th-semester Computer Science student at Sarhad University of Science & Information Technology, Peshawar. Recipient of Academic Merit Scholarship (2nd position across 6 consecutive semesters) and winner of 1st Position in FYP 2026 for UlcerGuard AI.")


class Metric(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(50), nullable=False)
    label = db.Column(db.String(150), nullable=False)


class Pillar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_filename = db.Column(db.String(200), nullable=True)


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    image_filename = db.Column(db.String(200), nullable=False)
    github_link = db.Column(db.String(300), nullable=True)
    live_link = db.Column(db.String(300), nullable=True)


class Certification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    image_filename = db.Column(db.String(200), nullable=False)


class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)


@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


with app.app_context():
    db.create_all()

    admin_user = os.environ.get('ADMIN_USERNAME', 'admin')
    admin_pass = os.environ.get('ADMIN_PASSWORD', 'hammad12345')

    admin_obj = Admin.query.filter_by(username=admin_user).first()
    if not admin_obj:
        hashed_pwd = generate_password_hash(admin_pass, method='pbkdf2:sha256')
        admin_obj = Admin(username=admin_user, password_hash=hashed_pwd)
        db.session.add(admin_obj)

    if not SiteConfig.query.first():
        config = SiteConfig()
        db.session.add(config)

    if Metric.query.count() == 0:
        db.session.add_all([
            Metric(value="1st Place", label="FYP 2026 Winner (UlcerGuard)"),
            Metric(value="5+ Apps", label="Production ML Deployments"),
            Metric(value="100%", label="Custom Neural Architectures")
        ])

    if Pillar.query.count() == 0:
        db.session.add_all([
            Pillar(title="Computer Vision & Medical AI",
                   description="YOLOv8, YOLO11, and Mask2Former pipelines for real-time detection and medical image instance segmentation."),
            Pillar(title="Generative AI & LLMs",
                   description="Retrieval-Augmented Generation (RAG) using LangChain & FAISS, fine-tuning Qwen 2.5 with Unsloth PEFT LoRA."),
            Pillar(title="Full-Stack Production ML",
                   description="Modular Flask microservices, Docker containerization, SQLite/PostgreSQL, hosted on cloud platforms."),
            Pillar(title="Agentic Frameworks & Optimization",
                   description="Multi-agent meta-reasoning setups, hyperparameter tuning, and efficient edge model conversion.")
        ])
    db.session.commit()


# --- CONTACT EMAIL API ROUTE ---
@app.route('/api/contact', methods=['POST'])
def handle_contact():
    try:
        name = request.form.get('name')
        sender_email = request.form.get('email')
        message_body = request.form.get('message')

        if not name or not sender_email or not message_body:
            return jsonify({'success': False, 'message': 'All fields are required.'}), 400

        msg = MIMEMultipart()
        # Formatted headers to guarantee direct delivery to primary inbox
        msg['From'] = f"{name} via Portfolio <{MAIL_USERNAME}>"
        msg['To'] = MAIL_USERNAME
        msg['Reply-To'] = sender_email
        msg['Subject'] = f"📥 Portfolio Inquiry: {name}"

        body = f"Sender Name: {name}\nSender Email: {sender_email}\n\nMessage:\n{message_body}"
        msg.attach(MIMEText(body, 'plain'))

        # Connect to Gmail SMTP Server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(MAIL_USERNAME, MAIL_PASSWORD)
        server.send_message(msg)
        server.quit()

        return jsonify({
            'success': True,
            'message': '✓ Your message has been sent to Hammad Ullah! Please be patient for his reply.'
        }), 200

    except Exception as e:
        print("Detailed SMTP Error:", str(e))
        return jsonify({'success': False, 'message': f'SMTP Error: {str(e)}'}), 500


@app.route('/')
def index():
    config = SiteConfig.query.first()
    metrics = Metric.query.all()
    pillars = Pillar.query.all()
    return render_template('index.html', config=config, metrics=metrics, pillars=pillars)


@app.route('/about')
def about():
    config = SiteConfig.query.first()
    skills = Skill.query.all()
    return render_template('about.html', config=config, skills=skills)


@app.route('/projects')
def projects():
    config = SiteConfig.query.first()
    ml_projects = Project.query.filter_by(category='ml').all()
    cv_projects = Project.query.filter_by(category='cv').all()
    nlp_projects = Project.query.filter_by(category='nlp').all()
    genai_projects = Project.query.filter_by(category='genai').all()
    agentic_projects = Project.query.filter_by(category='agentic').all()
    return render_template('projects.html', config=config, ml=ml_projects, cv=cv_projects, nlp=nlp_projects,
                           genai=genai_projects, agentic=agentic_projects)


@app.route('/certifications')
def certifications():
    config = SiteConfig.query.first()
    certs = Certification.query.all()
    return render_template('certifications.html', config=config, certs=certs)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password_hash, password):
            login_user(admin, remember=True)
            return redirect(url_for('dashboard'))
        flash('Invalid credentials!')
    return render_template('login.html')


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    config = SiteConfig.query.first()
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'update_config':
            config.site_title = request.form.get('site_title')
            config.hero_name = request.form.get('hero_name')
            config.hero_subtitle = request.form.get('hero_subtitle')
            config.about_text = request.form.get('about_text')
            db.session.commit()
            flash('General info updated successfully!')

        elif action == 'add_metric':
            value = request.form.get('value')
            label = request.form.get('label')
            if value and label:
                db.session.add(Metric(value=value, label=label))
                db.session.commit()
                flash('Metric added successfully!')

        elif action == 'edit_metric':
            m_id = request.form.get('id')
            m = Metric.query.get(m_id)
            if m:
                m.value = request.form.get('value')
                m.label = request.form.get('label')
                db.session.commit()
                flash('Metric updated successfully!')

        elif action == 'delete_metric':
            m_id = request.form.get('id')
            m = Metric.query.get(m_id)
            if m:
                db.session.delete(m)
                db.session.commit()
                flash('Metric deleted!')

        elif action == 'add_pillar':
            title = request.form.get('title')
            description = request.form.get('description')
            file = request.files.get('image')
            filename = None
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            if title and description:
                db.session.add(Pillar(title=title, description=description, image_filename=filename))
                db.session.commit()
                flash('Engineering Pillar added successfully!')

        elif action == 'edit_pillar':
            p_id = request.form.get('id')
            p = Pillar.query.get(p_id)
            if p:
                p.title = request.form.get('title')
                p.description = request.form.get('description')
                file = request.files.get('image')
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    p.image_filename = filename
                db.session.commit()
                flash('Engineering Pillar updated successfully!')

        elif action == 'delete_pillar':
            p_id = request.form.get('id')
            p = Pillar.query.get(p_id)
            if p:
                db.session.delete(p)
                db.session.commit()
                flash('Pillar deleted!')

        elif action == 'add_project':
            title = request.form.get('title')
            category = request.form.get('category')
            github = request.form.get('github_link')
            live = request.form.get('live_link')
            file = request.files.get('image')

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                new_proj = Project(title=title, category=category, image_filename=filename, github_link=github,
                                   live_link=live)
                db.session.add(new_proj)
                db.session.commit()
                flash('Project added successfully!')

        elif action == 'edit_project':
            p_id = request.form.get('id')
            p = Project.query.get(p_id)
            if p:
                p.title = request.form.get('title')
                p.category = request.form.get('category')
                p.github_link = request.form.get('github_link')
                p.live_link = request.form.get('live_link')
                file = request.files.get('image')
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    p.image_filename = filename
                db.session.commit()
                flash('Project updated successfully!')

        elif action == 'delete_project':
            p_id = request.form.get('id')
            p = Project.query.get(p_id)
            if p:
                db.session.delete(p)
                db.session.commit()
                flash('Project deleted!')

        elif action == 'add_cert':
            title = request.form.get('title')
            file = request.files.get('image')
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                new_cert = Certification(title=title, image_filename=filename)
                db.session.add(new_cert)
                db.session.commit()
                flash('Certification added successfully!')

        elif action == 'edit_cert':
            c_id = request.form.get('id')
            c = Certification.query.get(c_id)
            if c:
                c.title = request.form.get('title')
                file = request.files.get('image')
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    c.image_filename = filename
                db.session.commit()
                flash('Certification updated successfully!')

        elif action == 'delete_cert':
            c_id = request.form.get('id')
            c = Certification.query.get(c_id)
            if c:
                db.session.delete(c)
                db.session.commit()
                flash('Certification deleted!')

        elif action == 'add_skill':
            skill_name = request.form.get('skill_name')
            if skill_name:
                db.session.add(Skill(name=skill_name))
                db.session.commit()
                flash('Skill added successfully!')

        elif action == 'edit_skill':
            s_id = request.form.get('id')
            s = Skill.query.get(s_id)
            if s:
                s.name = request.form.get('skill_name')
                db.session.commit()
                flash('Skill updated successfully!')

        elif action == 'delete_skill':
            s_id = request.form.get('id')
            s = Skill.query.get(s_id)
            if s:
                db.session.delete(s)
                db.session.commit()
                flash('Skill deleted!')

        return redirect(url_for('dashboard'))

    metrics = Metric.query.all()
    pillars = Pillar.query.all()
    projects = Project.query.all()
    certs = Certification.query.all()
    skills = Skill.query.all()
    return render_template('dashboard.html', config=config, metrics=metrics, pillars=pillars, projects=projects,
                           certs=certs, skills=skills)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    is_dev = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=is_dev)