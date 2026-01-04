from flask import Flask, render_template, render_template_string, redirect, url_for, flash, request, jsonify, get_flashed_messages
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
import pymysql
pymysql.install_as_MySQLdb()
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, DecimalField
from wtforms.validators import DataRequired
from config import Config
import subprocess
import os
import stripe
import redis
import logging
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

# --- INICIALIZÁCIA ---
app = Flask(__name__)
app.config.from_object(Config)
app.config['TEMPLATES_AUTO_RELOAD'] = True
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # type: ignore[assignment]

# Vytvor logs adresár ak neexistuje (pred konfiguráciou logovania)
os.makedirs('logs', exist_ok=True)

# Vytvor UPLOAD_FOLDER adresár ak neexistuje (po načítaní konfigurácie)
try:
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
except (OSError, PermissionError) as e:
    # Ak zlyhá vytvorenie adresára, len zaloguj varovanie
    # Aplikácia môže pokračovať, ale upload funkcie nemusia fungovať
    import logging
    logging.warning(f'Nepodarilo sa vytvoriť UPLOAD_FOLDER: {e}')

# Nastavenie logovania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

try:
    redis_client = redis.StrictRedis.from_url(app.config['REDIS_URL'], decode_responses=True)
    redis_client.ping()  # type: ignore[union-attr]
    logger.info("Redis pripojenie úspešné")
except Exception as e:
    logger.warning(f"Redis connection warning: {e}")
    redis_client = None  # type: ignore[assignment]

# --- STRIPE ---
if app.config['STRIPE_SECRET_KEY']:
    stripe.api_key = app.config['STRIPE_SECRET_KEY']

# --- MODELY ---
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    projects = db.relationship('Project', backref='author', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        """Hashuje heslo pomocou werkzeug (pbkdf2 pre Python 3.9 kompatibilitu)"""
        # Použij pbkdf2:sha256 namiesto scrypt pre Python 3.9 kompatibilitu
        self.password = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        """Overí heslo"""
        try:
            return check_password_hash(self.password, password)
        except AttributeError as e:
            # Zachyť chybu ak je heslo hashované pomocou scrypt (nie je podporované v Python 3.9)
            if 'scrypt' in str(e).lower():
                logger.warning(f'Scrypt hash detected for user {self.id}, cannot verify. User needs password reset.')
                return False
            raise
        except Exception as e:
            logger.error(f'Error checking password for user {self.id}: {str(e)}')
            raise

class Project(db.Model):
    __tablename__ = 'projects'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    api_key = db.Column(db.String(120), unique=True, nullable=False)
    script_path = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    payments = db.relationship('Payment', backref='project', lazy=True, cascade='all, delete-orphan')
    automation = db.relationship('Automation', backref='project', lazy=True, cascade='all, delete-orphan')
    ai_requests = db.relationship('AIRequest', backref='project', lazy=True, cascade='all, delete-orphan')

class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='EUR')
    status = db.Column(db.String(20), default='pending')
    gateway = db.Column(db.String(20), nullable=False)
    transaction_id = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Automation(db.Model):
    __tablename__ = 'automation'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    script_name = db.Column(db.String(120), nullable=False)
    schedule = db.Column(db.String(50), nullable=False)
    last_run = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AIRequest(db.Model):
    __tablename__ = 'ai_requests'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    prompt = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CarDeal(db.Model):
    __tablename__ = 'car_deals'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    market_value = db.Column(db.Numeric(10, 2))
    profit = db.Column(db.Numeric(10, 2))
    verdict = db.Column(db.String(20))  # KÚPIŤ, NEKUPOVAŤ, RIZIKO
    risk_level = db.Column(db.String(20))  # Nízke, Stredné, Vysoké
    reason = db.Column(db.Text)
    source = db.Column(db.String(100))  # Bazoš.sk, Autobazar.eu, atď.
    link = db.Column(db.String(500))
    description = db.Column(db.Text)
    image_url = db.Column(db.String(500))
    ai_analysis = db.Column(db.Text)  # JSON s AI analýzou
    is_viewed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    project = db.relationship('Project', backref='car_deals')

# --- FORMULÁRE ---
class LoginForm(FlaskForm):
    username = StringField('Užívateľské meno', validators=[DataRequired()])
    password = PasswordField('Heslo', validators=[DataRequired()])
    submit = SubmitField('Prihlásiť')

class ProjectForm(FlaskForm):
    name = StringField('Názov projektu', validators=[DataRequired()])
    script_path = StringField('Cesta k skriptu (napr. example_script.py)')
    submit = SubmitField('Vytvoriť projekt')

class PaymentForm(FlaskForm):
    amount = DecimalField('Suma', validators=[DataRequired()])
    gateway = SelectField('Platobná brána', choices=[
        ('stripe', 'Stripe'),
        ('sumup', 'SumUp'),
        ('coingate', 'CoinGate (krypto)')
    ])
    submit = SubmitField('Vytvoriť platbu')

class AutomationForm(FlaskForm):
    script_name = StringField('Názov skriptu', validators=[DataRequired()])
    schedule = StringField('Cron rozvrh (napr. 0 3 * * *)', validators=[DataRequired()])
    submit = SubmitField('Pridať automatizáciu')

class AIForm(FlaskForm):
    prompt = TextAreaField('AI prompt', validators=[DataRequired()])
    submit = SubmitField('Generovať')

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Staré heslo', validators=[DataRequired()])
    new_password = PasswordField('Nové heslo', validators=[DataRequired()])
    confirm_password = PasswordField('Potvrď nové heslo', validators=[DataRequired()])
    submit = SubmitField('Zmeniť heslo')

