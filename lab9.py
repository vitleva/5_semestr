from flask import Blueprint, render_template, request, session, current_app, redirect
import random
import sqlite3
from os import path
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import check_password_hash, generate_password_hash

lab9 = Blueprint('lab9', __name__)

MAX_OPENED = 3
TOTAL_BOXES = 10

GREETINGS = [
    "🎄 С Новым годом! Дай Бог без депрессии в новом году!",
    "❄️ Пусть в новом году у Деда Мороза не придется просить... пощады",
    "🎁 С Новым Годом, пусть он заберет еще больше нервных клеток!",
    "☃️ Ура! Еще 365 поводов для нервного срыва!",
    "✨ Желаю в Новом году еще больше эмоциональных качель!",
    "🎅 С Новым Годом! Желаю дожить до следующей сессии!",
    "🎆 В Новом Году желаю килограмм новопассита бесплатно!",
    "🌟 В Новом Году желаю дождаться Макана из армии!",
    "🍾 Пусть Новый год переплюнет старый: депрессия заиграет новыми красками!",
    "💫 В Новогоднюю ночь желаю не уехать в дурдом (хотя может это не так плохо)"
]

GIFT_IMAGES = [
    "/static/lab9/gifts/gift1.jpg",
    "/static/lab9/gifts/gift2.jpg",
    "/static/lab9/gifts/gift3.jpg",
    "/static/lab9/gifts/gift4.jpg",
    "/static/lab9/gifts/gift5.jpg",
    "/static/lab9/gifts/gift6.jpg",
    "/static/lab9/gifts/gift7.jpg",
    "/static/lab9/gifts/gift8.jpg",
    "/static/lab9/gifts/gift9.jpg",
    "/static/lab9/gifts/gift10.jpg",
]

BOX_IMAGES = [
    "/static/lab9/boxes/box1.png",
    "/static/lab9/boxes/box2.png",
    "/static/lab9/boxes/box3.png",
    "/static/lab9/boxes/box4.png",
    "/static/lab9/boxes/box5.png",
    "/static/lab9/boxes/box6.png",
    "/static/lab9/boxes/box7.png",
    "/static/lab9/boxes/box8.png",
    "/static/lab9/boxes/box9.png",
    "/static/lab9/boxes/box10.png",
]

BOX_POSITIONS = [
    (20, 2),
    (40, 3),
    (66, 1),
    (15, 35),
    (35, 37),
    (55, 36),
    (71, 29),
    (25, 65),
    (45, 65),
    (65, 62)
]



def db_connect():
    if current_app.config.get('DB_TYPE') == 'postgres':
        conn = psycopg2.connect(
            host='127.0.0.1',
            database='anastasia_vitleva_knowledge_base',
            user='anastasia_vitleva_knowledge_base',
            password='123'
        )
        cur = conn.cursor(cursor_factory=RealDictCursor)
        return conn, cur

    db_path = current_app.config.get('DB_PATH') or path.join(current_app.root_path, "database.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    return conn, cur

def db_close(conn, cur):
    try:
        conn.commit()
    except Exception as e:
        print("[lab9] Warning: commit failed:", e)
    try:
        cur.close()
    except Exception:
        pass
    try:
        conn.close()
    except Exception:
        pass

# --- Роуты авторизации ---
@lab9.route('/lab9/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        conn, cur = db_connect()
        try:
            if current_app.config.get('DB_TYPE') == 'postgres':
                cur.execute("SELECT * FROM users WHERE login = %s;", (login,))
            else:
                cur.execute("SELECT * FROM users WHERE login = ?;", (login,))
            user = cur.fetchone()
            if user and check_password_hash(user['password'], password):
                session['login'] = login
                return redirect('/lab9')
            else:
                error = "Неверный логин или пароль"
        finally:
            db_close(conn, cur)
    return render_template('lab9/login.html', error=error)

@lab9.route('/lab9/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        if not login or not password:
            error = "Заполните все поля"
        else:
            conn, cur = db_connect()
            try:
                if current_app.config.get('DB_TYPE') == 'postgres':
                    cur.execute("SELECT id FROM users WHERE login = %s;", (login,))
                else:
                    cur.execute("SELECT id FROM users WHERE login = ?;", (login,))
                if cur.fetchone():
                    error = "Логин уже занят"
                else:
                    hashed = generate_password_hash(password)
                    if current_app.config.get('DB_TYPE') == 'postgres':
                        cur.execute("INSERT INTO users (login, password) VALUES (%s, %s);", (login, hashed))
                    else:
                        cur.execute("INSERT INTO users (login, password) VALUES (?, ?);", (login, hashed))
                    session['login'] = login
                    return redirect('/lab9')
            finally:
                db_close(conn, cur)
    return render_template('lab9/register.html', error=error)

# --- API открывания подарков ---
@lab9.route('/lab9/api/open', methods=['POST'])
def open_box():
    data = request.get_json()
    box_id = data.get('id')
    if session.get('opened_count', 0) >= MAX_OPENED: 
        return {'error': 'Можно открыть не более 3 коробок'}, 403

    conn, cur = db_connect()
    try:
        if current_app.config.get('DB_TYPE') == 'postgres':
            cur.execute("SELECT * FROM gift_boxes WHERE id = %s;", (box_id,))
        else:
            cur.execute("SELECT * FROM gift_boxes WHERE id = ?;", (box_id,))
        box = cur.fetchone()
        if not box:
            return {'error': 'Коробка не найдена'}, 404

        restricted = bool(box.get('restricted', False))
        if restricted and 'login' not in session:
            return {'error': 'Только для авторизованных пользователей'}, 403

        if box['opened']:
            return {'error': 'Коробка уже пуста'}, 400

        if current_app.config.get('DB_TYPE') == 'postgres':
            cur.execute("UPDATE gift_boxes SET opened = 1 WHERE id = %s;", (box_id,))
        else:
            cur.execute("UPDATE gift_boxes SET opened = 1 WHERE id = ?;", (box_id,))
    finally:
        db_close(conn, cur)

    session['opened_count'] = session.get('opened_count', 0) + 1
    return {
        'greeting': box['greeting'],
        'gift_image': box['gift_image'],
        'opened_count': session['opened_count']
    }

# --- API перезаполнения всех коробок ---
@lab9.route('/lab9/api/refill', methods=['POST'])
def refill_boxes():
    if 'login' not in session:
        return {'success': False, 'error': 'Только для авторизованных'}

    conn, cur = db_connect()
    try:
        if current_app.config.get('DB_TYPE') == 'postgres':
            cur.execute("UPDATE gift_boxes SET opened = 0;")
        else:
            cur.execute("UPDATE gift_boxes SET opened = 0;")
    finally:
        db_close(conn, cur)
    session['opened_count'] = 0
    return {'success': True}

# --- Главная страница ---
@lab9.route('/lab9')
def main():
    if 'opened_count' not in session:
        session['opened_count'] = 0

    conn, cur = db_connect()
    try:
        cur.execute("SELECT * FROM gift_boxes;")
        boxes = [dict(row) for row in cur.fetchall()]
    finally:
        db_close(conn, cur)

    unopened = sum(1 for b in boxes if b['opened'] == 0)

    return render_template(
        'lab9/index.html',
        boxes=boxes,
        unopened=unopened,
        opened_count=session['opened_count']
    )

@lab9.route('/lab9/logout')
def logout():
    session.pop('login', None)
    return redirect('/lab9')