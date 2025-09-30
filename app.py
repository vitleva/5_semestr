from flask import Flask, url_for, request, redirect, abort, render_template
import datetime
app = Flask(__name__)

# список логов
access_log = []

@app.errorhandler(404)
def not_found(err):
    path = url_for("static", filename="404.jpg")
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
            <a href="/lab2">Вторая лабораторная</a>
        </nav>
        <footer>
            Витлева Анастасия Александровна, ФБИ-31, 3 курс, 2025
        </footer>
    </body>
</html>
'''

@app.route("/lab1")
def lab1():
    return '''
<!doctype html>
<html>
    <head>
        <meta charset="utf-8">
        <title>Лабораторная 1</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 20px; 
                background: #f9f9f9; 
                color: #333; 
                line-height: 1.6
            }
            a { 
                color: #3a6ea5; 
                font-weight: bold
            }
            a:hover { text-decoration: underline}
        </style>
    </head>
    <body>
        <p>Flask — фреймворк для создания веб-приложений на языке программирования Python, использующий набор 
        инструментов Werkzeug, а также шаблонизатор Jinja2. Относится к категории так называемых микрофреймворков 
        — минималистичных каркасов веб-приложений, сознательно предоставляющих лишь самые базовые возможности.</p>
        <p><a href="/">На главную</a></p>

        <h2>Список роутов</h2>
        <ul>
            <li><a href="/index">/index</a></li>
            <li><a href="/">/</a></li>
            <li><a href="/lab1/web">/web</a></li>
            <li><a href="/lab1/author">/author</a></li>
            <li><a href="/lab1/image">/image</a></li>
            <li><a href="/lab1/counter">/counter</a></li>
            <li><a href="/lab1/counter/reset">/counter/reset</a></li>
            <li><a href="/lab1/info">/info</a></li>
            <li><a href="/lab1/created">/created</a></li>
            <li><a href="/lab1/error/400">/error/400</a></li>
            <li><a href="/lab1/error/401">/error/401</a></li>
            <li><a href="/lab1/error/402">/error/402</a></li>
            <li><a href="/lab1/error/403">/error/403</a></li>
            <li><a href="/lab1/error/405">/error/405</a></li>
            <li><a href="/lab1/error/418">/error/418</a></li>
            <li><a href="/lab1/cause_error">/cause_error</a></li>
        </ul>
    </body>
</html>
'''


@app.route("/lab1/web")
def web():
    return """<!DOCTYPE html>
        <html>
           <body>
               <h1>web-сервер на flask</h1>
               <a href="l/ab1/author">author</a>
           </body>
        </html>""", 200, {
            'X-server': "sample",
            'Content-Type': 'text/plain; charset=utf-8'}

@app.route("/lab1/author")
def author():
    name = "Витлева Анастасия Александровна"
    group = "ФБИ-31"
    faculty = "ФБ"

    return """<!doctype html>
        <html>
            <body>
                <p>Студент: """ + name + """</p>
                <p>Группа: """ + group + """</p>
                <p>Факультет: """ + faculty + """</p>
                <a href="/lab1/web">web</a>
            </body>
        </html>"""

@app.route('/lab1/image')
def image():
    path = url_for("static", filename="makak.jpg")
    style = url_for("static", filename="lab1.css")
    return '''
<!doctype html>
<html>
    <head>
       <link rel="stylesheet" href="''' + style + '''">
   </head>
    <body>
        <h1>Макак</h1>
        <img src="''' + path + '''">
    </body>
</html>''', 200, {
        'Content-Language': 'ru',
        'X-Author': 'Vitleva A.A.',    
        'X-Framework': 'Flask'}

count = 0
@app.route('/lab1/counter')
def counter():
    global count
    count+=1
    time = datetime.datetime.today
    url = request.url
    client_ip = request.remote_addr
    return '''
<!doctype html>
<html>
    <body>
        Сколько раз сюда заходили: '''+ str(count) + '''
        <hr>
        Дата и время: ''' + str(time) + '''<br>
        Запрошенный адрес: ''' + str(url) + '''<br>
        Ваш IP-адрес: ''' + str(client_ip) + '''<br>
        <a href="/lab1/counter/reset">Сбросить счётчик</a>
    </body>
</html>'''

@app.route('/lab1/info')
def info():
    return redirect('/lab1/author')

@app.route('/lab1/created')
def created():
    return '''
<!doctype html>
<html>
    <body>
        <h1>Создано успешно</h1>
        <div><i>что-то создано...</i></div>
    </body>
