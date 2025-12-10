from flask import Flask, url_for, request, redirect, abort, render_template
import os
from lab1 import lab1
from lab2 import lab2
from lab3 import lab3
from lab4 import lab4
from lab5 import lab5
from lab6 import lab6
from lab7 import lab7
from lab8 import lab8
from rgz import rgz
import datetime
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'секретно-секретный секрет')
app.config['DB_TYPE'] = os.getenv('DB_TYPE', 'postgres')
app.register_blueprint(lab1)
app.register_blueprint(lab2)
app.register_blueprint(lab3)
app.register_blueprint(lab4)
app.register_blueprint(lab5)
app.register_blueprint(lab6)
app.register_blueprint(lab7)
app.register_blueprint(lab8)
app.register_blueprint(rgz)
# список логов
access_log = []


@app.errorhandler(404)
def not_found(err):
    path = url_for("static", filename="lab1/404.jpg")
    user_ip = request.remote_addr
    access_time = str(datetime.datetime.now())
    requested_url = request.url

    # добавляем запись в журнал
    access_log.append(f"[{access_time}] пользователь {user_ip} зашёл на адрес: {requested_url}")

    log_html = "<ul>"
    for entry in reversed(access_log):  # последние записи сверху
        log_html += f"<li>{entry}</li>"
    log_html += "</ul>"

    return '''
<!doctype html>
<html>
    <head>
        <meta charset="utf-8">
        <title>404 Not Found</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #f0f4f8;
                color: #333;
                margin: 0;
                padding: 20px;
                text-align: center;
            }
            h1 {
                margin-top: 20px;
                color: #c0392b;
            }
            img {
                margin-top: 20px;
                max-width: 50%;
                height: auto;
                border-radius: 10px;
                box-shadow: 0 8px 20px rgba(0,0,0,0.2);
            }
            .info {
                margin: 20px 0;
                font-size: 1.1em;
            }
            .log {
                margin-top: 30px;
                text-align: left;
                display: inline-block;
                max-width: 90%;
                background: #fff;
                padding: 15px;
                border-radius: 10px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            }
            .log ul { padding-left: 20px; }
            .log li { margin-bottom: 5px; }
            a {
                color: #3a6ea5;
                font-weight: bold;
                text-decoration: none;
            }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1>нет такой страницы...</h1>
        <img src="''' + path + '''">
        <div class="info">
            Ваш IP: '''+str(user_ip)+'''<br>
            Дата доступа: '''+access_time+'''<br>
            <a href="/">На главную</a>
        </div>
        <div class="log">
            <h2>Журнал посещений</h2>
            '''+log_html+'''
        </div>
    </body>
</html>
''', 404


@app.route("/index")
@app.route("/")
def index():
    return '''
<!doctype html>
<html>
    <head>
        <meta charset="utf-8">
        <title>НГТУ, ФБ, Лабораторные работы</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 0; 
                padding: 0; 
                background: #f0f4f8; 
                text-align:center
            }
            header { 
                background: #3a6ea5; 
                color: white; 
                padding: 20px; 
                text-align: center; 
                margin: 20px
            }
            a { 
                color: #3a6ea5; 
                font-weight: bold
            }
            a:hover { text-decoration: underline}
            footer { 
                background: #e0e0e0; 
                text-align: center; 
                padding: 10px; 
                position: fixed; 
                bottom: 0; 
                width: 100%
            }
        </style>
    </head>
    <body>
        <header>
            <h1>НГТУ, ФБ, WEB-программирование, часть 2. Список лабораторных</h1>
        </header>
        <nav>
            <a href="/lab1">Первая лабораторная</a><br>
            <a href="/lab2">Вторая лабораторная</a><br>
            <a href="/lab3">Третья лабораторная</a><br>
            <a href="/lab4">Четвертая лабораторная</a><br>
            <a href="/lab5">Пятая лабораторная</a><br>
            <a href="/lab6">Шестая лабораторная</a><br>
            <a href="/lab7">Седьмая лабораторная</a><br>
            <a href="/lab8">Восьмая лабораторная</a><br>
            <a href="/rgz">Планирование отпусков (РГЗ)</a><br>
        </nav>
        <footer>
            Витлева Анастасия Александровна, ФБИ-31, 3 курс, 2025
        </footer>
    </body>
</html>
'''


# Обработчик ошибки 500
@app.errorhandler(500)
def internal_error(err):
    return '''
<!doctype html>
<html>
    <head>
        <meta charset="utf-8">
        <title>Ошибка сервера</title>
        <style>
            body {
                text-align: center;
                background: #f8d7da;
                color: #721c24;
                margin: 0;
                padding: 50px;
            }
        </style>
    </head>
    <body>
        <h1>Внутренняя ошибка сервера (500)</h1>
        <p>Произошла непредвиденная ошибка на сервере</p>
    </body>
</html>
''', 500