class EditProjectForm(FlaskForm):
    name = StringField('Názov projektu', validators=[DataRequired()])
    script_path = StringField('Cesta k skriptu (napr. example_script.py)')
    is_active = SelectField('Stav', choices=[('True', 'Aktívny'), ('False', 'Neaktívny')], default='True')
    submit = SubmitField('Uložiť zmeny')

# --- LOGIN MANAGER ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- ROUTES ---
@app.route('/')
@login_required
def dashboard():
    """Hlavný dashboard zobrazujúci všetky projekty používateľa"""
    # Rate limiting check pred databázovými dotazmi
    if redis_client:
        try:
            key = f"rate_limit:{request.remote_addr}:dashboard"
            current = redis_client.get(key)
            if current and int(current) >= 60:  # 60 requests per minute
                flash('Príliš veľa požiadavok. Skús to neskôr.', 'warning')
                return redirect(url_for('dashboard')), 429
            redis_client.incr(key)
            redis_client.expire(key, 60)
        except Exception:
            pass  # Ak Redis zlyhá, pokračuj bez rate limiting
    
    # 1. AUTOMATICKÉ VYTVORENIE CARSCRAPER PRO PROJEKTU
    # Preskoč auto-vytváranie počas testov
    carscraper_project = None
    if not app.config.get('TESTING', False):
        carscraper_project = Project.query.filter_by(
            user_id=current_user.id,
            name='CarScraper Pro'
        ).first()
        
        if not carscraper_project:
            try:
                # type: ignore[call-arg]
                carscraper_project = Project(
                    name='CarScraper Pro',  # type: ignore[arg-type]
                    api_key=os.urandom(24).hex(),  # type: ignore[arg-type]
                    user_id=current_user.id,  # type: ignore[arg-type]
                    is_active=True  # type: ignore[arg-type]
                )
                db.session.add(carscraper_project)
                db.session.commit()
                flash('CarScraper Pro projekt bol automaticky vytvorený!', 'info')
                logger.info(f'CarScraper Pro projekt vytvorený pre používateľa {current_user.id}')
            except Exception as e:
                logger.error(f'Chyba pri vytváraní CarScraper Pro projektu: {e}')
                db.session.rollback()
                carscraper_project = None
    
    # Paginácia
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '', type=str)
    
    # Vyhľadávanie
    query = Project.query.filter_by(user_id=current_user.id)
    if search:
        query = query.filter(Project.name.contains(search))
    
    # Zoradenie a paginácia
    projects = query.order_by(Project.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Štatistiky
    total_projects = Project.query.filter_by(user_id=current_user.id).count()
    active_projects = Project.query.filter_by(user_id=current_user.id, is_active=True).count()
    total_payments = Payment.query.join(Project).filter(Project.user_id == current_user.id).count()
    total_automations = Automation.query.join(Project).filter(Project.user_id == current_user.id).count()
    
    # CarScraper Pro štatistiky
    carscraper_stats = None
    carscraper_top_deals = []
    
    if carscraper_project:
        try:
            total_deals = CarDeal.query.filter_by(project_id=carscraper_project.id).count()
            good_deals = CarDeal.query.filter_by(project_id=carscraper_project.id, verdict='KÚPIŤ').count()
            from sqlalchemy import func
            total_profit_result = db.session.query(func.sum(CarDeal.profit)).filter(
                CarDeal.project_id == carscraper_project.id,
                CarDeal.verdict == 'KÚPIŤ'
            ).scalar()
            total_profit = float(total_profit_result) if total_profit_result else 0.0
            
            carscraper_stats = {
                'total_deals': total_deals,
                'good_deals': good_deals,
                'total_profit': total_profit,
                'success_rate': round((good_deals / total_deals * 100) if total_deals > 0 else 0, 2)
            }
            
            # Top 5 deals (najnovšie, verdict='KÚPIŤ')
            carscraper_top_deals = CarDeal.query.filter_by(
                project_id=carscraper_project.id,
                verdict='KÚPIŤ'
            ).order_by(CarDeal.created_at.desc()).limit(5).all()
        except Exception as e:
            logger.error(f'Chyba pri získavaní CarScraper štatistík: {e}')
    
    stats = {
        'total_projects': total_projects,
        'active_projects': active_projects,
        'total_payments': total_payments,
        'total_automations': total_automations
    }
    
    return render_template(
        'dashboard.html',
        projects=projects,
        stats=stats,
        search=search,
        carscraper_project=carscraper_project,
        carscraper_stats=carscraper_stats,
        carscraper_top_deals=carscraper_top_deals
    )

@app.route('/projects', methods=['GET', 'POST'])
@login_required
def projects():
    """Správa projektov - vytvorenie nového projektu"""
    form = ProjectForm()
    if form.validate_on_submit():
        # type: ignore[call-arg]
        new_project = Project(
            name=form.name.data,  # type: ignore[arg-type]
            api_key=os.urandom(24).hex(),  # type: ignore[arg-type]
            script_path=form.script_path.data,  # type: ignore[arg-type]
            user_id=current_user.id  # type: ignore[arg-type]
        )
        db.session.add(new_project)
        db.session.commit()
        flash('Projekt bol pridaný!', 'success')
        return redirect(url_for('projects'))

    user_projects = Project.query.filter_by(user_id=current_user.id).all()
    return render_template('projects/projects.html', form=form, projects=user_projects)

@app.route('/run_script/<int:project_id>')
@login_required
def run_script(project_id):
    """Spustenie skriptu priradeného k projektu"""
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        flash('Nemáš oprávnenie!', 'danger')
        return redirect(url_for('dashboard'))

    if project.script_path:
        script_full_path = os.path.join(app.config['UPLOAD_FOLDER'], project.script_path)
        if os.path.exists(script_full_path):
            try:
                subprocess.Popen(['python3', script_full_path])
                logger.info(f'Skript spustený: {script_full_path} pre projekt {project.name}')
                flash(f'Skript {project.name} beží!', 'success')
            except Exception as e:
                logger.error(f'Chyba pri spustení skriptu {script_full_path}: {str(e)}', exc_info=True)
                flash(f'Chyba: {str(e)}', 'danger')
        else:
            flash(f'Skript nebol nájdený: {script_full_path}', 'warning')
    else:
        flash('Projekt nemá priradený skript!', 'warning')

    return redirect(url_for('dashboard'))

@app.route('/payments/<int:project_id>', methods=['GET', 'POST'])
@login_required
def payments(project_id):
    """Správa platieb pre projekt"""
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        flash('Nemáš oprávnenie!', 'danger')
        return redirect(url_for('dashboard'))

    form = PaymentForm()
    if form.validate_on_submit():
        if form.gateway.data == 'stripe':
            if not app.config['STRIPE_SECRET_KEY']:
                flash('Stripe nie je nakonfigurovaný!', 'danger')
                return redirect(url_for('payments', project_id=project_id))

            try:
                # Vytvor platobný intent
                amount_value = form.amount.data
                if amount_value is None:
                    flash('Neplatná suma!', 'danger')
                    return redirect(url_for('payments', project_id=project_id))
                intent = stripe.PaymentIntent.create(
                    amount=int(float(amount_value) * 100),  # Stripe počíta v centoch
                    currency='eur',
                    metadata={'project_id': project_id}
                )
                # type: ignore[call-arg]
                new_payment = Payment(
                    project_id=project_id,  # type: ignore[arg-type]
                    amount=amount_value,  # type: ignore[arg-type]
                    gateway='stripe',  # type: ignore[arg-type]
                    transaction_id=intent.id  # type: ignore[arg-type]
                )
                db.session.add(new_payment)
                db.session.commit()
                return render_template('payments/stripe.html',
                                     client_secret=intent.client_secret,
                                     STRIPE_PUBLIC_KEY=app.config['STRIPE_PUBLIC_KEY'])
            except Exception as e:
                logger.error(f'Stripe chyba pre projekt {project_id}: {str(e)}', exc_info=True)
                flash(f'Chyba Stripe: {str(e)}', 'danger')

        elif form.gateway.data == 'sumup':
            flash('SumUp integrácia nie je ešte implementovaná', 'info')

        elif form.gateway.data == 'coingate':
            flash('CoinGate integrácia nie je ešte implementovaná', 'info')

    return render_template('payments/payments.html', form=form, project=project)

@app.route('/automation/<int:project_id>', methods=['GET', 'POST'])
@login_required
def automation(project_id):
    """Správa automatizácií pre projekt"""
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        flash('Nemáš oprávnenie!', 'danger')
        return redirect(url_for('dashboard'))

    form = AutomationForm()
    if form.validate_on_submit():
        # type: ignore[call-arg]
        new_automation = Automation(
            project_id=project_id,  # type: ignore[arg-type]
            script_name=form.script_name.data,  # type: ignore[arg-type]
            schedule=form.schedule.data  # type: ignore[arg-type]
        )
        db.session.add(new_automation)
        db.session.commit()
        flash('Automatizácia bola pridaná!', 'success')
        return redirect(url_for('automation', project_id=project_id))

    automations = Automation.query.filter_by(project_id=project_id).all()
    return render_template('automation/automation.html', form=form, automations=automations, project=project)

@app.route('/ai/<int:project_id>', methods=['GET', 'POST'])
@login_required
def ai(project_id):
    """AI generátor pre projekt"""
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        flash('Nemáš oprávnenie!', 'danger')
        return redirect(url_for('dashboard'))

    form = AIForm()
    if form.validate_on_submit():
        if not app.config['OPENAI_API_KEY']:
            flash('OpenAI API nie je nakonfigurované!', 'danger')
            return redirect(url_for('ai', project_id=project_id))

        try:
            # Použitie novšej OpenAI API (verzia 1.x)
            import httpx
            from openai import OpenAI

            # Vytvor httpx klienta s trust_env=False aby sa vyhol proxy problémom
            http_client = httpx.Client(trust_env=False)
            client = OpenAI(api_key=app.config['OPENAI_API_KEY'], http_client=http_client)

            prompt_content = form.prompt.data or ""
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": prompt_content}
                ],
                max_tokens=200
            )

            ai_response = response.choices[0].message.content

            # type: ignore[call-arg]
            ai_request = AIRequest(
                project_id=project_id,  # type: ignore[arg-type]
                prompt=prompt_content,  # type: ignore[arg-type]
                response=ai_response  # type: ignore[arg-type]
            )
            db.session.add(ai_request)
            db.session.commit()
            flash('AI odpoveď bola vygenerovaná!', 'success')
        except Exception as e:
            logger.error(f'AI generovanie zlyhalo pre projekt {project_id}: {str(e)}', exc_info=True)
            flash(f'Chyba AI: {str(e)}', 'danger')

    ai_requests = AIRequest.query.filter_by(project_id=project_id).order_by(AIRequest.created_at.desc()).limit(10).all()
    return render_template('ai/ai.html', form=form, ai_requests=ai_requests, project=project)