</html>
''', 201

@app.route('/lab1/counter/reset')
def reset_counter():
    global count
    count = 0
    return '''
<!doctype html>
<html>
    <body>
        <p>счётчик был сброшен</p>
        <a href="/lab1/counter">назад к счётчику</a>
    </body>
</html>
'''

@app.route("/lab1/error/400")
def error_400():
    return "неверный запрос", 400

@app.route("/lab1/error/401")
def error_401():
    return "требуется авторизация", 401

@app.route("/lab1/error/402")
def error_402():
    return "требуется оплата", 402

@app.route("/lab1/error/403")
def error_403():
    return "доступ запрещён", 403

@app.route("/lab1/error/405")
def error_405():
    return "метод не разрешён", 405

@app.route("/lab1/error/418")
def error_418():
    return "я чайник", 418

# Роут, который вызывает ошибку
@app.route("/lab1/cause_error")
def cause_error():
    # Пример: деление на ноль
    x = 1 / 0
    return str(x)

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

@app.route('/lab2/a')
def a():
    return 'без слэша'

@app.route('/lab2/a/')
def a2():
    return 'со слэшем'

flower_list = ["карасик", "вобла", "кальмар", "форель", "семга"]

@app.route('/lab2/flowers/<int:flower_id>')
def flowers(flower_id):
    if flower_id >= len(flower_list):
        abort(404)
    else:
        flower = flower_list[flower_id]
        return f'''
<!doctype html>
<html>
    <body>
        <h1>Вы выбрали закусь</h1>
        <p>Пивной букет из: <b>{flower}</b></p>
        <a href="/lab2/all_flowers">Посмотреть все закуски</a>
    </body>
</html>
'''
    
@app.route('/lab2/add_flower/<name>')
def add_flower(name):
    flower_list.append(name)
    return f'''
<!doctype html>
<html>
    <body>
    <h1>Добавлена новая закусь</h1>
    <p>Название новой закуси: {name}</p>
    <p>Всего закусок: {len(flower_list)}</p>
    <p>Полный список: {flower_list}</p>
    </body>
</html>
'''

@app.route('/lab2/add_flower/')
def add_flower_no_name():
    return "Вы не задали имя цветка", 400

@app.route('/lab2/all_flowers')
def all_flowers():
    return f'''
<!doctype html>
<html>
    <body>
        <h1>Список закусок</h1>
        <p>Всего закусок: {len(flower_list)}</p>
        <ul>
            {''.join(f"<li>{flower}</li>" for i, flower in enumerate(flower_list))}
        </ul>
        <a href="/lab2">Назад к лабораторной 2</a>
    </body>
</html>
'''



@app.route('/lab2/example')
def example():
    name = 'Витлева Анастасия'
    number = 2
    group = 'ФБИ-31'
    course = 3
    fruits = [
            {'name':'яблоки', 'price': 100},
            {'name':'груши', 'price': 120},
            {'name':'апельсины', 'price': 80},
            {'name':'мандарины', 'price': 95},
            {'name':'манго', 'price': 321},
        ]
    return render_template('example.html',
                           name=name,
                           number=number,
                           group=group,
                           course=course,
                           fruits=fruits)

@app.route('/lab2')
def lab2():
    return render_template('lab2.html')

@app.route('/lab2/filters')
def filters():
    phrase = 'О <b>сколько</b> <u>нам</u> <i>открытий</i> чудных...'
    return render_template('filter.html', phrase = phrase)

@app.route('/lab2/clear_flowers')
def clear_flowers():
    flower_list.clear()
    return '''
<!doctype html>
<html>
    <body>
        <h1>Список очищен</h1>
        <p>Все закуски удалены.</p>
        <a href="/lab2/all_flowers">Посмотреть все закуски</a>
    </body>
