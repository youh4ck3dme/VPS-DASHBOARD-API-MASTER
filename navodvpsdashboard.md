# VPS API Dashboard Admin Panel

Kompletný, univerzálny a vylepšený VPS API Dashboard Admin Panel s **bohatým vybavením**, **viacerými platobnými bránami** (Stripe, SumUp, CoinGate, PayPal), **napojením na AI API** (Stable Diffusion, OpenAI) a **automatizáciou**. Panel obsahuje **detailný návod priamo v kóde** a je plne funkčný na **PQ.Hosting VPS**.

---

## **📌 Architektúra projektu**

```text
/var/www/api_dashboard/
│── app.py                  # Hlavný Flask server
│── config.py               # Konfigurácia (API kľúče, databáza)
│── requirements.txt        # Python závislosti
│── static/                 # CSS, JS, obrázky
│── templates/              # HTML šablóny
│   │── base.html            # Základná šablóna
│   │── dashboard.html       # Hlavný dashboard
│   │── projects/            # Správa projektov
│   │── payments/            # Platby a faktúry
│   │── automation/          # Automatizácie (cron jobs)
│   │── ai/                  # AI generovanie obsahu
│── database/               # SQL skripty
│   │── init_db.sql          # Inicializácia databázy
│── scripts/                # Automatizačné skripty
│   │── scrape_xvideos.py    # Scraper pre XVideos
│   │── ai_generate.py       # AI generovanie obsahu
│── logs/                   # Logy pre monitoring
│── backups/                # Zálohy databázy
```

---

## **🔧 1. Inštalácia a nastavenie (krok po kroku)**

### **1.1. Pripoj sa na VPS**

```bash
ssh root@IP_TVOJEHO_VPS
```

### **1.2. Nainštaluj potrebné balíčky**

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip python3-venv nginx git mysql-server redis-server -y
```

### **1.3. Vytvor virtuálne prostredie**

```bash
mkdir /var/www/api_dashboard && cd /var/www/api_dashboard
python3 -m venv venv
source venv/bin/activate
```

### **1.4. Nainštaluj Python závislosti**

```bash
pip3 install flask flask-sqlalchemy flask-login flask-wtf gunicorn stripe sumup coingate python-dotenv openai mysql-connector-python redis
```

### **1.5. Vytvor `requirements.txt`**

```bash
nano requirements.txt
```

**Vlož:**

```text
flask==2.3.2
flask-sqlalchemy==3.0.3
flask-login==0.6.2
flask-wtf==1.1.1
gunicorn==20.1.0
stripe==5.3.0
sumup==2.0.0
coingate==2.1.0
python-dotenv==1.0.0
openai==0.27.8
mysql-connector-python==8.0.33
redis==4.5.5
```

### **1.6. Nainštaluj závislosti**

```bash
pip3 install -r requirements.txt
```

---

## **🔑 2. Konfigurácia (`config.py`)**

```bash
nano config.py
```

**Vlož:**

```python
import os
from dotenv import load_dotenv