# --- AUTENTIFIKÁCIA ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Prihlásenie používateľa"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username and password:
            try:
                user = User.query.filter_by(username=username).first()

                # Kontrola hesla
                if user:
                    # Skontroluj hashované heslo
                    if user.check_password(password):
                        login_user(user)
                        flash('Úspešne prihlásený!', 'success')
                        return redirect(url_for('dashboard'))
            except Exception as e:
                logger.error(f'Login error: {str(e)}', exc_info=True)
                flash('Chyba pri prihlásení. Skús to znova.', 'danger')
                return redirect(url_for('login'))

            flash('Nesprávne prihlasovacie údaje!', 'danger')
            return redirect(url_for('login'))

    return render_template_string('''
<!DOCTYPE html>
<html lang="sk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Prihlásenie - API Dashboard</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.1);
            width: 100%;
            max-width: 400px;
        }
        .logo {
            text-align: center;
            font-size: 48px;
            color: #667eea;
            margin-bottom: 20px;
        }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 10px;
            font-size: 24px;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 500;
        }
        input[type="text"], input[type="password"] {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            font-size: 16px;
            box-sizing: border-box;
            transition: border-color 0.3s ease;
        }
        input[type="text"]:focus, input[type="password"]:focus {
            outline: none;
            border-color: #667eea;
        }
        .input-group {
            position: relative;
        }
        .input-icon {
            position: absolute;
            right: 15px;
            top: 50%;
            transform: translateY(-50%);
            color: #999;
            font-size: 18px;
        }
        .btn {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s ease;
        }
        .btn:hover {
            transform: translateY(-2px);
        }
        .alert {
            padding: 15px;
            background: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 8px;
            margin-top: 20px;
            color: #155724;
        }
        .alert strong {
            display: block;
            margin-bottom: 8px;
            color: #0f5132;
        }
        code {
            background: #f8f9fa;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: monospace;
        }
        .error {
            padding: 15px;
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            border-radius: 8px;
            margin-bottom: 20px;
            color: #721c24;
        }
        .success {
            padding: 15px;
            background: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 8px;
            margin-bottom: 20px;
            color: #155724;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🚀</div>
        <h1>API Dashboard</h1>
        <p class="subtitle">Prihlás sa do svojho účtu</p>

        {% if error %}
        <div class="error">
            {{ error }}
        </div>
        {% endif %}

        {% if success %}
        <div class="success">
            {{ success }}
        </div>
        {% endif %}

        <form method="POST">
            <div class="form-group">
                <label for="username">Užívateľské meno</label>
                <div class="input-group">
                    <input type="text" id="username" name="username" placeholder="Zadaj používateľské meno" required value="{{ username or '' }}">
                    <span class="input-icon">👤</span>
                </div>
            </div>

            <div class="form-group">
                <label for="password">Heslo</label>
                <div class="input-group">
                    <input type="password" id="password" name="password" placeholder="Zadaj heslo" required>
                    <span class="input-icon">🔒</span>
                </div>
            </div>

            <button type="submit" class="btn">Prihlásiť</button>
        </form>

        <div class="alert">
            <strong>Predvolené prihlasovacie údaje:</strong><br>
            Užívateľ: <code>admin</code><br>
            Heslo: <code>admin123</code><br>
            <em>Zmeň heslo po prvom prihlásení!</em>
        </div>
    </div>
</body>
</html>
''', error=get_flashed_messages(category_filter=['danger']), success=get_flashed_messages(category_filter=['success']), username=request.form.get('username', ''))

