from flask import Blueprint, render_template, request, redirect, session, current_app, url_for, flash
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
from os import path

lab5 = Blueprint('lab5', __name__)

@lab5.route('/lab5')
def lab():
    return render_template('lab5/lab5.html', login=session.get('login'))

def db_connect():
    if current_app.config['DB_TYPE'] == 'postgres':
        conn = psycopg2.connect(
            host = '127.0.0.1',
            database = 'anastasia_vitleva_knowledge_base',
            user = 'anastasia_vitleva_knowledge_base',
            password = '123'
        )
        cur = conn.cursor(cursor_factory = RealDictCursor)
    else:
        dir_path = path.dirname(path.realpath(__file__))
        db_path = path.join(dir_path, "database.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

    return conn, cur

def db_close(conn, cur):
    conn.commit()
    cur.close()
    conn.close()

@lab5.route('/lab5/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('lab5/register.html')
    
    login = request.form.get('login')
    name = request.form.get('name') or ''
    password = request.form.get('password')

    if not login or not password:
        return render_template('lab5/register.html', error='Заполните все поля', name=name, login=login)
    
    conn, cur = db_connect()

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT login FROM users WHERE login=%s;", (login,))
    else:
        cur.execute("SELECT login FROM users WHERE login=?;", (login,))
    
    if cur.fetchone():
        db_close(conn, cur)
        return render_template('lab5/register.html', error="Такой пользователь уже существует", name=name, login=login)
    
    password_hash = generate_password_hash(password)
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("INSERT INTO users (login, password, name) VALUES (%s, %s, %s);", (login, password_hash, name))
    else:
        cur.execute("INSERT INTO users (login, password, name) VALUES (?, ?, ?);", (login, password_hash, name))
    db_close(conn, cur)
    return render_template('lab5/success.html', login=login)

@lab5.route('/lab5/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('lab5/login.html')
    
    login_val = request.form.get('login')
    password = request.form.get('password')

    if not (login_val and password):
        return render_template('lab5/login.html', error='Заполните поля')
    
    conn, cur = db_connect()

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT * FROM users WHERE login=%s;", (login_val, ))
    else:
        cur.execute("SELECT * FROM users WHERE login=?;", (login_val, ))
    user = cur.fetchone()

    if not user:
        db_close(conn, cur)
        return render_template('lab5/login.html',
                               error='Логин и/или пароль неверны')
    
    if not check_password_hash(user['password'], password):
        db_close(conn, cur)
        return render_template('lab5/login.html',
                               error='Логин и/или пароль неверны')
    
    session['login'] = login_val
    db_close(conn, cur)
    return render_template('lab5/success_login.html', login=login_val)

@lab5.route('/lab5/logout')
def logout():
    session.pop('login', None)
    return redirect(url_for('lab5.lab'))

@lab5.route('/lab5/create', methods = ['GET', 'POST'])
def create():
    login_val = session.get('login')
    if not login_val:
        return redirect('/lab5/login')
    
    if request.method == 'GET':
        return render_template('lab5/create_article.html')
    
    title = (request.form.get('title') or '').strip()
    article_text = (request.form.get('article_text') or '').strip()
    is_public = True if request.form.get('is_public') == 'on' else False

    if not title or not article_text:
        return render_template('lab5/create_article.html', error='Тема и текст не могут быть пустыми', title=title, article_text=article_text, is_public=is_public)

    conn, cur = db_connect()

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT * FROM users WHERE login=%s;", (login_val, ))
    else:
        cur.execute("SELECT * FROM users WHERE login=?;", (login_val, ))
    user = cur.fetchone()
    if not user:
        db_close(conn, cur)
        return redirect('/lab5/login')

    user_id = user['id']

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("INSERT INTO articles(user_id, title, article_text, is_favorite, is_public, likes) VALUES (%s, %s, %s, %s, %s, %s);",
                    (user_id, title, article_text, False, is_public, 0))
    else:
        cur.execute("INSERT INTO articles(user_id, title, article_text, is_favorite, is_public, likes) VALUES (?, ?, ?, ?, ?, ?);",
                    (user_id, title, article_text, 0, 1 if is_public else 0, 0))
    
    db_close(conn, cur)
    return redirect('/lab5')

@lab5.route('/lab5/list')
def list():
    login_val = session.get('login')
    conn, cur = db_connect()

    current_user_id = None
    if login_val:
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("SELECT id FROM users WHERE login=%s;", (login_val,))
        else:
            cur.execute("SELECT id FROM users WHERE login=?;", (login_val,))
        row = cur.fetchone()
        if row:
            current_user_id = row['id']

    if current_app.config['DB_TYPE'] == 'postgres':
        if current_user_id:
            cur.execute("""
                SELECT a.*, u.login as author_login, u.name as author_name
                FROM articles a
                JOIN users u ON a.user_id = u.id
                WHERE a.is_public = TRUE OR a.user_id = %s
                ORDER BY a.is_favorite DESC NULLS LAST, a.id DESC;
            """, (current_user_id,))
        else:
            cur.execute("""
                SELECT a.*, u.login as author_login, u.name as author_name
                FROM articles a
                JOIN users u ON a.user_id = u.id
                WHERE a.is_public = TRUE
                ORDER BY a.is_favorite DESC NULLS LAST, a.id DESC;
            """)
        articles = cur.fetchall()
    else:
        if current_user_id:
            cur.execute("""
                SELECT a.*, u.login as author_login, u.name as author_name
                FROM articles a
                JOIN users u ON a.user_id = u.id
                WHERE a.is_public = 1 OR a.user_id = ?
                ORDER BY a.is_favorite DESC, a.id DESC;
            """, (current_user_id,))
        else:
            cur.execute("""
                SELECT a.*, u.login as author_login, u.name as author_name
                FROM articles a
                JOIN users u ON a.user_id = u.id
                WHERE a.is_public = 1
                ORDER BY a.is_favorite DESC, a.id DESC;
            """)
        articles = cur.fetchall()

    db_close(conn, cur)
    if not articles:
        message = "Пока нет статей." if current_user_id else "Пока нет публичных статей."
        return render_template('lab5/articles.html', articles=[], message=message, login=login_val)
    return render_template('lab5/articles.html', articles=articles, login=login_val)

@lab5.route('/lab5/article/<int:article_id>/edit', methods=['GET', 'POST'])
def edit_article(article_id):
    login_val = session.get('login')
    if not login_val:
        return redirect('/lab5/login')

    conn, cur = db_connect()
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT a.*, u.login as author_login FROM articles a JOIN users u ON a.user_id = u.id WHERE a.id=%s;", (article_id,))
    else:
        cur.execute("SELECT a.*, u.login as author_login FROM articles a JOIN users u ON a.user_id = u.id WHERE a.id=?;", (article_id,))
    article = cur.fetchone()
    if not article:
        db_close(conn, cur)
        return redirect('/lab5/list')

    if article['author_login'] != login_val:
        db_close(conn, cur)
        return "Нет доступа для редактирования этой статьи", 403

    if request.method == 'GET':
        db_close(conn, cur)
        return render_template('lab5/edit_article.html', article=article)

    title = (request.form.get('title') or '').strip()
    article_text = (request.form.get('article_text') or '').strip()
    is_public = True if request.form.get('is_public') == 'on' else False
    is_favorite = True if request.form.get('is_favorite') == 'on' else False

    if not title or not article_text:
        db_close(conn, cur)
        return render_template('lab5/edit_article.html', article=article, error='Тема и текст не могут быть пустыми')

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("""
            UPDATE articles SET title=%s, article_text=%s, is_public=%s, is_favorite=%s WHERE id=%s;
        """, (title, article_text, is_public, is_favorite, article_id))
    else:
        cur.execute("""
            UPDATE articles SET title=?, article_text=?, is_public=?, is_favorite=? WHERE id=?;
        """, (title, article_text, 1 if is_public else 0, 1 if is_favorite else 0, article_id))

    db_close(conn, cur)
    return redirect('/lab5/list')

@lab5.route('/lab5/article/<int:article_id>/delete', methods=['POST'])
def delete_article(article_id):
    login_val = session.get('login')
    if not login_val:
        return redirect('/lab5/login')

    conn, cur = db_connect()
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT a.id, u.login FROM articles a JOIN users u ON a.user_id = u.id WHERE a.id=%s;", (article_id,))
    else:
        cur.execute("SELECT a.id, u.login FROM articles a JOIN users u ON a.user_id = u.id WHERE a.id=?;", (article_id,))
    row = cur.fetchone()
    if not row:
        db_close(conn, cur)
        return redirect('/lab5/list')
    if row['login'] != login_val and (row.get('author_login') != login_val):
        db_close(conn, cur)
        return "Нет доступа для удаления этой статьи", 403

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("DELETE FROM articles WHERE id=%s;", (article_id,))
    else:
        cur.execute("DELETE FROM articles WHERE id=?;", (article_id,))
    db_close(conn, cur)
    return redirect('/lab5/list')

@lab5.route('/lab5/users')
def users_list():
    conn, cur = db_connect()
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT login, name FROM users ORDER BY login;")
        users = cur.fetchall()
    else:
        cur.execute("SELECT login, name FROM users ORDER BY login;")
        users = cur.fetchall()
    db_close(conn, cur)
    return render_template('lab5/users.html', users=users, login=session.get('login'))

@lab5.route('/lab5/profile', methods=['GET','POST'])
def profile():
    login_val = session.get('login')
    if not login_val:
        return redirect('/lab5/login')
    conn, cur = db_connect()
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT * FROM users WHERE login=%s;", (login_val,))
    else:
        cur.execute("SELECT * FROM users WHERE login=?;", (login_val,))
    user = cur.fetchone()

    if request.method == 'GET':
        db_close(conn, cur)
        return render_template('lab5/profile.html', user=user)

    new_name = request.form.get('name') or ''
    new_password = request.form.get('password') or ''
    confirm = request.form.get('confirm') or ''

    if new_password or confirm:
        if new_password != confirm:
            db_close(conn, cur)
            return render_template('lab5/profile.html', user=user, error='Пароли не совпадают')
        password_hash = generate_password_hash(new_password)
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("UPDATE users SET name=%s, password=%s WHERE login=%s;", (new_name, password_hash, login_val))
        else:
            cur.execute("UPDATE users SET name=?, password=? WHERE login=?;", (new_name, password_hash, login_val))
    else:
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("UPDATE users SET name=%s WHERE login=%s;", (new_name, login_val))
        else:
            cur.execute("UPDATE users SET name=? WHERE login=?;", (new_name, login_val))

    db_close(conn, cur)
    return redirect('/lab5')