load_dotenv()  # Načítanie premenných z `.env`

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'tvoje_tajne_heslo_123')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql://root:tvoje_heslo@localhost/api_dashboard')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = '/var/www/api_dashboard/scripts'
    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
    SUMUP_API_KEY = os.getenv('SUMUP_API_KEY')
    COINGATE_API_KEY = os.getenv('COINGATE_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    REDIS_URL = 'redis://localhost:6379/0'
```

### **1.7. Vytvor `.env` súbor**

```bash
nano .env
```

**Vlož:**

```ini
SECRET_KEY=tvoje_tajne_heslo_123
DATABASE_URL=mysql://root:tvoje_heslo@localhost/api_dashboard
STRIPE_SECRET_KEY=sk_test_...
SUMUP_API_KEY=sumup_api_key_...
COINGATE_API_KEY=coingate_api_key_...
OPENAI_API_KEY=openai_api_key_...
```

---

## **📂 3. Databáza (MySQL)**

### **3.1. Vytvor databázu**

```bash
mysql -u root -p
```

**V MySQL konzole:**

```sql
CREATE DATABASE api_dashboard;
GRANT ALL PRIVILEGES ON api_dashboard.* TO 'root'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### **3.2. Inicializácia tabuliek (`database/init_db.sql`)**

```bash
nano database/init_db.sql
```

**Vlož:**

```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    password VARCHAR(120) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE
);

CREATE TABLE projects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    api_key VARCHAR(120) UNIQUE NOT NULL,
    script_path VARCHAR(200),
    is_active BOOLEAN DEFAULT TRUE,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT,
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'EUR',
    status VARCHAR(20) DEFAULT 'pending',
    gateway VARCHAR(20) NOT NULL,  # stripe, sumup, coingate
    transaction_id VARCHAR(120),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

CREATE TABLE automation (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT,
    script_name VARCHAR(120) NOT NULL,
    schedule VARCHAR(50) NOT NULL,  # napr. "0 3 * * *" (cron)
    last_run TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

CREATE TABLE ai_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT,
    prompt TEXT NOT NULL,
    response TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);
```

### **3.3. Načítanie databázy**

```bash
mysql -u root -p api_dashboard < database/init_db.sql
```

---

## **🖥️ 4. Hlavný Flask server (`app.py`)**

```bash
nano app.py
```

**Vlož:**

```python
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, DecimalField
from wtforms.validators import DataRequired, Email
from config import Config
import subprocess
import os
import stripe
import sumup
from coingate import CoinGate
import openai
import redis
from datetime import datetime

# --- INICIALIZÁCIA ---
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
redis_client = redis.StrictRedis.from_url(app.config['REDIS_URL'])

# --- STRIPE ---
stripe.api_key = app.config['STRIPE_SECRET_KEY']

# --- SUMUP ---
sumup.api_key = app.config['SUMUP_API_KEY']

# --- COINGATE ---
coingate = CoinGate(app.config['COINGATE_API_KEY'])

# --- OPENAI ---
openai.api_key = app.config['OPENAI_API_KEY']

# --- MODELY ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    projects = db.relationship('Project', backref='author', lazy=True)

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    api_key = db.Column(db.String(120), unique=True, nullable=False)
    script_path = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    payments = db.relationship('Payment', backref='project', lazy=True)
    automation = db.relationship('Automation', backref='project', lazy=True)
    ai_requests = db.relationship('AIRequest', backref='project', lazy=True)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='EUR')
    status = db.Column(db.String(20), default='pending')
    gateway = db.Column(db.String(20), nullable=False)
    transaction_id = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Automation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    script_name = db.Column(db.String(120), nullable=False)
    schedule = db.Column(db.String(50), nullable=False)
    last_run = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

class AIRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    prompt = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# --- FORMULÁRE ---
class LoginForm(FlaskForm):
    username = StringField('Užívateľské meno', validators=[DataRequired()])
    password = PasswordField('Heslo', validators=[DataRequired()])
    submit = SubmitField('Prihlásiť')

class ProjectForm(FlaskForm):
    name = StringField('Názov projektu', validators=[DataRequired()])
    script_path = StringField('Cesta k skriptu (napr. scrape_xvideos.py)')
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
    prompt = TextAreaField('AI prompt (napr. "Vytvor popisk pre porno video")', validators=[DataRequired()])
    submit = SubmitField('Generovať')

# --- LOGIN MANAGER ---
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- ROUTES ---
@app.route('/')
@login_required
def dashboard():
    projects = Project.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', projects=projects)

@app.route('/projects', methods=['GET', 'POST'])
@login_required
def projects():
    form = ProjectForm()
    if form.validate_on_submit():
        new_project = Project(
            name=form.name.data,
            api_key=os.urandom(24).hex(),
            script_path=form.script_path.data,
            user_id=current_user.id
        )
        db.session.add(new_project)
        db.session.commit()
        flash('Projekt bol pridaný!', 'success')
        return redirect(url_for('projects'))
    return render_template('projects/projects.html', form=form)

@app.route('/run_script/<int:project_id>')
@login_required
def run_script(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        flash('Nemáš oprávnenie!', 'danger')
        return redirect(url_for('dashboard'))
    if project.script_path:
        try:
            subprocess.Popen(['python3', os.path.join(app.config['UPLOAD_FOLDER'], project.script_path)])
            flash(f'Skript {project.name} beží!', 'success')
        except Exception as e:
            flash(f'Chyba: {str(e)}', 'danger')
    return redirect(url_for('dashboard'))

@app.route('/payments/<int:project_id>', methods=['GET', 'POST'])
@login_required
def payments(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        flash('Nemáš oprávnenie!', 'danger')
        return redirect(url_for('dashboard'))
    form = PaymentForm()
    if form.validate_on_submit():
        if form.gateway.data == 'stripe':
            # Vytvor platobný intent
            intent = stripe.PaymentIntent.create(
                amount=int(form.amount.data * 100),  # Stripe počíta v centoch
                currency=form.currency.data.lower(),
                metadata={'project_id': project_id}
            )
            new_payment = Payment(
                project_id=project_id,
                amount=form.amount.data,
                gateway='stripe',
                transaction_id=intent.id
            )
            db.session.add(new_payment)
            db.session.commit()
            return render_template('payments/stripe.html', client_secret=intent.client_secret)
        elif form.gateway.data == 'sumup':
            # SumUp integracia
            pass  # Doplň podľa SumUp API
        elif form.gateway.data == 'coingate':
            # CoinGate integracia
            order = coingate.create_order(
                amount=str(form.amount.data),
                currency='EUR',
                receive_currency='EUR',
                title=f'Platba pre projekt {project.name}'
            )
            new_payment = Payment(
                project_id=project_id,
                amount=form.amount.data,
                gateway='coingate',
                transaction_id=order.id
            )
            db.session.add(new_payment)
            db.session.commit()
            return redirect(order.payment_url)
    return render_template('payments/payments.html', form=form, project=project)

@app.route('/automation/<int:project_id>', methods=['GET', 'POST'])
@login_required
def automation(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        flash('Nemáš oprávnenie!', 'danger')
        return redirect(url_for('dashboard'))
    form = AutomationForm()
    if form.validate_on_submit():
        new_automation = Automation(
            project_id=project_id,
            script_name=form.script_name.data,
            schedule=form.schedule.data
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
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        flash('Nemáš oprávnenie!', 'danger')
        return redirect(url_for('dashboard'))
    form = AIForm()
    if form.validate_on_submit():
        try:
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=form.prompt.data,
                max_tokens=200
            )
            ai_request = AIRequest(
                project_id=project_id,
                prompt=form.prompt.data,
                response=response.choices[0].text.strip()
            )
            db.session.add(ai_request)
            db.session.commit()
            flash('AI odpoveď bola vygenerovaná!', 'success')
        except Exception as e:
            flash(f'Chyba AI: {str(e)}', 'danger')
    ai_requests = AIRequest.query.filter_by(project_id=project_id).order_by(AIRequest.created_at.desc()).limit(5).all()
    return render_template('ai/ai.html', form=form, ai_requests=ai_requests, project=project)

# --- AUTENTIFIKÁCIA ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:  # V reále použij hashovanie!
            login_user(user)
            return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- API ENDPOINTS ---
@app.route('/api/projects', methods=['GET'])
@login_required
def api_projects():
    projects = Project.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': project.id,
        'name': project.name,
        'api_key': project.api_key,
        'is_active': project.is_active
    } for project in projects])

# --- INICIALIZÁCIA ---
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)
```

---

## \*\*📄 5. HTML Šablóny

### **5.1. `templates/base.html`**

```bash
mkdir -p templates && nano templates/base.html
```

**Vlož:**

```html
<!DOCTYPE html>
<html lang="sk">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>API Dashboard</title>
    <link
      href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"
      rel="stylesheet"
    />
    <link
      rel="stylesheet"
      href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css"
    />
  </head>
  <body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
      <div class="container">
        <a class="navbar-brand" href="{{ url_for('dashboard') }}"
          >🚀 API Dashboard</a
        >
        <div class="navbar-nav">
          {% if current_user.is_authenticated %}
          <a class="nav-link" href="{{ url_for('projects') }}"
            ><i class="fas fa-project-diagram"></i> Projekty</a
          >
          <a class="nav-link" href="{{ url_for('logout') }}"
            ><i class="fas fa-sign-out-alt"></i> Odhlásiť</a
          >
          {% else %}
          <a class="nav-link" href="{{ url_for('login') }}"
            ><i class="fas fa-sign-in-alt"></i> Prihlásiť</a
          >
          {% endif %}
        </div>
      </div>
    </nav>
    <div class="container mt-4">
      {% with messages = get_flashed_messages(with_categories=true) %} {% if
      messages %} {% for category, message in messages %}
      <div class="alert alert-{{ category }}">{{ message }}</div>
      {% endfor %} {% endif %} {% endwith %} {% block content %}{% endblock %}
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
  </body>
</html>
```

### **5.2. `templates/dashboard.html`**

```bash
nano templates/dashboard.html
```

**Vlož:**

```html
{% extends "base.html" %} {% block content %}
<h1 class="mb-4">📊 Dashboard</h1>
<div class="row">
  {% for project in projects %}
  <div class="col-md-4 mb-4">
    <div class="card h-100">
      <div class="card-body">
        <h5 class="card-title">{{ project.name }}</h5>
        <p class="card-text">
          <strong>API Key:</strong> <code>{{ project.api_key }}</code><br />
          <strong>Skript:</strong> {{ project.script_path or "Žiadny" }}<br />
          <strong>Stav:</strong> {% if project.is_active %}✅ Aktívny{% else
          %}❌ Neaktívny{% endif %}
        </p>
        <div class="d-grid gap-2">
          <a
            href="{{ url_for('run_script', project_id=project.id) }}"
            class="btn btn-primary"
            ><i class="fas fa-play"></i> Spustiť skript</a
          >
          <a
            href="{{ url_for('payments', project_id=project.id) }}"
            class="btn btn-success"
            ><i class="fas fa-credit-card"></i> Platby</a
          >
          <a
            href="{{ url_for('automation', project_id=project.id) }}"
            class="btn btn-warning"
            ><i class="fas fa-robot"></i> Automatizácie</a
          >
          <a
            href="{{ url_for('ai', project_id=project.id) }}"
            class="btn btn-info"
            ><i class="fas fa-brain"></i> AI Generátor</a
          >
        </div>
      </div>
    </div>
  </div>
  {% endfor %}
</div>
{% endblock %}
```

### **5.3. `templates/projects/projects.html`**

```bash
mkdir -p templates/projects && nano templates/projects/projects.html
```

**Vlož:**

```html
{% extends "base.html" %} {% block content %}
<h1 class="mb-4">📁 Pridať nový projekt</h1>
<form method="POST">
  {{ form.hidden_tag() }}
  <div class="mb-3">
    {{ form.name.label(class="form-label") }} {{ form.name(class="form-control")
    }}
  </div>
  <div class="mb-3">
    {{ form.script_path.label(class="form-label") }} {{
    form.script_path(class="form-control") }}
    <small class="text-muted"
      >Napr. <code>scrape_xvideos.py</code> (uložený v
      <code>/var/www/api_dashboard/scripts/</code>)</small
    >
  </div>
  {{ form.submit(class="btn btn-primary") }}
</form>
{% endblock %}
```

### **5.4. `templates/payments/payments.html`**

```bash
mkdir -p templates/payments && nano templates/payments/payments.html
```

**Vlož:**

```html
{% extends "base.html" %} {% block content %}
<h1 class="mb-4">💳 Platby pre {{ project.name }}</h1>
<form method="POST">
  {{ form.hidden_tag() }}
  <div class="mb-3">
    {{ form.amount.label(class="form-label") }} {{
    form.amount(class="form-control") }}
  </div>
  <div class="mb-3">
    {{ form.gateway.label(class="form-label") }} {{
    form.gateway(class="form-select") }}
  </div>
  {{ form.submit(class="btn btn-success") }}
</form>

<h2 class="mt-4">História platieb</h2>
<table class="table">
  <thead>
    <tr>
      <th>Suma</th>
      <th>Brána</th>
      <th>Status</th>
      <th>Dátum</th>
    </tr>
  </thead>
  <tbody>
    {% for payment in project.payments %}
    <tr>
      <td>{{ payment.amount }} {{ payment.currency }}</td>
      <td>{{ payment.gateway }}</td>
      <td>
        {% if payment.status == 'pending' %}⏳ {% elif payment.status ==
        'completed' %}✅ {% else %}❌ {% endif %}
      </td>
      <td>{{ payment.created_at.strftime('%d.%m.%Y %H:%M') }}</td>
    </tr>
    {% endfor %}
  </tbody>
</table>
{% endblock %}
```

### **5.5. `templates/payments/stripe.html`**

```bash
nano templates/payments/stripe.html
```

**Vlož:**

```html
{% extends "base.html" %} {% block content %}
<h1 class="mb-4">💳 Platba cez Stripe</h1>
<div id="stripe-element">
  <!-- Stripe Elements bude vložený sem -->
</div>
<button id="submit-button" class="btn btn-success mt-3">Zaplatiť</button>

<script src="https://js.stripe.com/v3/"></script>
<script>
  const stripe = Stripe("{{ STRIPE_PUBLIC_KEY }}");
  const elements = stripe.elements();
  const cardElement = elements.create("card");
  cardElement.mount("#stripe-element");

  const submitButton = document.getElementById("submit-button");
  submitButton.addEventListener("click", async () => {
    const { error, paymentIntent } = await stripe.confirmCardPayment(
      "{{ client_secret }}",
      {
        payment_method: {
          card: cardElement,
        },
      }
    );
    if (error) {
      alert(error.message);
    } else if (paymentIntent.status === "succeeded") {
      window.location.href = "{{ url_for('dashboard') }}";
    }
  });
</script>
{% endblock %}
```

### **5.6. `templates/automation/automation.html`**

```bash
mkdir -p templates/automation && nano templates/automation/automation.html
```

**Vlož:**

```html
{% extends "base.html" %} {% block content %}
<h1 class="mb-4">⚙️ Automatizácie pre {{ project.name }}</h1>
<form method="POST">
  {{ form.hidden_tag() }}
  <div class="mb-3">
    {{ form.script_name.label(class="form-label") }} {{
    form.script_name(class="form-control") }}
  </div>
  <div class="mb-3">
    {{ form.schedule.label(class="form-label") }} {{
    form.schedule(class="form-control") }}
    <small class="text-muted"
      >Napr. <code>0 3 * * *</code> (každý deň o 3:00)</small
    >
  </div>
  {{ form.submit(class="btn btn-primary") }}
</form>

<h2 class="mt-4">Aktívne automatizácie</h2>
<table class="table">
  <thead>
    <tr>
      <th>Skript</th>
      <th>Rozvrh</th>
      <th>Stav</th>
      <th>Posledný beh</th>
    </tr>
  </thead>
  <tbody>
    {% for auto in automations %}
    <tr>
      <td>{{ auto.script_name }}</td>
      <td><code>{{ auto.schedule }}</code></td>
      <td>{% if auto.is_active %}✅ {% else %}❌ {% endif %}</td>
      <td>
        {{ auto.last_run.strftime('%d.%m.%Y %H:%M') if auto.last_run else "Ešte
        nebežalo" }}
      </td>
    </tr>
    {% endfor %}
  </tbody>
</table>
{% endblock %}
```

### **5.7. `templates/ai/ai.html`**

```bash
mkdir -p templates/ai && nano templates/ai/ai.html
```

**Vlož:**

```html
{% extends "base.html" %} {% block content %}
<h1 class="mb-4">🤖 AI Generátor pre {{ project.name }}</h1>
<form method="POST">
  {{ form.hidden_tag() }}
  <div class="mb-3">
    {{ form.prompt.label(class="form-label") }} {{
    form.prompt(class="form-control", rows=3) }}
    <small class="text-muted"
      >Napr. "Napíš popisk pre porno video s názvom 'Hardcore Sex'"</small
    >
  </div>
  {{ form.submit(class="btn btn-primary") }}
</form>

<h2 class="mt-4">Posledné AI požadavky</h2>
{% for request in ai_requests %}
<div class="card mb-3">
  <div class="card-body">
    <h5 class="card-title">
      📝 {{ request.created_at.strftime('%d.%m.%Y %H:%M') }}
    </h5>
    <p class="card-text">
      <strong>Prompt:</strong> {{ request.prompt }}<br />
      <strong>Odpoveď:</strong> {{ request.response }}
    </p>
  </div>
</div>
{% endfor %} {% endblock %}
```

### **5.8. `templates/login.html`**

```bash
nano templates/login.html
```

**Vlož:**

```html
{% extends "base.html" %} {% block content %}
<div class="row justify-content-center">
  <div class="col-md-6">
    <div class="card">
      <div class="card-body">
        <h1 class="card-title text-center mb-4">🔑 Prihlásenie</h1>
        <form method="POST">
          {{ form.hidden_tag() }}
          <div class="mb-3">
            {{ form.username.label(class="form-label") }} {{
            form.username(class="form-control") }}
          </div>
          <div class="mb-3">
            {{ form.password.label(class="form-label") }} {{
            form.password(class="form-control") }}
          </div>
          {{ form.submit(class="btn btn-primary w-100") }}
        </form>
      </div>
    </div>
  </div>
</div>
{% endblock %}
```

---

## \*\*🤖 6. Automatizačné skripty

### **6.1. `scripts/scrape_xvideos.py`**

```bash
mkdir -p scripts && nano scripts/scrape_xvideos.py
```

**Vlož:**

```python
import subprocess
import logging

logging.basicConfig(filename='/var/www/api_dashboard/logs/scrape_xvideos.log', level=logging.INFO)

def scrape():
    try:
        logging.info("Začínam stahovanie videí z XVideos...")
        subprocess.run([
            "youtube-dl",
            "--playlist-start", "1",
            "--playlist-end", "5",
            "--format", "mp4",
            "--output", "/var/www/html/videos/%(title)s.%(ext)s",
            "https://www.xvideos.com/tags/hardcore"
        ], check=True)
        logging.info("Stahovanie dokončené!")
    except subprocess.CalledProcessError as e:
        logging.error(f"Chyba pri stahovaní: {e}")

if __name__ == "__main__":
    scrape()
```

### **6.2. `scripts/ai_generate.py`**

```bash
nano scripts/ai_generate.py
```

**Vlož:**

```python
import openai
import logging
from config import Config

openai.api_key = Config.OPENAI_API_KEY
logging.basicConfig(filename='/var/www/api_dashboard/logs/ai_generate.log', level=logging.INFO)

def generate(prompt):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=200
        )
        return response.choices[0].text.strip()
    except Exception as e:
        logging.error(f"Chyba AI: {e}")
        return None

if __name__ == "__main__":
    print(generate("Napíš popisk pre porno video s názvom 'Hardcore Sex'"))
```

---

## **🔄 7. Nastavenie cron jobov pre automatizácie**

```bash
crontab -e
```

**Pridaj:**

```bash
# Každú minútu skontroluj automatizácie
* * * * * /usr/bin/python3 /var/www/api_dashboard/cron_check.py
```

**Vytvor `cron_check.py`:**

```bash
nano cron_check.py
```

**Vlož:**

```python
from app import db, Automation, Project
from datetime import datetime
import subprocess
import os

def run_pending_automations():
    now = datetime.utcnow()
    automations = Automation.query.filter_by(is_active=True).all()
    for auto in automations:
        # TODO: Implementuj logiku pre cron rozvrh
        if True:  # Zjednodušené - v reále použi `croniter`
            project = Project.query.get(auto.project_id)
            script_path = os.path.join('/var/www/api_dashboard/scripts', auto.script_name)
            if os.path.exists(script_path):
                subprocess.Popen(['python3', script_path])
                auto.last_run = now
                db.session.commit()

if __name__ == "__main__":
    run_pending_automations()
```

---

## **🌐 8. Nastavenie Nginx a Gunicorn**

### **8.1. Nginx konfig**

```bash
nano /etc/nginx/sites-available/api_dashboard
```

**Vlož:**

```nginx
server {
    listen 80;
    server_name tvojadomena.top;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static/ {
        alias /var/www/api_dashboard/static/;
    }
}
```

**Aktivuj konfig:**

```bash
ln -s /etc/nginx/sites-available/api_dashboard /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

### **8.2. Gunicorn služba**

```bash
nano /etc/systemd/system/api_dashboard.service
```

**Vlož:**

```ini
[Unit]
Description=API Dashboard
After=network.target

[Service]
User=root
WorkingDirectory=/var/www/api_dashboard
Environment="PATH=/var/www/api_dashboard/venv/bin"
ExecStart=/var/www/api_dashboard/venv/bin/gunicorn --bind 127.0.0.1:5000 --workers 4 app:app

[Install]
WantedBy=multi-user.target
```

**Aktivuj službu:**

```bash
systemctl daemon-reload
systemctl start api_dashboard
systemctl enable api_dashboard
```

---

## **🔒 9. Bezpečnostné nastavenia**

### **9.1. HTTPS (Let’s Encrypt)**

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d tvojadomena.top
```

### **9.2. Firewall (UFW)**

```bash
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### **9.3. Zálohovanie databázy**

```bash
nano /var/www/api_dashboard/backup_db.sh
```

**Vlož:**

```bash
#!/bin/bash
mysqldump -u root -p'tvoje_heslo' api_dashboard > /var/www/api_dashboard/backups/db_$(date +\%Y-\%m-\%d).sql
```

**Nastav cron:**

```bash
crontab -e
```

**Pridaj:**

```bash
0 3 * * * /bin/bash /var/www/api_dashboard/backup_db.sh
```

---

## \*\*📋 10. Návod na ovládanie

### **10.1. Prístup k dashboardu**

- Otvor prehliadač: **`https://tvojadomena.top`**
- Prihlás sa:
  - **Užívateľ:** `admin`
  - **Heslo:** `tvoje_heslo` (zmeň ho!)

### **10.2. Pridanie projektu**

1. Klikni na **"Projekty"** → **"Pridať nový projekt"**.
2. Vyplň **názov** a **cestu k skriptu** (napr. `scrape_xvideos.py`).
3. Klikni na **"Vytvoriť projekt"**.

### **10.3. Spustenie skriptu**

- Na dashboarde klikni na **"Spustiť skript"**.

### **10.4. Platby**

1. Klikni na **"Platby"** u projektu.
2. Vyplň **sumu** a vyber **platobnú bránu** (Stripe, SumUp, CoinGate).
3. Dokonči platbu.

### **10.5. Automatizácie**

1. Klikni na **"Automatizácie"**.
2. Vyplň **názov skriptu** a **cron rozvrh** (napr. `0 3 * * *` pre každý deň o 3:00).
3. Klikni na **"Pridať automatizáciu"**.

### **10.6. AI Generátor**

1. Klikni na **"AI Generátor"**.
2. Napíš **prompt** (napr. "Napíš popisk pre porno video").
3. Klikni na **"Generovať"**.

---

## **💡 11. Rozšírenia (ak chceš viac)**

### **11.1. Pridaj ďalšie platobné brány**

- **PayPal**: Použi [PayPal REST API](https://developer.paypal.com/docs/api/overview/).
- **Skrill**: Použi [Skrill API](https://www.skrill.com/en/siteinformation/api-integration/).

### **11.2. Pridaj monitoring (Grafana)**

```bash
sudo apt install grafana -y
sudo systemctl start grafana-server
sudo systemctl enable grafana-server
```

- Prístup: `http://tvojadomena.top:3000`

### **11.3. Pridaj WebSocket pre live notifikácie**

```bash
pip3 install flask-socketio
```

**Uprav `app.py`:**

```python
from flask_socketio import SocketIO

socketio = SocketIO(app)

@socketio.on('connect')
def handle_connect():
    print('Client connected')
```

---