@app.route('/logout')
@login_required
def logout():
    """Odhlásenie používateľa"""
    logout_user()
    flash('Bol si odhlásený!', 'info')
    return redirect(url_for('login'))

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Nastavenia používateľa - zmena hesla"""
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.old_password.data):
            flash('Staré heslo je nesprávne!', 'danger')
            return redirect(url_for('settings'))
        
        new_password = form.new_password.data
        if not new_password or new_password != form.confirm_password.data:
            flash('Nové heslá sa nezhodujú!', 'danger')
            return redirect(url_for('settings'))
        
        if len(new_password) < 6:
            flash('Nové heslo musí mať aspoň 6 znakov!', 'danger')
            return redirect(url_for('settings'))
        
        current_user.set_password(new_password)
        db.session.commit()
        logger.info(f'User {current_user.id} changed password')
        flash('Heslo bolo úspešne zmenené!', 'success')
        return redirect(url_for('settings'))
    
    return render_template('settings.html', form=form)

@app.route('/projects/<int:project_id>/delete', methods=['POST'])
@login_required
def delete_project(project_id):
    """Vymazanie projektu"""
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        flash('Nemáš oprávnenie!', 'danger')
        return redirect(url_for('dashboard'))
    
    project_name = project.name
    db.session.delete(project)
    db.session.commit()
    logger.info(f'Project {project_id} ({project_name}) deleted by user {current_user.id}')
    flash(f'Projekt "{project_name}" bol vymazaný!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/projects/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    """Editácia projektu"""
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        flash('Nemáš oprávnenie!', 'danger')
        return redirect(url_for('dashboard'))
    
    form = EditProjectForm(obj=project)
    form.is_active.data = 'True' if project.is_active else 'False'
    
    if form.validate_on_submit():
        try:
            project.name = form.name.data
            project.script_path = form.script_path.data
            project.is_active = form.is_active.data == 'True'
            db.session.commit()
            logger.info(f'Project {project_id} edited by user {current_user.id}')
            flash('Projekt bol úspešne upravený!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            logger.error(f'Error editing project {project_id}: {str(e)}', exc_info=True)
            db.session.rollback()
            flash('Chyba pri ukladaní zmien. Skús to znova.', 'danger')
    
    return render_template('projects/edit_project.html', form=form, project=project)

@app.route('/projects/<int:project_id>/regenerate-key', methods=['POST'])
@login_required
def regenerate_api_key(project_id):
    """Regenerácia API kľúča projektu"""
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        flash('Nemáš oprávnenie!', 'danger')
        return redirect(url_for('dashboard'))
    
    # old_key = project.api_key  # Uložené pre logovanie ak by bolo potrebné
    project.api_key = os.urandom(24).hex()
    db.session.commit()
    logger.info(f'API key regenerated for project {project_id} by user {current_user.id}')
    flash(f'API kľúč bol regenerovaný! Nový kľúč: {project.api_key}', 'success')
    return redirect(url_for('dashboard'))

@app.route('/export/projects')
@login_required
def export_projects():
    """Export projektov do JSON"""
    projects = Project.query.filter_by(user_id=current_user.id).all()
    data = [{
        'id': p.id,
        'name': p.name,
        'api_key': p.api_key,
        'script_path': p.script_path,
        'is_active': p.is_active,
        'created_at': p.created_at.isoformat()
    } for p in projects]
    
    from flask import Response
    import json
    return Response(
        json.dumps(data, indent=2, ensure_ascii=False),
        mimetype='application/json',
        headers={'Content-Disposition': 'attachment; filename=projects.json'}
    )

@app.route('/export/payments')
@login_required
def export_payments():
    """Export platieb do CSV"""
    payments = Payment.query.join(Project).filter(Project.user_id == current_user.id).all()
    
    import csv
    from io import StringIO
    from flask import Response
    
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Projekt', 'Suma', 'Mena', 'Status', 'Brána', 'Dátum'])
    
    for payment in payments:
        writer.writerow([
            payment.id,
            payment.project.name,
            payment.amount,
            payment.currency,
            payment.status,
            payment.gateway,
            payment.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=payments.csv'}
    )

@app.route('/favicon.ico')
def favicon():
    """Serve favicon from root path"""
    from flask import send_from_directory
    static_folder = app.static_folder
    if static_folder is None:
        return '', 404
    return send_from_directory(static_folder, 'favicon.ico', mimetype='image/x-icon')

@app.route('/carscraper')
@app.route('/carscraper/<path:path>')
def carscraper_frontend(path='index.html'):
    """Serve CarScraper Pro React frontend"""
    from flask import send_from_directory
    static_folder = app.static_folder
    if static_folder is None:
        return redirect(url_for('dashboard'))
    frontend_dir = os.path.join(static_folder, 'carscraper')
    if not os.path.exists(frontend_dir):
        return redirect(url_for('dashboard'))
    return send_from_directory(frontend_dir, path)

# Health endpoints sú definované nižšie (lines 1005-1047)
# Táto duplicitná definícia bola odstránená aby sa predišlo konfliktu

# Debug route len pre development
@app.route('/debug')
def debug():
    """Debug page to test if Flask is working (len v development režime)"""
    if not app.config.get('FLASK_DEBUG', False):
        return redirect(url_for('login'))
    
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>DEBUG - Flask is working!</title>
        <style>
            body { font-family: Arial; padding: 20px; background: #f0f0f0; }
            .box { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .success { color: green; font-size: 24px; }
            .time { color: #666; font-size: 14px; }
        </style>
    </head>
    <body>
        <div class="box">
            <h1 class="success">✅ FLASK IS WORKING!</h1>
            <p>This page proves that your Flask application is running correctly.</p>
            <p><strong>Server time:</strong> <span class="time" id="time"></span></p>
            <p><strong>Port:</strong> 6002</p>
            <p><strong>Status:</strong> Active</p>
            <p><strong>Mode:</strong> Development (DEBUG enabled)</p>
            <br>
            <a href="/login" style="background: blue; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;">Go to Login</a>
        </div>
        <script>
            document.getElementById('time').textContent = new Date().toLocaleString();
        </script>
    </body>
    </html>
    '''

# --- RATE LIMITING ---
def rate_limit(max_per_minute=60):
    """Jednoduchý rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if redis_client:
                key = f"rate_limit:{request.remote_addr}:{f.__name__}"
                current = redis_client.get(key)
                
                if current and int(current) >= max_per_minute:
                    return jsonify({
                        'error': 'Rate limit exceeded',
                        'message': f'Maximum {max_per_minute} requests per minute allowed'
                    }), 429
                
                pipe = redis_client.pipeline()
                pipe.incr(key)
                pipe.expire(key, 60)  # 60 sekúnd
                pipe.execute()
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# --- API DOCUMENTATION ---
@app.route('/api/docs', methods=['GET'])
def api_docs():
    """API dokumentácia endpoint"""
    docs = {
        'title': 'VPS Dashboard API Documentation',
        'version': '1.0.0',
        'base_url': request.url_root.rstrip('/'),
        'endpoints': {
            'GET /api/health': {
                'description': 'Health check endpoint pre monitoring',
                'authentication': False,
                'response': {
                    'status': 'healthy|degraded',
                    'timestamp': 'ISO datetime',
                    'services': {
                        'database': 'status',
                        'redis': 'status',
                        'stripe': 'status',
                        'openai': 'status'
                    }
                }
            },
            'GET /api/projects': {
                'description': 'Získanie zoznamu projektov používateľa',
                'authentication': True,
                'response': [{
                    'id': 'integer',
                    'name': 'string',
                    'api_key': 'string',
                    'is_active': 'boolean',
                    'created_at': 'ISO datetime'
                }]
            },
            'GET /api/project/<id>': {
                'description': 'Získanie detailu projektu',
                'authentication': True,
                'parameters': {
                    'id': 'integer - ID projektu'
                },
                'response': {
                    'id': 'integer',
                    'name': 'string',
                    'api_key': 'string',
                    'is_active': 'boolean',
                    'script_path': 'string',
                    'created_at': 'ISO datetime',
                    'payments_count': 'integer',
                    'automations_count': 'integer'
                }
            }
        },
        'rate_limiting': {
            'description': 'API endpointy majú rate limiting 60 požiadavok za minútu',
            'headers': {
                'X-RateLimit-Limit': '60',
                'X-RateLimit-Remaining': 'počet zostávajúcich požiadavok'
            }
        },
        'authentication': {
            'description': 'Používa Flask-Login session cookies',
            'required': 'Pre väčšinu endpointov je potrebné prihlásenie'
        }
    }
    return jsonify(docs)