</html>
'''

@app.route('/lab2/calc/<int:a>/<int:b>')
def calc(a, b):
    result = f"""
<!doctype html>
<html>
    <body>
        <h1>Калькулятор</h1>
        <p>{a} + {b} = {a + b}</p>
        <p>{a} - {b} = {a - b}</p>
        <p>{a} * {b} = {a * b}</p>
        <p>{a} / {b} = {"нельзя делить на 0" if b == 0 else a / b}</p>
        <p>{a} ** {b} = {a ** b}</p>
        <hr>
        <a href="/lab2">Назад к лабораторной 2</a>
    </body>
</html>
"""
    return result

@app.route('/lab2/calc/')
def calc_default():
    return redirect('/lab2/calc/1/1')

@app.route('/lab2/calc/<int:a>')
def calc_one_arg(a):
    return redirect(f'/lab2/calc/{a}/1')

books = [
    {"author": "Фёдор Достоевский", "title": "Преступление и наказание", "genre": "Роман", "pages": 672},
    {"author": "Лев Толстой", "title": "Война и мир", "genre": "Исторический роман", "pages": 1225},
    {"author": "Александр Пушкин", "title": "Евгений Онегин", "genre": "Роман в стихах", "pages": 384},
    {"author": "Михаил Булгаков", "title": "Мастер и Маргарита", "genre": "Роман", "pages": 480},
    {"author": "Иван Тургенев", "title": "Отцы и дети", "genre": "Роман", "pages": 320},
    {"author": "Антон Чехов", "title": "Вишнёвый сад", "genre": "Пьеса", "pages": 120},
    {"author": "Николай Гоголь", "title": "Мёртвые души", "genre": "Роман", "pages": 432},
    {"author": "Владимир Набоков", "title": "Лолита", "genre": "Роман", "pages": 368},
    {"author": "Рэй Брэдбери", "title": "451° по Фаренгейту", "genre": "Фантастика", "pages": 249},
    {"author": "Джордж Оруэлл", "title": "1984", "genre": "Антиутопия", "pages": 328}
]

@app.route('/lab2/books')
def show_books():
    return render_template('books.html', books=books)

energy_drinks = [
    {"name": "Red Bull", "desc": "Классический энергетик из Австрии, один из самых популярных в мире.", "image": "redbull.jpg"},
    {"name": "Monster Energy", "desc": "Американский энергетик с большим количеством сахара и кофеина.", "image": "monster.jpg"},
    {"name": "Burn", "desc": "Энергетический напиток от Coca-Cola, часто встречается в России.", "image": "burn.jpg"},
    {"name": "Adrenaline Rush", "desc": "Популярный российский энергетик с разными вкусами.", "image": "adrenaline.jpg"},
    {"name": "Drive Me", "desc": "Бюджетный энергетик, часто встречается в магазинах РФ.", "image": "drive.jpg"},
    {"name": "Gorilla", "desc": "Российский энергетик, спонсор киберспорта и рэп-культуры.", "image": "gorilla.jpg"},
    {"name": "Flash Up", "desc": "Недорогой энергетик, продаётся в дискаунтерах.", "image": "flash.jpg"},
    {"name": "Effect", "desc": "Немецкий энергетический напиток с мягким вкусом.", "image": "effect.jpg"},
    {"name": "Rockstar Energy", "desc": "Американский энергетик с десятками вкусовых вариаций.", "image": "rockstar.jpg"},
    {"name": "Crazy Wolf", "desc": "Европейский энергетик, недорогой вариант для студентов.", "image": "crazywolf.jpg"},
    {"name": "Tornado Energy", "desc": "Российский бренд энергетиков, часто встречается в супермаркетах.", "image": "tornado.jpg"},
    {"name": "Black Monster", "desc": "Вариация Monster в чёрной банке, более крепкий вкус.", "image": "blackmonster.jpg"},
    {"name": "Hype Energy", "desc": "Энергетик из Великобритании, ориентирован на спорт и музыку.", "image": "hype.jpg"},
    {"name": "LitEnergy", "desc": "Российский энергетик, выпускаемый блогером Михаилом Литивном.", "image": "lit.jpg"},
    {"name": "Celsius", "desc": "Функциональный энергетик для ЗОЖ, без сахара.", "image": "celsius.jpg"},
    {"name": "Mother Energy", "desc": "Популярный бренд в Австралии и Новой Зеландии.", "image": "mother.jpg"},
    {"name": "V Energy", "desc": "Новозеландский энергетик с мягким вкусом и зелёной банкой.", "image": "v.jpg"},
    {"name": "Bang Energy", "desc": "Американский энергетик с аминокислотами и витаминами.", "image": "bang.jpg"},
    {"name": "Revo Energy", "desc": "Энергетик, ориентированный на молодёжь, яркий дизайн банок.", "image": "revo.jpg"},
    {"name": "E-ON", "desc": "Российский энергетик от Coca-Cola с необычными вкусами.", "image": "eon.jpg"},
]

@app.route('/lab2/energy')
def energy():
    return render_template("energy.html", drinks=energy_drinks)






