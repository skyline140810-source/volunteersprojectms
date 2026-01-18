from flask import Flask, render_template_string, request, redirect, make_response
import json
import os
import hashlib
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'school_project_secret_key_2024'

# Файлы для данных
REQUESTS_FILE = 'volunteer_data.json'
USERS_FILE = 'users.json'

# Статусы заявок
STATUS_ACTIVE = "активна"
STATUS_IN_PROGRESS = "выполняется"
STATUS_COMPLETED = "завершена"
STATUS_CANCELLED = "отменена"

# Классификации заявок
CLASSIFICATIONS = {
    'social': 'Социальное волонтерство',
    'ecological': 'Экологическое волонтерство',
    'other': 'Другое'
}

# Администраторы
ADMINS = ['admin']

# Загружаем данные
def load_data():
    """Загружаем заявки"""
    if os.path.exists(REQUESTS_FILE):
        try:
            with open(REQUESTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_data(data):
    """Сохраняем заявки"""
    with open(REQUESTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_users():
    """Загружаем пользователей"""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_users(users):
    """Сохраняем пользователей"""
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def hash_password(password):
    """Хешируем пароль"""
    return hashlib.sha256(password.encode()).hexdigest()

def check_auth(cookies):
    """Проверяем авторизацию по cookies"""
    username = cookies.get('username')
    password_hash = cookies.get('password_hash')
    
    if not username or not password_hash:
        return None
    
    users = load_users()
    if username in users and users[username] == password_hash:
        return username
    
    return None

def is_admin(username):
    """Проверяем, является ли пользователь администратором"""
    return username in ADMINS

# Создаем администратора при первом запуске
users = load_users()
if 'admin' not in users:
    users['admin'] = hash_password('admin123')
    save_users(users)

all_requests = load_data()

# ==================== АВТОРИЗАЦИЯ ====================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Страница входа"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        users = load_users()
        
        if username in users and users[username] == hash_password(password):
            # Создаем ответ с cookies
            response = make_response(redirect('/'))
            response.set_cookie('username', username)
            response.set_cookie('password_hash', users[username])
            return response
        
        # Неверные данные
        return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Вход</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background: #f5f5f5;
                    padding: 20px;
                }
                .container {
                    max-width: 400px;
                    margin: 100px auto;
                    background: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }
                h1 {
                    color: #2c3e50;
                    text-align: center;
                    margin-bottom: 30px;
                }
                input {
                    width: 100%;
                    padding: 12px;
                    margin: 10px 0;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    font-size: 16px;
                }
                button {
                    width: 100%;
                    padding: 12px;
                    background: #3498db;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 16px;
                    cursor: pointer;
                    margin-top: 10px;
                }
                button:hover {
                    background: #2980b9;
                }
                .error {
                    background: #ffe6e6;
                    color: #e74c3c;
                    padding: 10px;
                    border-radius: 4px;
                    margin-bottom: 20px;
                    text-align: center;
                }
                .links {
                    text-align: center;
                    margin-top: 20px;
                }
                .links a {
                    color: #3498db;
                    text-decoration: none;
                    margin: 0 10px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Вход в систему</h1>
                <div class="error">
                    Неверное имя пользователя или пароль
                </div>
                <form method="POST">
                    <input type="text" name="username" placeholder="Имя пользователя" required>
                    <input type="password" name="password" placeholder="Пароль" required>
                    <button type="submit">Войти</button>
                </form>
                <div class="links">
                    <a href="/register">Регистрация</a>
                    <a href="/">На главную</a>
                </div>
            </div>
        </body>
        </html>
        ''')
    
    # GET запрос - показываем форму входа
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Вход</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #f5f5f5;
                padding: 20px;
            }
            .container {
                max-width: 400px;
                margin: 100px auto;
                background: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #2c3e50;
                text-align: center;
                margin-bottom: 30px;
            }
            input {
                width: 100%;
                padding: 12px;
                margin: 10px 0;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 16px;
            }
            button {
                width: 100%;
                padding: 12px;
                background: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 16px;
                cursor: pointer;
                margin-top: 10px;
            }
            button:hover {
                background: #2980b9;
            }
            .links {
                text-align: center;
                margin-top: 20px;
            }
            .links a {
                color: #3498db;
                text-decoration: none;
                margin: 0 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Вход в систему</h1>
            <form method="POST">
                <input type="text" name="username" placeholder="Имя пользователя" required>
                <input type="password" name="password" placeholder="Пароль" required>
                <button type="submit">Войти</button>
            </form>
            <div class="links">
                <a href="/register">Регистрация</a>
                <a href="/">На главную</a>
            </div>
        </div>
    </body>
    </html>
    ''')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Страница регистрации"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        users = load_users()
        
        # Проверки
        if not username or not password:
            error = "Заполните все поля"
        elif len(username) < 3:
            error = "Имя пользователя должно быть не менее 3 символов"
        elif len(password) < 4:
            error = "Пароль должен быть не менее 4 символов"
        elif password != confirm_password:
            error = "Пароли не совпадают"
        elif username in users:
            error = "Пользователь с таким именем уже существует"
        else:
            # Регистрируем пользователя
            users[username] = hash_password(password)
            save_users(users)
            
            # Автоматически входим
            response = make_response(redirect('/'))
            response.set_cookie('username', username)
            response.set_cookie('password_hash', users[username])
            return response
        
        # Если есть ошибка - показываем форму с ошибкой
        return render_template_string(f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Регистрация</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background: #f5f5f5;
                    padding: 20px;
                }}
                .container {{
                    max-width: 400px;
                    margin: 50px auto;
                    background: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                h1 {{
                    color: #2c3e50;
                    text-align: center;
                    margin-bottom: 30px;
                }}
                input {{
                    width: 100%;
                    padding: 12px;
                    margin: 10px 0;
                    border: 1px solid #ddd;
                    border-radius: 4px;
                    font-size: 16px;
                }}
                button {{
                    width: 100%;
                    padding: 12px;
                    background: #27ae60;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 16px;
                    cursor: pointer;
                    margin-top: 10px;
                }}
                button:hover {{
                    background: #219653;
                }}
                .error {{
                    background: #ffe6e6;
                    color: #e74c3c;
                    padding: 10px;
                    border-radius: 4px;
                    margin-bottom: 20px;
                    text-align: center;
                }}
                .links {{
                    text-align: center;
                    margin-top: 20px;
                }}
                .links a {{
                    color: #3498db;
                    text-decoration: none;
                    margin: 0 10px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Регистрация</h1>
                <div class="error">
                    {error}
                </div>
                <form method="POST">
                    <input type="text" name="username" placeholder="Имя пользователя" required>
                    <input type="password" name="password" placeholder="Пароль" required>
                    <input type="password" name="confirm_password" placeholder="Повторите пароль" required>
                    <button type="submit">Зарегистрироваться</button>
                </form>
                <div class="links">
                    <a href="/login">Войти</a>
                    <a href="/">На главную</a>
                </div>
            </div>
        </body>
        </html>
        ''')
    
    # GET запрос - показываем форму регистрации
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Регистрация</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #f5f5f5;
                padding: 20px;
            }
            .container {
                max-width: 400px;
                margin: 50px auto;
                background: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #2c3e50;
                text-align: center;
                margin-bottom: 30px;
            }
            input {
                width: 100%;
                padding: 12px;
                margin: 10px 0;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 16px;
            }
            button {
                width: 100%;
                padding: 12px;
                background: #27ae60;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 16px;
                cursor: pointer;
                margin-top: 10px;
            }
            button:hover {
                background: #219653;
            }
            .links {
                text-align: center;
                margin-top: 20px;
            }
            .links a {
                color: #3498db;
                text-decoration: none;
                margin: 0 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Регистрация</h1>
            <form method="POST">
                <input type="text" name="username" placeholder="Имя пользователя" required>
                <input type="password" name="password" placeholder="Пароль" required>
                <input type="password" name="confirm_password" placeholder="Повторите пароль" required>
                <button type="submit">Зарегистрироваться</button>
            </form>
            <div class="links">
                <a href="/login">Войти</a>
                <a href="/">На главную</a>
            </div>
        </div>
    </body>
    </html>
    ''')

@app.route('/logout')
def logout():
    """Выход из системы"""
    response = make_response(redirect('/'))
    response.set_cookie('username', '', expires=0)
    response.set_cookie('password_hash', '', expires=0)
    return response

# ==================== ГЛАВНАЯ СТРАНИЦА ====================

@app.route('/')
def home():
    """Главная страница (меняется в зависимости от авторизации)"""
    username = check_auth(request.cookies)
    admin = is_admin(username) if username else False
    
    active_requests = [r for r in all_requests if r.get('status') == STATUS_ACTIVE]
    my_requests = [r for r in all_requests if r.get('author') == username]
    responded_requests = [r for r in all_requests if username in r.get('responders', [])]
    
    if username:
        # Пользователь авторизован
        requests_html = ""
        for i, r in enumerate(active_requests[:3]):
            status_class = r.get('status', 'active').replace(' ', '-')
            classification = CLASSIFICATIONS.get(r.get('classification', 'social'), 'Социальное волонтерство')
            requests_html += f'''
            <div class="request-item status-{status_class}">
                <div class="request-title">{r["name"]}</div>
                <div class="request-info">Классификация: {classification}</div>
                <div class="request-info">Город: {r["city"]}</div>
                <div class="request-info">Статус: {r.get('status', 'активна')}</div>
                <a href="/request/{i}" style="color: #3498db; font-size: 14px;">Подробнее</a>
            </div>
            '''
        
        my_requests_html = ""
        for r in my_requests[:3]:
            status_class = r.get('status', 'active').replace(' ', '-')
            request_index = all_requests.index(r)
            classification = CLASSIFICATIONS.get(r.get('classification', 'social'), 'Социальное волонтерство')
            my_requests_html += f'''
            <div class="request-item status-{status_class}">
                <div class="request-title">{r["name"]}</div>
                <div class="request-info">Классификация: {classification}</div>
                <div class="request-info">Статус: {r.get('status', 'активна')}</div>
                <div class="request-info">Откликов: {len(r.get('responders', []))}</div>
                <a href="/request/{request_index}" style="color: #3498db; font-size: 14px;">Управление</a>
            </div>
            '''
        
        admin_badge = '<span class="admin-badge">Администратор</span>' if admin else ''
        
        return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Добрые дела рядом</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background: #f5f5f5;
                    margin: 0;
                    padding: 20px;
                }
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                }
                header {
                    background: #2c3e50;
                    color: white;
                    padding: 20px;
                    border-radius: 8px;
                    margin-bottom: 30px;
                }
                h1 {
                    margin: 0;
                    font-size: 28px;
                }
                .user-info {
                    color: #bdc3c7;
                    margin-top: 10px;
                }
                .admin-badge {
                    background: #e74c3c;
                    color: white;
                    padding: 2px 8px;
                    border-radius: 4px;
                    font-size: 12px;
                    margin-left: 10px;
                }
                .dashboard {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }
                .card {
                    background: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }
                .card h2 {
                    color: #2c3e50;
                    margin-top: 0;
                    border-bottom: 2px solid #3498db;
                    padding-bottom: 10px;
                }
                .stats {
                    display: grid;
                    grid-template-columns: repeat(3, 1fr);
                    gap: 15px;
                    margin-bottom: 20px;
                }
                .stat {
                    background: #ecf0f1;
                    padding: 15px;
                    border-radius: 6px;
                    text-align: center;
                }
                .stat-number {
                    font-size: 24px;
                    font-weight: bold;
                    color: #2c3e50;
                }
                .stat-label {
                    color: #7f8c8d;
                    font-size: 14px;
                }
                .btn {
                    display: inline-block;
                    padding: 12px 24px;
                    background: #3498db;
                    color: white;
                    text-decoration: none;
                    border-radius: 4px;
                    border: none;
                    cursor: pointer;
                    font-size: 16px;
                    margin: 5px;
                }
                .btn:hover {
                    background: #2980b9;
                }
                .btn-create {
                    background: #27ae60;
                }
                .btn-create:hover {
                    background: #219653;
                }
                .btn-admin {
                    background: #e74c3c;
                }
                .btn-admin:hover {
                    background: #c0392b;
                }
                .btn-logout {
                    background: #95a5a6;
                }
                .btn-logout:hover {
                    background: #7f8c8d;
                }
                .btn-group {
                    margin-top: 20px;
                }
                .requests-list {
                    margin-top: 20px;
                }
                .request-item {
                    background: #f8f9fa;
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 6px;
                    border-left: 4px solid #3498db;
                }
                .status-active { border-left-color: #27ae60; }
                .status-in-progress { border-left-color: #f39c12; }
                .status-completed { border-left-color: #95a5a6; }
                .status-cancelled { border-left-color: #e74c3c; }
                .request-title {
                    font-weight: bold;
                    color: #2c3e50;
                }
                .request-info {
                    color: #7f8c8d;
                    font-size: 14px;
                    margin: 5px 0;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <header>
                    <h1>Добрые дела рядом</h1>
                    <div class="user-info">
                        Вы вошли как: <strong>''' + username + '''</strong>
                        ''' + admin_badge + '''
                    </div>
                </header>
                
                <div class="stats">
                    <div class="stat">
                        <div class="stat-number">''' + str(len(active_requests)) + '''</div>
                        <div class="stat-label">Активных заявок</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">''' + str(len(my_requests)) + '''</div>
                        <div class="stat-label">Моих заявок</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">''' + str(len(responded_requests)) + '''</div>
                        <div class="stat-label">Мои отклики</div>
                    </div>
                </div>
                
                <div class="btn-group">
                    <a href="/create" class="btn btn-create">Создать заявку</a>
                    <a href="/view" class="btn">Просмотр заявок</a>
                    <a href="/my_requests" class="btn">Мои заявки</a>
                    <a href="/archive" class="btn">Архив заявок</a>
                    ''' + ('<a href="/admin" class="btn btn-admin">Панель администратора</a>' if admin else '') + '''
                    <a href="/logout" class="btn btn-logout">Выйти</a>
                </div>
                
                <div class="dashboard">
                    <div class="card">
                        <h2>Последние активные заявки</h2>
                        <div class="requests-list">
                            ''' + (requests_html if requests_html else '<p>Нет активных заявок</p>') + '''
                        </div>
                    </div>
                    
                    <div class="card">
                        <h2>Мои последние заявки</h2>
                        <div class="requests-list">
                            ''' + (my_requests_html if my_requests_html else '<p>У вас пока нет заявок</p>') + '''
                        </div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        ''')
    else:
        # Пользователь не авторизован
        active_count = len([r for r in all_requests if r.get('status') == STATUS_ACTIVE])
        
        return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Добрые дела рядом</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background: #f5f5f5;
                    height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    margin: 0;
                }
                .container {
                    background: white;
                    padding: 40px;
                    border-radius: 8px;
                    box-shadow: 0 2px 20px rgba(0,0,0,0.1);
                    text-align: center;
                    max-width: 500px;
                    width: 100%;
                }
                h1 {
                    color: #2c3e50;
                    margin-bottom: 10px;
                }
                p {
                    color: #7f8c8d;
                    margin-bottom: 30px;
                }
                .btn {
                    display: block;
                    width: 100%;
                    padding: 15px;
                    margin: 10px 0;
                    font-size: 16px;
                    text-decoration: none;
                    border-radius: 4px;
                    color: white;
                    font-weight: bold;
                    border: none;
                    cursor: pointer;
                }
                .btn-login {
                    background: #3498db;
                }
                .btn-login:hover {
                    background: #2980b9;
                }
                .btn-register {
                    background: #27ae60;
                }
                .btn-register:hover {
                    background: #219653;
                }
                .btn-guest {
                    background: #95a5a6;
                }
                .btn-guest:hover {
                    background: #7f8c8d;
                }
                .stats {
                    margin-top: 30px;
                    padding: 15px;
                    background: #f8f9fa;
                    border-radius: 6px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Добрые дела рядом</h1>
                <p>Система поиска волонтеров и помощи</p>
                
                <a href="/login" class="btn btn-login">Войти в систему</a>
                <a href="/register" class="btn btn-register">Регистрация</a>
                <a href="/view" class="btn btn-guest">Просмотр заявок (гостем)</a>
                
                <div class="stats">
                    <p>Всего заявок: ''' + str(len(all_requests)) + '''</p>
                    <p>Активных заявок: ''' + str(active_count) + '''</p>
                </div>
            </div>
        </body>
        </html>
        ''')

# ==================== СОЗДАНИЕ ЗАЯВКИ ====================

@app.route('/create', methods=['GET', 'POST'])
def create():
    """Создание заявки"""
    username = check_auth(request.cookies)
    if not username:
        return redirect('/login')
    
    if request.method == 'POST':
        new_request = {
            'id': len(all_requests) + 1,
            'author': username,
            'name': request.form['name'],
            'city': request.form['city'],
            'phone': request.form['phone'],
            'help': request.form['help'],
            'classification': request.form.get('classification', 'social'),
            'status': STATUS_ACTIVE,
            'created_at': datetime.now().strftime('%d.%m.%Y %H:%M'),
            'updated_at': datetime.now().strftime('%d.%m.%Y %H:%M'),
            'responders': []
        }
        
        all_requests.append(new_request)
        save_data(all_requests)
        return redirect('/my_requests')
    
    # Показываем форму
    classification_options = ''
    for key, value in CLASSIFICATIONS.items():
        classification_options += f'<option value="{key}">{value}</option>'
    
    return render_template_string(f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Новая заявка</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #f5f5f5;
                padding: 20px;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #2c3e50;
                text-align: center;
                margin-bottom: 30px;
            }}
            .user-info {{
                text-align: center;
                color: #7f8c8d;
                margin-bottom: 20px;
                padding: 10px;
                background: #f8f9fa;
                border-radius: 4px;
            }}
            input, textarea, select {{
                width: 100%;
                padding: 12px;
                margin: 10px 0;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 16px;
                box-sizing: border-box;
            }}
            button {{
                width: 100%;
                padding: 15px;
                background: #27ae60;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 16px;
                cursor: pointer;
                margin-top: 10px;
            }}
            button:hover {{
                background: #219653;
            }}
            .back {{
                text-align: center;
                margin-top: 20px;
            }}
            .back a {{
                color: #3498db;
                text-decoration: none;
                padding: 10px 20px;
                background: #f8f9fa;
                border-radius: 4px;
                display: inline-block;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Создание новой заявки</h1>
            <div class="user-info">
                Вы авторизованы как: <strong>{username}</strong>
            </div>
            
            <form method="POST">
                <input type="text" name="name" placeholder="Ваше имя или название организации" required>
                <input type="text" name="city" placeholder="Город" required>
                <input type="text" name="phone" placeholder="Телефон" required>
                <select name="classification" required>
                    <option value="">Выберите классификацию</option>
                    {classification_options}
                </select>
                <textarea name="help" placeholder="Опишите, какая помощь нужна" rows="6" required></textarea>
                
                <button type="submit">Создать заявку</button>
            </form>
            
            <div class="back">
                <a href="/">На главную</a>
            </div>
        </div>
    </body>
    </html>
    ''')

# ==================== ПРОСМОТР ЗАЯВОК ====================

@app.route('/view')
def view():
    """Просмотр активных заявок (доступно всем)"""
    username = check_auth(request.cookies)
    admin = is_admin(username) if username else False
    
    visible_requests = [r for r in all_requests if r.get('status') == STATUS_ACTIVE]
    
    requests_html = ""
    for i, r in enumerate(all_requests):
        if i in [all_requests.index(req) for req in visible_requests]:
            status_class = r.get('status', 'active').replace(' ', '-')
            classification = CLASSIFICATIONS.get(r.get('classification', 'social'), 'Социальное волонтерство')
            
            respond_button = ''
            if username and username != r.get('author') and r.get('status') == STATUS_ACTIVE:
                respond_button = f'<a href="/respond/{i}" class="btn btn-respond">Откликнуться</a>'
            
            responders_info = ''
            if r.get('responders'):
                responders_info = f'<div class="request-info">Откликов: {len(r.get("responders", []))}</div>'
            
            requests_html += f'''
            <div class="request-card {status_class}">
                <div class="request-title">{r['name']}</div>
                <div class="request-info">Классификация: {classification}</div>
                <div class="request-info">Город: {r['city']}</div>
                <div class="request-info">Телефон: {r['phone']}</div>
                <div class="request-info">Помощь: {r['help']}</div>
                <div class="request-info">Создано: {r['created_at']}</div>
                <div class="request-info">Автор: {r.get('author', 'аноним')}</div>
                
                <div class="request-status status-{status_class}">
                    {r.get('status', 'активна')}
                </div>
                
                {responders_info}
                
                <div>
                    <a href="/request/{i}" class="btn">Подробнее</a>
                    {respond_button}
                </div>
            </div>
            '''
    
    auth_info = ''
    if username:
        auth_info = f'Вы вошли как: <strong>{username}</strong>' + (' (администратор)' if admin else '')
    else:
        auth_info = 'Вы не авторизованы'
    
    grid_html = ''
    if visible_requests:
        grid_html = f'<div class="requests-grid">{requests_html}</div>'
    else:
        grid_html = '''
        <div class="empty-message">
            <p>Нет активных заявок</p>
            <p>Все заявки либо выполнены, либо находятся в архиве</p>
        </div>
        '''
    
    return render_template_string(f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Просмотр заявок</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #f5f5f5;
                padding: 20px;
            }}
            .container {{
                max-width: 1000px;
                margin: 0 auto;
            }}
            header {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 30px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #2c3e50;
                margin: 0;
            }}
            .auth-info {{
                color: #7f8c8d;
                margin-top: 10px;
            }}
            .back-link {{
                display: inline-block;
                margin-top: 20px;
                color: #3498db;
                text-decoration: none;
                padding: 8px 16px;
                background: #f8f9fa;
                border-radius: 4px;
            }}
            .requests-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 20px;
            }}
            .request-card {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                border-left: 4px solid #3498db;
            }}
            .request-card.active {{ border-left-color: #27ae60; }}
            .request-card.in-progress {{ border-left-color: #f39c12; }}
            .request-card.completed {{ border-left-color: #95a5a6; }}
            .request-card.cancelled {{ border-left-color: #e74c3c; }}
            
            .request-title {{
                font-weight: bold;
                color: #2c3e50;
                font-size: 18px;
                margin: 0 0 10px 0;
            }}
            .request-info {{
                color: #7f8c8d;
                margin: 8px 0;
                font-size: 14px;
            }}
            .request-status {{
                display: inline-block;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
                margin: 10px 0;
            }}
            .status-active {{ background: #d4edda; color: #155724; }}
            .status-in-progress {{ background: #fff3cd; color: #856404; }}
            .status-completed {{ background: #e2e3e5; color: #383d41; }}
            .status-cancelled {{ background: #f8d7da; color: #721c24; }}
            
            .btn {{
                display: inline-block;
                padding: 8px 16px;
                background: #3498db;
                color: white;
                text-decoration: none;
                border-radius: 4px;
                border: none;
                cursor: pointer;
                font-size: 14px;
                margin-top: 10px;
                margin-right: 5px;
            }}
            .btn:hover {{
                background: #2980b9;
            }}
            .btn-respond {{
                background: #27ae60;
            }}
            .btn-respond:hover {{
                background: #219653;
            }}
            .empty-message {{
                text-align: center;
                padding: 40px;
                color: #7f8c8d;
                font-size: 18px;
            }}
            .stats {{
                background: white;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>Активные заявки</h1>
                <div class="auth-info">
                    {auth_info}
                </div>
                <a href="/" class="back-link">На главную</a>
            </header>
            
            <div class="stats">
                Найдено заявок: {len(visible_requests)} из {len(all_requests)}
            </div>
            
            {grid_html}
        </div>
    </body>
    </html>
    ''')

# ==================== ДЕТАЛЬНАЯ СТРАНИЦА ЗАЯВКИ ====================

@app.route('/request/<int:index>')
def request_detail(index):
    """Детальная страница заявки"""
    username = check_auth(request.cookies)
    admin = is_admin(username) if username else False
    
    if index < 0 or index >= len(all_requests):
        return "Заявка не найдена", 404
    
    request_data = all_requests[index]
    
    # Проверяем права доступа
    can_view = False
    if admin:
        can_view = True
    elif username == request_data.get('author'):
        can_view = True
    elif username in request_data.get('responders', []):
        can_view = True
    elif request_data.get('status') == STATUS_ACTIVE:
        can_view = True
    
    if not can_view:
        return "Доступ запрещен", 403
    
    responders_html = ""
    if request_data.get('responders'):
        for responder in request_data.get('responders', []):
            responders_html += f'<div class="responder">{responder}</div>'
    
    # Получаем название классификации
    classification = CLASSIFICATIONS.get(request_data.get('classification', 'social'), 'Социальное волонтерство')
    
    # Формируем кнопки действий
    action_buttons = '<a href="/view" class="btn btn-back">Назад к списку</a>'
    
    if username and username != request_data.get('author') and request_data.get('status') == STATUS_ACTIVE:
        action_buttons += f'<a href="/respond/{index}" class="btn btn-respond">Откликнуться на заявку</a>'
    
    if username == request_data.get('author') and request_data.get('status') in [STATUS_ACTIVE, STATUS_IN_PROGRESS]:
        action_buttons += f'''
        <form action="/update_status/{index}" method="POST" style="display: inline;">
            <input type="hidden" name="status" value="{STATUS_COMPLETED}">
            <button type="submit" class="btn btn-complete">Отметить как выполненную</button>
        </form>
        '''
        action_buttons += f'''
        <form action="/update_status/{index}" method="POST" style="display: inline;">
            <input type="hidden" name="status" value="{STATUS_CANCELLED}">
            <button type="submit" class="btn btn-cancel" onclick="return confirm('Вы уверены, что хотите отменить заявку?')">Отменить заявку</button>
        </form>
        '''
    
    if admin or username == request_data.get('author'):
        action_buttons += f'''
        <form action="/delete/{index}" method="POST" style="display: inline;">
            <button type="submit" class="btn btn-cancel" onclick="return confirm('Вы уверены, что хотите удалить заявку?')">Удалить заявку</button>
        </form>
        '''
    
    # Обработка отображения списка откликов
    responders_section = ''
    if request_data.get('responders'):
        responders_section = f'''
        <div class="responders-list">
            <h3>Откликнувшиеся волонтеры ({len(request_data.get('responders', []))}):</h3>
            {responders_html or '<p>Пока нет откликов</p>'}
        </div>
        '''
    
    return render_template_string(f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Заявка: {request_data["name"]}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #f5f5f5;
                padding: 20px;
            }}
            .container {{
                max-width: 800px;
                margin: 0 auto;
            }}
            .request-detail {{
                background: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 20px rgba(0,0,0,0.1);
            }}
            .request-header {{
                border-bottom: 2px solid #ecf0f1;
                padding-bottom: 20px;
                margin-bottom: 20px;
            }}
            .request-title {{
                color: #2c3e50;
                font-size: 24px;
                margin: 0 0 10px 0;
            }}
            .request-meta {{
                color: #7f8c8d;
                font-size: 14px;
            }}
            .request-status {{
                display: inline-block;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
                margin: 10px 0;
            }}
            .status-active {{ background: #d4edda; color: #155724; }}
            .status-in-progress {{ background: #fff3cd; color: #856404; }}
            .status-completed {{ background: #e2e3e5; color: #383d41; }}
            .status-cancelled {{ background: #f8d7da; color: #721c24; }}
            
            .request-content {{
                margin: 20px 0;
            }}
            .info-row {{
                margin: 15px 0;
                padding: 10px;
                background: #f8f9fa;
                border-radius: 4px;
            }}
            .info-label {{
                font-weight: bold;
                color: #2c3e50;
            }}
            .info-value {{
                color: #34495e;
                margin-top: 5px;
            }}
            
            .btn {{
                display: inline-block;
                padding: 10px 20px;
                margin: 5px;
                border-radius: 4px;
                text-decoration: none;
                color: white;
                border: none;
                cursor: pointer;
                font-size: 14px;
            }}
            .btn-back {{ background: #95a5a6; }}
            .btn-back:hover {{ background: #7f8c8d; }}
            .btn-respond {{ background: #27ae60; }}
            .btn-respond:hover {{ background: #219653; }}
            .btn-cancel {{ background: #e74c3c; }}
            .btn-cancel:hover {{ background: #c0392b; }}
            .btn-complete {{ background: #3498db; }}
            .btn-complete:hover {{ background: #2980b9; }}
            .btn-edit {{ background: #f39c12; }}
            .btn-edit:hover {{ background: #d68910; }}
            
            .responders-list {{
                margin-top: 30px;
                padding: 20px;
                background: #f8f9fa;
                border-radius: 6px;
            }}
            .responder {{
                padding: 10px;
                margin: 10px 0;
                background: white;
                border-radius: 4px;
                border-left: 3px solid #3498db;
            }}
            .action-form {{
                margin-top: 20px;
                padding-top: 20px;
                border-top: 1px solid #ecf0f1;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="request-detail">
                <div class="request-header">
                    <h1 class="request-title">{request_data["name"]}</h1>
                    <div class="request-meta">
                        Создано: {request_data["created_at"]} | 
                        Автор: {request_data.get("author", "аноним")} | 
                        ID: {request_data.get("id", index + 1)}
                    </div>
                    <div class="request-status status-{request_data.get('status', 'active').replace(' ', '-')}">
                        Статус: {request_data.get('status', 'активна')}
                    </div>
                </div>
                
                <div class="request-content">
                    <div class="info-row">
                        <div class="info-label">Классификация:</div>
                        <div class="info-value">{classification}</div>
                    </div>
                    
                    <div class="info-row">
                        <div class="info-label">Город:</div>
                        <div class="info-value">{request_data["city"]}</div>
                    </div>
                    
                    <div class="info-row">
                        <div class="info-label">Контактный телефон:</div>
                        <div class="info-value">{request_data["phone"]}</div>
                    </div>
                    
                    <div class="info-row">
                        <div class="info-label">Описание помощи:</div>
                        <div class="info-value">{request_data["help"]}</div>
                    </div>
                    
                    <div class="info-row">
                        <div class="info-label">Последнее обновление:</div>
                        <div class="info-value">{request_data.get("updated_at", request_data["created_at"])}</div>
                    </div>
                </div>
                
                {responders_section}
                
                <div class="action-form">
                    {action_buttons}
                </div>
            </div>
        </div>
    </body>
    </html>
    ''')

# ==================== ОТКЛИК НА ЗАЯВКУ ====================

@app.route('/respond/<int:index>', methods=['GET', 'POST'])
def respond_to_request(index):
    """Отклик на заявку"""
    username = check_auth(request.cookies)
    if not username:
        return redirect('/login')
    
    if index < 0 or index >= len(all_requests):
        return "Заявка не найдена", 404
    
    request_data = all_requests[index]
    
    if username == request_data.get('author'):
        return "Вы не можете откликнуться на свою заявку", 403
    
    if request_data.get('status') != STATUS_ACTIVE:
        return "На эту заявку нельзя откликнуться", 403
    
    if request.method == 'POST':
        # Добавляем отклик
        if 'responders' not in request_data:
            request_data['responders'] = []
        
        if username not in request_data['responders']:
            request_data['responders'].append(username)
            
            # Если это первый отклик - меняем статус
            if len(request_data['responders']) == 1:
                request_data['status'] = STATUS_IN_PROGRESS
            
            request_data['updated_at'] = datetime.now().strftime('%d.%m.%Y %H:%M')
            all_requests[index] = request_data
            save_data(all_requests)
        
        return redirect(f'/request/{index}')
    
    # GET запрос - показываем подтверждение
    classification = CLASSIFICATIONS.get(request_data.get('classification', 'social'), 'Социальное волонтерство')
    
    return render_template_string(f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Отклик на заявку</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #f5f5f5;
                padding: 20px;
            }}
            .container {{
                max-width: 600px;
                margin: 100px auto;
                background: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 20px rgba(0,0,0,0.1);
                text-align: center;
            }}
            h1 {{
                color: #2c3e50;
            }}
            .request-info {{
                background: #f8f9fa;
                padding: 20px;
                border-radius: 6px;
                margin: 20px 0;
                text-align: left;
            }}
            .btn {{
                display: inline-block;
                padding: 12px 24px;
                margin: 10px;
                border-radius: 4px;
                text-decoration: none;
                color: white;
                border: none;
                cursor: pointer;
                font-size: 16px;
            }}
            .btn-confirm {{
                background: #27ae60;
            }}
            .btn-confirm:hover {{
                background: #219653;
            }}
            .btn-cancel {{
                background: #95a5a6;
            }}
            .btn-cancel:hover {{
                background: #7f8c8d;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Отклик на заявку</h1>
            <p>Вы собираетесь откликнуться на заявку:</p>
            
            <div class="request-info">
                <p><strong>{request_data["name"]}</strong></p>
                <p>Классификация: {classification}</p>
                <p>Город: {request_data["city"]}</p>
                <p>Помощь: {request_data["help"]}</p>
                <p>Автор: {request_data.get("author", "аноним")}</p>
            </div>
            
            <p>После отклика вы сможете видеть контактные данные автора и общаться с ним.</p>
            
            <form method="POST">
                <button type="submit" class="btn btn-confirm">Подтвердить отклик</button>
                <a href="/request/{index}" class="btn btn-cancel">Отмена</a>
            </form>
        </div>
    </body>
    </html>
    ''')

# ==================== МОИ ЗАЯВКИ ====================

@app.route('/my_requests')
def my_requests():
    """Страница с заявками пользователя"""
    username = check_auth(request.cookies)
    if not username:
        return redirect('/login')
    
    admin = is_admin(username)
    
    if admin:
        # Администратор видит все заявки
        user_requests = all_requests
        title = 'Все заявки'
    else:
        # Обычный пользователь видит свои заявки и заявки, на которые откликнулся
        user_requests = [r for r in all_requests if r.get('author') == username or username in r.get('responders', [])]
        title = 'Мои заявки'
    
    requests_html = ""
    for r in user_requests:
        status_class = r.get('status', 'active').replace(' ', '-')
        request_index = all_requests.index(r)
        role_class = 'role-author' if r.get('author') == username else 'role-responder'
        role_text = 'Автор' if r.get('author') == username else 'Откликнулся'
        classification = CLASSIFICATIONS.get(r.get('classification', 'social'), 'Социальное волонтерство')
        
        respond_button = ''
        if username != r.get('author') and r.get('status') == STATUS_ACTIVE:
            respond_button = f'<a href="/respond/{request_index}" class="btn btn-respond">Откликнуться</a>'
        
        manage_button = ''
        if username == r.get('author') or admin:
            manage_button = f'<a href="/request/{request_index}" class="btn btn-manage">Управление</a>'
        
        responders_info = ''
        if r.get('responders'):
            responders_info = f'<span class="request-info">Откликов: {len(r.get("responders", []))}</span>'
        
        requests_html += f'''
        <div class="request-card {status_class}">
            <div class="request-header">
                <div class="request-title">{r['name']}</div>
                <div class="request-status status-{status_class}">
                    {r.get('status', 'активна')}
                </div>
            </div>
            
            <div class="request-info">Классификация: {classification}</div>
            <div class="request-info">Город: {r['city']}</div>
            <div class="request-info">Создано: {r['created_at']}</div>
            
            <div>
                <span class="request-role {role_class}">
                    {role_text}
                </span>
                {responders_info}
            </div>
            
            <div style="margin-top: 15px;">
                <a href="/request/{request_index}" class="btn btn-details">Подробнее</a>
                {respond_button}
                {manage_button}
            </div>
        </div>
        '''
    
    empty_message = '''
    <div class="empty-message">
        <p>У вас пока нет заявок</p>
        <p><a href="/create">Создайте первую заявку</a> или <a href="/view">откликнитесь на существующие</a></p>
    </div>
    '''
    
    return render_template_string(f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Мои заявки</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #f5f5f5;
                padding: 20px;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
            }}
            header {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 30px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #2c3e50;
                margin: 0;
            }}
            .back-link {{
                display: inline-block;
                margin-top: 20px;
                color: #3498db;
                text-decoration: none;
                padding: 8px 16px;
                background: #f8f9fa;
                border-radius: 4px;
            }}
            .requests-list {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
                gap: 20px;
            }}
            .request-card {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                border-left: 4px solid #3498db;
            }}
            .request-card.active {{ border-left-color: #27ae60; }}
            .request-card.in-progress {{ border-left-color: #f39c12; }}
            .request-card.completed {{ border-left-color: #95a5a6; }}
            .request-card.cancelled {{ border-left-color: #e74c3c; }}
            
            .request-header {{
                display: flex;
                justify-content: space-between;
                align-items: start;
                margin-bottom: 15px;
            }}
            .request-title {{
                font-weight: bold;
                color: #2c3e50;
                font-size: 18px;
                margin: 0;
            }}
            .request-status {{
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
            }}
            .status-active {{ background: #d4edda; color: #155724; }}
            .status-in-progress {{ background: #fff3cd; color: #856404; }}
            .status-completed {{ background: #e2e3e5; color: #383d41; }}
            .status-cancelled {{ background: #f8d7da; color: #721c24; }}
            
            .request-info {{
                color: #7f8c8d;
                margin: 8px 0;
                font-size: 14px;
            }}
            .request-role {{
                display: inline-block;
                padding: 2px 6px;
                background: #3498db;
                color: white;
                border-radius: 3px;
                font-size: 12px;
                margin-right: 5px;
            }}
            .role-author {{ background: #27ae60; }}
            .role-responder {{ background: #f39c12; }}
            
            .btn {{
                display: inline-block;
                padding: 8px 16px;
                margin: 5px 5px 0 0;
                border-radius: 4px;
                text-decoration: none;
                color: white;
                border: none;
                cursor: pointer;
                font-size: 14px;
            }}
            .btn-details {{ background: #3498db; }}
            .btn-details:hover {{ background: #2980b9; }}
            .btn-respond {{ background: #27ae60; }}
            .btn-respond:hover {{ background: #219653; }}
            .btn-manage {{ background: #f39c12; }}
            .btn-manage:hover {{ background: #d68910; }}
            
            .empty-message {{
                text-align: center;
                padding: 40px;
                color: #7f8c8d;
                font-size: 18px;
                grid-column: 1 / -1;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>{title}</h1>
                <a href="/" class="back-link">На главную</a>
            </header>
            
            <div class="requests-list">
                {requests_html if requests_html else empty_message}
            </div>
        </div>
    </body>
    </html>
    ''')

# ==================== АРХИВ ЗАЯВОК ====================

@app.route('/archive')
def archive():
    """Архив завершенных и отмененных заявок"""
    username = check_auth(request.cookies)
    if not username:
        return redirect('/login')
    
    admin = is_admin(username)
    
    if admin:
        # Администратор видит все неактивные заявки
        archived_requests = [r for r in all_requests if r.get('status') in [STATUS_COMPLETED, STATUS_CANCELLED]]
    else:
        # Обычный пользователь видит только свои неактивные заявки
        archived_requests = [r for r in all_requests if r.get('author') == username and r.get('status') in [STATUS_COMPLETED, STATUS_CANCELLED]]
    
    requests_html = ""
    for r in archived_requests:
        status_class = r.get('status', 'completed').replace(' ', '-')
        request_index = all_requests.index(r)
        classification = CLASSIFICATIONS.get(r.get('classification', 'social'), 'Социальное волонтерство')
        requests_html += f'''
        <div class="request-card {status_class}">
            <div class="request-title">{r['name']}</div>
            <div class="request-info">Классификация: {classification}</div>
            <div class="request-info">Город: {r['city']}</div>
            <div class="request-info">Создано: {r['created_at']}</div>
            <div class="request-info">Завершено: {r.get('updated_at', r['created_at'])}</div>
            <div class="request-info">Автор: {r.get('author', 'аноним')}</div>
            
            <div class="request-status status-{status_class}">
                {r.get('status', 'завершена')}
            </div>
            
            <a href="/request/{request_index}" style="color: #3498db; font-size: 14px;">Просмотреть</a>
        </div>
        '''
    
    empty_message = '''
    <div class="empty-message">
        <p>Архив пуст</p>
        <p>Здесь будут отображаться завершенные и отмененные заявки</p>
    </div>
    '''
    
    return render_template_string(f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Архив заявок</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #f5f5f5;
                padding: 20px;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
            }}
            header {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 30px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #2c3e50;
                margin: 0;
            }}
            .back-link {{
                display: inline-block;
                margin-top: 20px;
                color: #3498db;
                text-decoration: none;
                padding: 8px 16px;
                background: #f8f9fa;
                border-radius: 4px;
            }}
            .requests-list {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
                gap: 20px;
            }}
            .request-card {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                border-left: 4px solid #95a5a6;
                opacity: 0.8;
            }}
            .request-card.completed {{ border-left-color: #95a5a6; }}
            .request-card.cancelled {{ border-left-color: #e74c3c; }}
            
            .request-title {{
                font-weight: bold;
                color: #2c3e50;
                font-size: 18px;
                margin: 0 0 10px 0;
            }}
            .request-info {{
                color: #7f8c8d;
                margin: 8px 0;
                font-size: 14px;
            }}
            .request-status {{
                display: inline-block;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
                margin: 10px 0;
            }}
            .status-completed {{ background: #e2e3e5; color: #383d41; }}
            .status-cancelled {{ background: #f8d7da; color: #721c24; }}
            
            .empty-message {{
                text-align: center;
                padding: 40px;
                color: #7f8c8d;
                font-size: 18px;
                grid-column: 1 / -1;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>Архив заявок</h1>
                <a href="/" class="back-link">На главную</a>
            </header>
            
            <div class="requests-list">
                {requests_html if requests_html else empty_message}
            </div>
        </div>
    </body>
    </html>
    ''')

# ==================== ПАНЕЛЬ АДМИНИСТРАТОРА ====================

@app.route('/admin')
def admin_panel():
    """Панель администратора"""
    username = check_auth(request.cookies)
    if not username or not is_admin(username):
        return "Доступ запрещен", 403
    
    # Статистика
    stats = {
        'total': len(all_requests),
        'active': len([r for r in all_requests if r.get('status') == STATUS_ACTIVE]),
        'in_progress': len([r for r in all_requests if r.get('status') == STATUS_IN_PROGRESS]),
        'completed': len([r for r in all_requests if r.get('status') == STATUS_COMPLETED]),
        'cancelled': len([r for r in all_requests if r.get('status') == STATUS_CANCELLED]),
        'social': len([r for r in all_requests if r.get('classification') == 'social']),
        'ecological': len([r for r in all_requests if r.get('classification') == 'ecological']),
        'other': len([r for r in all_requests if r.get('classification') == 'other']),
        'users': len(load_users())
    }
    
    recent_requests_html = ""
    for i, r in enumerate(all_requests[-10:]):
        status_class = r.get('status', 'active').replace(' ', '-')
        classification = CLASSIFICATIONS.get(r.get('classification', 'social'), 'Социальное волонтерство')
        recent_requests_html += f'''
        <tr>
            <td>{r.get('id', 'N/A')}</td>
            <td>{r['name']}</td>
            <td>{r.get('author', 'аноним')}</td>
            <td>{classification}</td>
            <td><span class="status-badge status-{status_class}">{r.get('status', 'активна')}</span></td>
            <td>{r['created_at']}</td>
            <td><a href="/request/{i}" class="btn btn-view">Просмотр</a></td>
        </tr>
        '''
    
    return render_template_string(f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Панель администратора</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #f5f5f5;
                padding: 20px;
            }}
            .container {{
                max-width: 1400px;
                margin: 0 auto;
            }}
            header {{
                background: #2c3e50;
                color: white;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 30px;
            }}
            h1 {{
                margin: 0;
                font-size: 28px;
            }}
            .admin-info {{
                color: #bdc3c7;
                margin-top: 10px;
            }}
            .back-link {{
                display: inline-block;
                margin-top: 20px;
                color: #3498db;
                text-decoration: none;
                padding: 8px 16px;
                background: #34495e;
                border-radius: 4px;
            }}
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            .stat-card {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                text-align: center;
            }}
            .stat-number {{
                font-size: 32px;
                font-weight: bold;
                color: #2c3e50;
            }}
            .stat-label {{
                color: #7f8c8d;
                font-size: 14px;
                margin-top: 10px;
            }}
            .admin-actions {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            .action-card {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            .action-card h2 {{
                color: #2c3e50;
                margin-top: 0;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
            }}
            .btn {{
                display: inline-block;
                padding: 10px 20px;
                margin: 5px;
                border-radius: 4px;
                text-decoration: none;
                color: white;
                border: none;
                cursor: pointer;
                font-size: 14px;
            }}
            .btn-view {{ background: #3498db; }}
            .btn-view:hover {{ background: #2980b9; }}
            .btn-archive {{ background: #95a5a6; }}
            .btn-archive:hover {{ background: #7f8c8d; }}
            .btn-all {{ background: #2c3e50; }}
            .btn-all:hover {{ background: #1a252f; }}
            .btn-manage {{ background: #27ae60; }}
            .btn-manage:hover {{ background: #219653; }}
            .btn-danger {{ background: #e74c3c; }}
            .btn-danger:hover {{ background: #c0392b; }}
            
            .recent-requests {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                margin-top: 30px;
            }}
            .requests-table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            .requests-table th {{
                background: #f8f9fa;
                padding: 12px;
                text-align: left;
                border-bottom: 2px solid #dee2e6;
                color: #495057;
                font-weight: bold;
            }}
            .requests-table td {{
                padding: 12px;
                border-bottom: 1px solid #dee2e6;
                color: #6c757d;
            }}
            .requests-table tr:hover {{
                background: #f8f9fa;
            }}
            .status-badge {{
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
            }}
            .status-active {{ background: #d4edda; color: #155724; }}
            .status-in-progress {{ background: #fff3cd; color: #856404; }}
            .status-completed {{ background: #e2e3e5; color: #383d41; }}
            .status-cancelled {{ background: #f8d7da; color: #721c24; }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>Панель администратора</h1>
                <div class="admin-info">
                    Вы вошли как администратор: <strong>{username}</strong>
                </div>
                <a href="/" class="back-link">На главную</a>
            </header>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number">{stats['total']}</div>
                    <div class="stat-label">Всего заявок</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['active']}</div>
                    <div class="stat-label">Активных</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['social']}</div>
                    <div class="stat-label">Социальных</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['ecological']}</div>
                    <div class="stat-label">Экологических</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['other']}</div>
                    <div class="stat-label">Других</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['in_progress']}</div>
                    <div class="stat-label">Выполняются</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['completed']}</div>
                    <div class="stat-label">Завершены</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['cancelled']}</div>
                    <div class="stat-label">Отменены</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{stats['users']}</div>
                    <div class="stat-label">Пользователей</div>
                </div>
            </div>
            
            <div class="admin-actions">
                <div class="action-card">
                    <h2>Управление заявками</h2>
                    <a href="/view" class="btn btn-view">Активные заявки</a>
                    <a href="/archive" class="btn btn-archive">Архив заявок</a>
                    <a href="/my_requests" class="btn btn-all">Все заявки</a>
                </div>
                
                <div class="action-card">
                    <h2>Управление пользователями</h2>
                    <button class="btn btn-manage" onclick="alert('В разработке')">Список пользователей</button>
                    <button class="btn btn-danger" onclick="alert('В разработке')">Удалить пользователя</button>
                </div>
                
                <div class="action-card">
                    <h2>Системные действия</h2>
                    <button class="btn btn-manage" onclick="location.reload()">Обновить статистику</button>
                    <button class="btn btn-danger" onclick="if(confirm('Очистить весь архив?')) location.href='/admin/clear_archive'">Очистить архив</button>
                </div>
            </div>
            
            <div class="recent-requests">
                <h2>Последние заявки</h2>
                <table class="requests-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Название</th>
                            <th>Автор</th>
                            <th>Классификация</th>
                            <th>Статус</th>
                            <th>Создано</th>
                            <th>Действия</th>
                        </tr>
                    </thead>
                    <tbody>
                        {recent_requests_html}
                    </tbody>
                </table>
            </div>
        </div>
    </body>
    </html>
    ''')

# ==================== ОБНОВЛЕНИЕ СТАТУСА ====================

@app.route('/update_status/<int:index>', methods=['POST'])
def update_status(index):
    """Обновление статуса заявки"""
    username = check_auth(request.cookies)
    if not username:
        return redirect('/login')
    
    if index < 0 or index >= len(all_requests):
        return "Заявка не найдена", 404
    
    request_data = all_requests[index]
    new_status = request.form.get('status')
    
    # Проверяем права
    if username != request_data.get('author') and not is_admin(username):
        return "Доступ запрещен", 403
    
    # Проверяем допустимость смены статуса
    valid_transitions = {
        STATUS_ACTIVE: [STATUS_IN_PROGRESS, STATUS_COMPLETED, STATUS_CANCELLED],
        STATUS_IN_PROGRESS: [STATUS_COMPLETED, STATUS_CANCELLED],
        STATUS_COMPLETED: [],
        STATUS_CANCELLED: []
    }
    
    current_status = request_data.get('status', STATUS_ACTIVE)
    if new_status not in valid_transitions.get(current_status, []):
        return "Недопустимая смена статуса", 400
    
    # Обновляем статус
    request_data['status'] = new_status
    request_data['updated_at'] = datetime.now().strftime('%d.%m.%Y %H:%M')
    all_requests[index] = request_data
    save_data(all_requests)
    
    return redirect(f'/request/{index}')

# ==================== УДАЛЕНИЕ ЗАЯВКИ ====================

@app.route('/delete/<int:index>', methods=['POST'])
def delete_request(index):
    """Удаление заявки"""
    username = check_auth(request.cookies)
    if not username:
        return redirect('/login')
    
    if index < 0 or index >= len(all_requests):
        return "Заявка не найдена", 404
    
    request_data = all_requests[index]
    
    # Проверяем права (только автор или администратор)
    if username != request_data.get('author') and not is_admin(username):
        return "Доступ запрещен", 403
    
    # Удаляем заявку
    all_requests.pop(index)
    save_data(all_requests)
    
    return redirect('/my_requests')

# ==================== ЗАПУСК СЕРВЕРА ====================

if __name__ == '__main__':
    print("=" * 70)
    print("Добрые дела рядом - СИСТЕМА УПРАВЛЕНИЯ ЗАЯВКАМИ")
    print("=" * 70)
    print("Адрес для входа: http://localhost:5015")
    print("=" * 70)
    print("Тестовый аккаунт администратора:")
    print("  Логин: admin")
    print("  Пароль: admin123")
    print("=" * 70)
    print("Классификации заявок:")
    print("  1. Социальное волонтерство")
    print("  2. Экологическое волонтерство")
    print("  3. Другое")
    print("=" * 70)
    print("Основные возможности системы:")
    print("1. Регистрация и авторизация пользователей")
    print("2. Создание заявок с различными статусами и классификациями")
    print("3. Отклик на заявки других пользователей")
    print("4. Управление статусами заявок (активна/выполняется/завершена/отменена)")
    print("5. Архив завершенных и отмененных заявок")
    print("6. Панель администратора с полным доступом")
    print("7. Разграничение прав доступа к заявкам")
    print("=" * 70)
    app.run(debug=True, host='0.0.0.0', port=5015)