# --- HEALTH CHECK ---
@app.route('/health', methods=['GET'])
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint pre monitoring"""
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'services': {}
    }
    
    # Kontrola databázy
    try:
        db.session.execute(text('SELECT 1'))
        health_status['services']['database'] = 'connected'
    except Exception as e:
        health_status['status'] = 'degraded'
        health_status['services']['database'] = f'error: {str(e)}'
    
    # Kontrola Redis
    if redis_client:
        try:
            redis_client.ping()
            health_status['services']['redis'] = 'connected'
        except Exception as e:
            health_status['services']['redis'] = f'error: {str(e)}'
    else:
        health_status['services']['redis'] = 'not configured'
    
    # Kontrola Stripe
    if app.config.get('STRIPE_SECRET_KEY'):
        health_status['services']['stripe'] = 'configured'
    else:
        health_status['services']['stripe'] = 'not configured'
    
    # Kontrola OpenAI
    if app.config.get('OPENAI_API_KEY'):
        health_status['services']['openai'] = 'configured'
    else:
        health_status['services']['openai'] = 'not configured'
    
    # Vráť 200 pre healthy aj degraded (monitoring systémy očakávajú 200)
    # 503 len ak je kritická chyba (napr. databáza úplne nefunguje)
    status_code = 200
    if health_status['status'] == 'degraded' and health_status['services'].get('database', '').startswith('error'):
        status_code = 503
    return jsonify(health_status), status_code

# --- API ENDPOINTS ---
@app.route('/api/projects', methods=['GET'])
@login_required
@rate_limit(max_per_minute=60)
def api_projects():
    """API endpoint pre zoznam projektov"""
    projects = Project.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': project.id,
        'name': project.name,
        'api_key': project.api_key,
        'is_active': project.is_active,
        'created_at': project.created_at.isoformat()
    } for project in projects])

@app.route('/api/project/<int:project_id>', methods=['GET'])
@login_required
@rate_limit(max_per_minute=60)
def api_project_detail(project_id):
    """API endpoint pre detail projektu"""
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    # Použijeme efektívne počítanie pomocou query namiesto len() na relationship
    payments_count = db.session.query(Payment).filter_by(project_id=project.id).count()
    automations_count = db.session.query(Automation).filter_by(project_id=project.id).count()
    
    return jsonify({
        'id': project.id,
        'name': project.name,
        'api_key': project.api_key,
        'is_active': project.is_active,
        'script_path': project.script_path,
        'created_at': project.created_at.isoformat(),
        'payments_count': payments_count,
        'automations_count': automations_count
    })

# --- CARSCRAPER PRO API ---
@app.route('/api/carscraper/deals', methods=['GET'])
@login_required
@rate_limit(max_per_minute=60)
def get_car_deals():
    """Získanie zoznamu car deals pre používateľa"""
    try:
        project = Project.query.filter_by(user_id=current_user.id, name='CarScraper Pro').first()
        if not project:
            return jsonify({'error': 'CarScraper Pro projekt nebol nájdený'}), 404
        
        # Filtre
        verdict = request.args.get('verdict')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        query = CarDeal.query.filter_by(project_id=project.id)
        
        if verdict:
            query = query.filter_by(verdict=verdict)
        
        deals = query.order_by(CarDeal.created_at.desc()).limit(limit).offset(offset).all()
        
        return jsonify({
            'deals': [{
                'id': deal.id,
                'title': deal.title,
                'price': float(deal.price),
                'market_value': float(deal.market_value) if deal.market_value else None,
                'profit': float(deal.profit) if deal.profit else None,
                'verdict': deal.verdict,
                'risk_level': deal.risk_level,
                'reason': deal.reason,
                'source': deal.source,
                'link': deal.link,
                'image_url': deal.image_url,
                'description': deal.description,
                'is_viewed': deal.is_viewed,
                'created_at': deal.created_at.isoformat() if deal.created_at else None
            } for deal in deals],
            'total': query.count(),
            'limit': limit,
            'offset': offset
        })
    except Exception as e:
        logger.error(f"Error getting car deals: {e}")
        return jsonify({'error': 'Chyba pri získavaní deals'}), 500

@app.route('/api/carscraper/deals/<int:deal_id>', methods=['GET'])
@login_required
@rate_limit(max_per_minute=60)
def get_car_deal(deal_id):
    """Získanie detailu car deal"""
    try:
        project = Project.query.filter_by(user_id=current_user.id, name='CarScraper Pro').first()
        if not project:
            return jsonify({'error': 'CarScraper Pro projekt nebol nájdený'}), 404
        
        deal = CarDeal.query.filter_by(id=deal_id, project_id=project.id).first()
        if not deal:
            return jsonify({'error': 'Deal nebol nájdený'}), 404
        
        # Označ ako videný
        deal.is_viewed = True
        db.session.commit()
        
        return jsonify({
            'id': deal.id,
            'title': deal.title,
            'price': float(deal.price),
            'market_value': float(deal.market_value) if deal.market_value else None,
            'profit': float(deal.profit) if deal.profit else None,
            'verdict': deal.verdict,
            'risk_level': deal.risk_level,
            'reason': deal.reason,
            'source': deal.source,
            'link': deal.link,
            'image_url': deal.image_url,
            'description': deal.description,
            'ai_analysis': deal.ai_analysis,
            'is_viewed': deal.is_viewed,
            'created_at': deal.created_at.isoformat() if deal.created_at else None
        })
    except Exception as e:
        logger.error(f"Error getting car deal: {e}")
        return jsonify({'error': 'Chyba pri získavaní deal'}), 500

@app.route('/api/carscraper/stats', methods=['GET'])
@login_required
@rate_limit(max_per_minute=60)
def get_carscraper_stats():
    """Získanie štatistík CarScraper Pro"""
    try:
        project = Project.query.filter_by(user_id=current_user.id, name='CarScraper Pro').first()
        if not project:
            return jsonify({'error': 'CarScraper Pro projekt nebol nájdený'}), 404
        
        total_deals = CarDeal.query.filter_by(project_id=project.id).count()
        good_deals = CarDeal.query.filter_by(project_id=project.id, verdict='KÚPIŤ').count()
        from sqlalchemy import func
        total_profit_result = db.session.query(func.sum(CarDeal.profit)).filter(
            CarDeal.project_id == project.id,
            CarDeal.verdict == 'KÚPIŤ'
        ).scalar()
        total_profit = float(total_profit_result) if total_profit_result else 0.0
        
        return jsonify({
            'total_deals': total_deals,
            'good_deals': good_deals,
            'total_profit': float(total_profit),
            'success_rate': round((good_deals / total_deals * 100) if total_deals > 0 else 0, 2)
        })
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({'error': 'Chyba pri získavaní štatistík'}), 500

@app.route('/api/carscraper/scrape', methods=['POST'])
@login_required
@rate_limit(max_per_minute=10)
def run_carscraper_scraping():
    """Manuálne spustenie scraping pre CarScraper Pro"""
    try:
        project = Project.query.filter_by(user_id=current_user.id, name='CarScraper Pro').first()
        if not project:
            return jsonify({'error': 'CarScraper Pro projekt nebol nájdený'}), 404
        
        if not project.is_active:
            return jsonify({'error': 'CarScraper Pro projekt nie je aktívny'}), 400
        
        # Import scraping funkcií
        import sys
        scripts_dir = os.path.join(os.path.dirname(__file__), 'scripts')
        if scripts_dir not in sys.path:
            sys.path.insert(0, scripts_dir)
        
        from car_scraper import scrape_bazos, save_deals_to_db
        
        # Spusti scraping
        logger.info(f'Spúšťam scraping pre používateľa {current_user.id}')
        listings = scrape_bazos()
        
        if not listings:
            return jsonify({
                'status': 'warning',
                'message': 'Žiadne inzeráty na spracovanie',
                'deals_found': 0,
                'deals_saved': 0
            })
        
        # Ulož deals
        saved_count = save_deals_to_db(listings, project.id)
        
        logger.info(f'Scraping dokončený: {len(listings)} nájdených, {saved_count} uložených')
        
        return jsonify({
            'status': 'success',
            'message': f'Scraping dokončený úspešne',
            'deals_found': len(listings),
            'deals_saved': saved_count
        })
    except Exception as e:
        logger.error(f'Chyba pri scraping: {e}', exc_info=True)
        return jsonify({'error': f'Chyba pri scraping: {str(e)}'}), 500

@app.route('/carscraper/run-scraping', methods=['GET'])
@login_required
def carscraper_run_scraping_page():
    """Stránka pre manuálne spustenie scraping"""
    project = Project.query.filter_by(user_id=current_user.id, name='CarScraper Pro').first()
    if not project:
        flash('CarScraper Pro projekt nebol nájdený', 'danger')
        return redirect(url_for('dashboard'))
    
    return render_template('carscraper/run_scraping.html', project=project)

# --- ERROR HANDLERS ---
@app.errorhandler(404)
def not_found_error(error):
    logger.warning(f'404 error: {request.url}')
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Not found', 'message': 'Endpoint nebol nájdený'}), 404
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    logger.error(f'500 error: {str(error)}', exc_info=True)
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Internal server error', 'message': 'Nastala chyba na serveri'}), 500
    return render_template('errors/500.html'), 500

@app.errorhandler(403)
def forbidden_error(error):
    logger.warning(f'403 error: {request.url} by user {current_user.id if current_user.is_authenticated else "anonymous"}')
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Forbidden', 'message': 'Nemáš oprávnenie'}), 403
    flash('Nemáš oprávnenie na prístup k tejto stránke!', 'danger')
    return redirect(url_for('dashboard') if current_user.is_authenticated else url_for('login')), 403

@app.errorhandler(429)
def rate_limit_error(error):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Rate limit exceeded', 'message': 'Príliš veľa požiadavok'}), 429
    flash('Príliš veľa požiadavok. Skús to neskôr.', 'warning')
    return redirect(request.referrer or url_for('dashboard')), 429

# --- AUTOMATICKÉ SCRAPING (Background Task) ---
def auto_scrape_carscraper():
    """Automatické spustenie scraping každých 60 sekúnd"""
    # Preskoč počas testov
    if app.config.get('TESTING', False):
        return
    
    try:
        with app.app_context():
            # Nájdeme všetky aktívne CarScraper Pro projekty
            projects = Project.query.filter_by(name='CarScraper Pro', is_active=True).all()
            
            if not projects:
                logger.info('Žiadne aktívne CarScraper Pro projekty na scraping')
                return
            
            # Import scraping funkcií
            import sys
            scripts_dir = os.path.join(os.path.dirname(__file__), 'scripts')
            if scripts_dir not in sys.path:
                sys.path.insert(0, scripts_dir)
            
            from car_scraper import scrape_bazos, save_deals_to_db
            
            # Obnov proxy pool každých 10 scrapingov (každých ~10 minút)
            if not hasattr(auto_scrape_carscraper, '_scrape_count'):
                auto_scrape_carscraper._scrape_count = 0
            
            auto_scrape_carscraper._scrape_count += 1
            if auto_scrape_carscraper._scrape_count % 10 == 0:
                try:
                    from utils.proxy_manager import get_proxy_manager
                    proxy_manager = get_proxy_manager()
                    proxy_manager.refresh_proxy_pool()
                    logger.info('🔄 Proxy pool automaticky obnovený')
                except Exception as e:
                    logger.debug(f'Chyba pri obnovovaní proxy pool: {e}')
            
            for project in projects:
                try:
                    logger.info(f'Automatický scraping pre projekt {project.id} (používateľ {project.user_id})')
                    listings = scrape_bazos()
                    
                    if listings:
                        saved = save_deals_to_db(listings, project.id)
                        logger.info(f'Automatický scraping dokončený: {len(listings)} nájdených, {saved} uložených pre projekt {project.id}')
                    else:
                        logger.info(f'Žiadne inzeráty nájdené pre projekt {project.id}')
                except Exception as e:
                    logger.error(f'Chyba pri automatickom scraping pre projekt {project.id}: {e}', exc_info=True)
    except Exception as e:
        logger.error(f'Chyba pri automatickom scraping: {e}', exc_info=True)

# Spusti background thread pre automatické scraping
import threading
import time

def background_scraper():
    """Background thread pre automatické scraping každých 60 sekúnd"""
    # Počkaj 10 sekúnd po štarte (aby sa server spustil)
    time.sleep(10)
    
    while True:
        try:
            auto_scrape_carscraper()
            time.sleep(60)  # 60 sekúnd (1 minúta)
        except Exception as e:
            logger.error(f'Chyba v background scraper thread: {e}', exc_info=True)
            time.sleep(60)  # Počkaj minútu pred ďalším pokusom

# Spusti background thread len ak nie sme v testovacom režime
if not os.environ.get('TESTING'):
    scraper_thread = threading.Thread(target=background_scraper, daemon=True)
    scraper_thread.start()
    logger.info('✅ Background scraper thread spustený (každých 60 sekúnd)')
    
    # Spusti proxy refresher (automatické obnovovanie free proxy každých 30 minút)
    try:
        from utils.proxy_manager import get_proxy_manager
        from utils.proxy_refresher import start_proxy_refresher
        proxy_manager = get_proxy_manager()
        start_proxy_refresher(proxy_manager, interval_minutes=30)
        logger.info('✅ Proxy refresher spustený (obnovovanie každých 30 minút)')
    except Exception as e:
        logger.debug(f'Proxy refresher nie je dostupný: {e}')

# --- INICIALIZÁCIA ---
if __name__ == '__main__':
    try:
        with app.app_context():
            db.create_all()
            logger.info("✅ Databáza bola inicializovaná!")
    except Exception as e:
        logger.error(f"❌ Chyba databázy: {e}")
        logger.warning("🚀 Spúšťam server bez databázy...")

    port = app.config.get('PORT', 6002)
    debug_value = app.config.get('FLASK_DEBUG', False)
    # Explicitne konvertuj na bool pre type checker
    if isinstance(debug_value, bool):
        debug_bool: bool = debug_value
    elif isinstance(debug_value, str):
        debug_bool = debug_value.lower() in ('true', '1', 'yes', 'on')
    else:
        debug_bool = bool(debug_value)
    logger.info(f"🚀 Server beží na http://0.0.0.0:{port}")
    logger.info(f"📝 Debug mode: {debug_bool}")
    app.run(host='0.0.0.0', port=port, debug=debug_bool)
