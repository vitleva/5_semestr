from flask import Blueprint, render_template, request, session, current_app, redirect, url_for
from werkzeug.security import check_password_hash, generate_password_hash
import psycopg2
from psycopg2.extras import RealDictCursor
import sqlite3
from os import path
from datetime import date, timedelta, datetime

rgz = Blueprint('rgz', __name__, template_folder='templates/rgz')

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

    db_path = current_app.config.get('DB_PATH')
    if not db_path:
        db_path = path.join(current_app.root_path, "database.db")

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    return conn, cur

def db_close(conn, cur):
    try:
        conn.commit()
    except Exception as e:
        print("[rgz] Warning: commit failed:", e)
    try:
        cur.close()
    except Exception:
        pass
    try:
        conn.close()
    except Exception:
        pass

@rgz.route('/rgz/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('rgz/login.html', login=session.get('login'))
    login_val = request.form.get('login', '').strip()
    password = request.form.get('password', '')
    if not login_val or not password:
        return render_template('rgz/login.html', error='Заполните поля')
    conn, cur = db_connect()
    try:
        if current_app.config.get('DB_TYPE') == 'postgres':
            cur.execute("SELECT * FROM users WHERE login=%s;", (login_val,))
        else:
            cur.execute("SELECT * FROM users WHERE login=?;", (login_val,))
        user = cur.fetchone()
    finally:
        db_close(conn, cur)
    if not user or not check_password_hash(user['password'], password):
        return render_template('rgz/login.html', error='Неправильный логин/пароль')
    session['login'] = login_val
    return redirect(url_for('rgz.main'))

@rgz.route('/rgz/logout')
def logout():
    session.pop('login', None)
    return redirect(url_for('rgz.main'))

@rgz.route('/rgz/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('rgz/register.html')
    login_val = (request.form.get('login') or '').strip()
    name = (request.form.get('name') or '').strip()
    password = request.form.get('password') or ''
    if not login_val or not password or not name:
        return render_template('rgz/register.html', error='Заполните все поля', name=name, login=login_val)
    # валидация логина
    import re
    if not re.match(r'^[\w\-\.\@\!]+$', login_val):
        return render_template('rgz/register.html', error='Логин содержит недопустимые символы', name=name, login=login_val)
    pwd_hash = generate_password_hash(password)
    conn, cur = db_connect()
    try:
        if current_app.config.get('DB_TYPE') == 'postgres':
            cur.execute("SELECT login FROM users WHERE login=%s;", (login_val,))
            if cur.fetchone():
                db_close(conn, cur)
                return render_template('rgz/register.html', error='Такой пользователь уже есть', name=name, login=login_val)
            cur.execute("INSERT INTO users (login, name, password) VALUES (%s, %s, %s);", (login_val, name, pwd_hash))
        else:
            cur.execute("SELECT login FROM users WHERE login=?;", (login_val,))
            if cur.fetchone():
                db_close(conn, cur)
                return render_template('rgz/register.html', error='Такой пользователь уже есть', name=name, login=login_val)
            cur.execute("INSERT INTO users (login, name, password) VALUES (?, ?, ?);", (login_val, name, pwd_hash))
    finally:
        db_close(conn, cur)
    session['login'] = login_val
    return redirect(url_for('rgz.main'))

@rgz.route('/rgz/delete_account', methods=['POST'])
def delete_account():
    login_val = session.get('login')
    if not login_val:
        return redirect(url_for('rgz.login'))
    conn, cur = db_connect()
    try:
        if current_app.config.get('DB_TYPE') == 'postgres':
            cur.execute("DELETE FROM users WHERE login=%s;", (login_val,))
        else:
            cur.execute("DELETE FROM users WHERE login=?;", (login_val,))
    finally:
        db_close(conn, cur)
    session.pop('login', None)
    return redirect(url_for('rgz.main'))

def weeks_for_year(year):
    # produce list of dicts: {'week': n, 'start': 'YYYY-MM-DD','end':'YYYY-MM-DD'}
    weeks = []
    # находим первый понедельник первой недели
    dt = date(year, 1, 4)
    # понедельник:
    monday = dt - timedelta(days=dt.isoweekday() - 1)
    # перебираем недели до 1-го понедельника след. года
    idx = 1
    while monday.year <= year:
        start = monday
        end = start + timedelta(days=6)
        if start.year > year and end.year > year:
            break
        weeks.append({'week': idx, 'start': start.isoformat(), 'end': end.isoformat()})
        idx += 1
        monday = monday + timedelta(days=7)
        if idx > 60:
            break
    return weeks

@rgz.route('/rgz/json-rpc/', methods=['POST'])
def api():
    data = request.json or {}
    method = data.get('method')
    id = data.get('id')
    # info: возвращаем недели на год и информацию о бронях
    if method == 'info':
        year = data.get('params') or datetime.now().year
        try:
            year = int(year)
        except Exception:
            year = datetime.now().year
        weeks = weeks_for_year(year)
        # получаем брони на этот год
        conn, cur = db_connect()
        try:
            if current_app.config.get('DB_TYPE') == 'postgres':
                cur.execute("SELECT v.week, u.login, u.name FROM vacations v JOIN users u ON v.user_id = u.id WHERE v.year = %s;", (year,))
                rows = cur.fetchall()
            else:
                cur.execute("SELECT v.week, u.login, u.name FROM vacations v JOIN users u ON v.user_id = u.id WHERE v.year = ?;", (year,))
                rows = cur.fetchall()
            bookings = {}
            for r in rows:
                # r может быть словарем или sqlite Row
                if isinstance(r, dict):
                    w = r['week']; bookings[w] = {'login': r['login'], 'name': r['name']}
                else:
                    w = r['week']; bookings[w] = {'login': r['login'], 'name': r['name']}
        finally:
            db_close(conn, cur)
        # добавляем информацию о бронировании в недели
        for w in weeks:
            wk = w['week']
            if wk in bookings:
                w['booked'] = True
                w['by'] = bookings[wk]['login']
                w['by_name'] = bookings[wk]['name']
            else:
                w['booked'] = False
                w['by'] = ''
                w['by_name'] = ''
        return {'jsonrpc': '2.0', 'result': {'weeks': weeks, 'year': year, 'user': session.get('login')}, 'id': id}

    # для некоторых методов проверяем логин
    login = session.get('login')
    if not login:
        return {'jsonrpc': '2.0', 'error': {'code': 1, 'message': 'Unauthorized'}, 'id': id}

    # броинрование недели
    if method == 'booking':
        params = data.get('params')
        try:
            year = int(params.get('year'))
            week = int(params.get('week'))
        except Exception:
            return {'jsonrpc': '2.0', 'error': {'code': -32602, 'message': 'Invalid params'}, 'id': id}

        # проверка: неделя не должна быть в прошлом 
        try:
            # сначала пробуем использовать fromisocalendar (Python 3.8+)
            try:
                week_start = date.fromisocalendar(year, week, 1)
            except AttributeError:
                # fallback: вычисляем monday of ISO week 1 (contains Jan 4), затем прибавляем (week-1)*7 дней
                jan4 = date(year, 1, 4)
                monday_week1 = jan4 - timedelta(days=jan4.isoweekday() - 1)
                week_start = monday_week1 + timedelta(weeks=week-1)
            week_end = week_start + timedelta(days=6)
        except Exception:
            return {'jsonrpc': '2.0', 'error': {'code': -32602, 'message': 'Invalid params (week/year)'} , 'id': id}

        if week_end < date.today():
            return {'jsonrpc': '2.0', 'error': {'code': 6, 'message': 'Past week (cannot modify past weeks)'}, 'id': id}

        conn, cur = db_connect()
        try:
            # получаем user id
            if current_app.config.get('DB_TYPE') == 'postgres':
                cur.execute("SELECT id FROM users WHERE login=%s;", (login,))
                row = cur.fetchone()
            else:
                cur.execute("SELECT id FROM users WHERE login=?;", (login,))
                row = cur.fetchone()
            if not row:
                db_close(conn, cur)
                return {'jsonrpc': '2.0', 'error': {'code': -32602, 'message': 'User not found'}, 'id': id}
            user_id = row['id'] if isinstance(row, dict) else (row[0] if isinstance(row, (list, tuple)) else row['id'])

            # сколько броней у пользователя за год
            if current_app.config.get('DB_TYPE') == 'postgres':
                cur.execute("SELECT COUNT(*) FROM vacations WHERE year=%s AND user_id=%s;", (year, user_id))
                cnt_row = cur.fetchone()
                cnt_val = list(cnt_row.values())[0] if isinstance(cnt_row, dict) else list(cnt_row)[0]
            else:
                cur.execute("SELECT COUNT(*) FROM vacations WHERE year=? AND user_id=?;", (year, user_id))
                cnt_row = cur.fetchone()
                cnt_val = list(cnt_row)[0] if isinstance(cnt_row, (list, tuple)) else list(cnt_row)[0]

            cnt_int = int(cnt_val)

            if cnt_int >= 4:
                db_close(conn, cur)
                return {'jsonrpc': '2.0', 'error': {'code': 5, 'message': 'Limit reached (4 weeks)'}, 'id': id}

            # проверка свободно ли
            if current_app.config.get('DB_TYPE') == 'postgres':
                cur.execute("SELECT user_id FROM vacations WHERE year=%s AND week=%s;", (year, week))
                r = cur.fetchone()
            else:
                cur.execute("SELECT user_id FROM vacations WHERE year=? AND week=?;", (year, week))
                r = cur.fetchone()
            if r:
                db_close(conn, cur)
                return {'jsonrpc': '2.0', 'error': {'code': 2, 'message': 'Already booked'}, 'id': id}

            # добавляем бронь
            if current_app.config.get('DB_TYPE') == 'postgres':
                cur.execute("INSERT INTO vacations (user_id, year, week) VALUES (%s, %s, %s);", (user_id, year, week))
            else:
                cur.execute("INSERT INTO vacations (user_id, year, week) VALUES (?, ?, ?);", (user_id, year, week))
        finally:
            db_close(conn, cur)
        return {'jsonrpc': '2.0', 'result': 'success', 'id': id}


    # отмена бронирования (только автор бронирования)
    if method == 'cancellation':
        params = data.get('params')
        try:
            year = int(params.get('year'))
            week = int(params.get('week'))
        except Exception:
            return {'jsonrpc': '2.0', 'error': {'code': -32602, 'message': 'Invalid params'}, 'id': id}

        # проверка: неделя не должна быть в прошлом
        try:
            try:
                week_start = date.fromisocalendar(year, week, 1)
            except AttributeError:
                jan4 = date(year, 1, 4)
                monday_week1 = jan4 - timedelta(days=jan4.isoweekday() - 1)
                week_start = monday_week1 + timedelta(weeks=week-1)
            week_end = week_start + timedelta(days=6)
        except Exception:
            return {'jsonrpc': '2.0', 'error': {'code': -32602, 'message': 'Invalid params (week/year)'}, 'id': id}

        if week_end < date.today():
            return {'jsonrpc': '2.0', 'error': {'code': 6, 'message': 'Past week (cannot modify past weeks)'}, 'id': id}

        conn, cur = db_connect()
        try:
            if current_app.config.get('DB_TYPE') == 'postgres':
                cur.execute("SELECT id FROM users WHERE login=%s;", (login,))
                row = cur.fetchone()
            else:
                cur.execute("SELECT id FROM users WHERE login=?;", (login,))
                row = cur.fetchone()
            if not row:
                db_close(conn, cur)
                return {'jsonrpc': '2.0', 'error': {'code': -32602, 'message': 'User not found'}, 'id': id}
            user_id = row['id'] if isinstance(row, dict) else (row[0] if isinstance(row, (list, tuple)) else row['id'])

            # проверяем текущую бронь
            if current_app.config.get('DB_TYPE') == 'postgres':
                cur.execute("SELECT user_id FROM vacations WHERE year=%s AND week=%s;", (year, week))
                r = cur.fetchone()
            else:
                cur.execute("SELECT user_id FROM vacations WHERE year=? AND week=?;", (year, week))
                r = cur.fetchone()
            if not r:
                db_close(conn, cur)
                return {'jsonrpc': '2.0', 'error': {'code': 3, 'message': 'Not rented'}, 'id': id}

            owner_id = r['user_id'] if isinstance(r, dict) else (list(r)[0] if isinstance(r, (list, tuple)) else r[0])
            if owner_id != user_id:
                db_close(conn, cur)
                return {'jsonrpc': '2.0', 'error': {'code': 4, 'message': 'Not tenant'}, 'id': id}

            # удаляем
            if current_app.config.get('DB_TYPE') == 'postgres':
                cur.execute("DELETE FROM vacations WHERE year=%s AND week=%s;", (year, week))
            else:
                cur.execute("DELETE FROM vacations WHERE year=? AND week=?;", (year, week))
        finally:
            db_close(conn, cur)
        return {'jsonrpc': '2.0', 'result': 'success', 'id': id}


    return {'jsonrpc': '2.0', 'error': {'code': -32601, 'message': 'Method not found'}, 'id': id}

@rgz.route('/rgz/')
def main():
    return render_template('rgz/index.html', login=session.get('login'))
