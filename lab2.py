from flask import Blueprint, url_for, redirect, abort, render_template
lab2 = Blueprint('lab2', __name__)

# список логов
access_log = []

@lab2.route('/lab2/a')
def a():
    return 'без слэша'


@lab2.route('/lab2/a/')
def a2():
    return 'со слэшем'

flowers = [
    {"name": "карасик", "price": 300},
    {"name": "вобла", "price": 310},
    {"name": "кальмар", "price": 320},
    {"name": "форель", "price": 330},
    {"name": "шпроты", "price": 300},
]


@lab2.route('/lab2/all_flowers/<int:flower_id>')
def id_flowers(flower_id):
    if flower_id >= len(flowers):
        abort(404)
    else:
        flower = list(flowers[flower_id].values())[0]
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


@lab2.route('/lab2/add_flower/<name>')
def add_flower(name):
    flowers.append({"name": name, "price": 300})
    return redirect(url_for("lab2.all_flowers"))


@lab2.route('/lab2/add_flower/')
def add_flower_no_name():
    return "Вы не задали имя закуски", 400


@lab2.route('/lab2/all_flowers')
def all_flowers():
    return render_template("lab2/flowers.html", flowers=flowers)


@lab2.route("/lab2/del_flower/<int:flower_id>")
def del_flower(flower_id):
    if 0 <= flower_id < len(flowers):
        flowers.pop(flower_id)
        return redirect(url_for("lab2.all_flowers"))
    else:
        abort(404)


@lab2.route('/lab2/del_flower/')
def del_flower_no_name():
    return "Вы не задали имя цветка", 400


@lab2.route('/lab2/example')
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
    return render_template('lab2/example.html',
                           name=name,
                           number=number,
                           group=group,
                           course=course,
                           fruits=fruits)


@lab2.route('/lab2')
def lab():
    return render_template('lab2/lab2.html')


@lab2.route('/lab2/filters')
def filters():
    phrase = 'О <b>сколько</b> <u>нам</u> <i>открытий</i> чудных...'
    return render_template('lab2/filter.html', phrase = phrase)


@lab2.route('/lab2/clear_flowers')
def clear_flowers():
    flowers.clear()
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


@lab2.route('/lab2/calc/<int:a>/<int:b>')
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


@lab2.route('/lab2/calc/')
def calc_default():
    return redirect('/lab2/calc/1/1')


@lab2.route('/lab2/calc/<int:a>')
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


@lab2.route('/lab2/books')
def show_books():
    return render_template('lab2/books.html', books=books)

energy_drinks = [
    {"name": "Red Bull", "desc": "Классический энергетик из Австрии, один из самых популярных в мире.", "image": "lab2/redbull.jpg"},
    {"name": "Monster Energy", "desc": "Американский энергетик с большим количеством сахара и кофеина.", "image": "lab2/monster.jpg"},
    {"name": "Burn", "desc": "Энергетический напиток от Coca-Cola, часто встречается в России.", "image": "lab2/burn.jpg"},
    {"name": "Adrenaline Rush", "desc": "Популярный российский энергетик с разными вкусами.", "image": "lab2/adrenaline.jpg"},
    {"name": "Drive Me", "desc": "Бюджетный энергетик, часто встречается в магазинах РФ.", "image": "lab2/drive.jpg"},
    {"name": "Gorilla", "desc": "Российский энергетик, спонсор киберспорта и рэп-культуры.", "image": "lab2/gorilla.jpg"},
    {"name": "Flash Up", "desc": "Недорогой энергетик, продаётся в дискаунтерах.", "image": "lab2/flash.jpg"},
    {"name": "Effect", "desc": "Немецкий энергетический напиток с мягким вкусом.", "image": "lab2/effect.jpg"},
    {"name": "Rockstar Energy", "desc": "Американский энергетик с десятками вкусовых вариаций.", "image": "lab2/rockstar.jpg"},
    {"name": "Crazy Wolf", "desc": "Европейский энергетик, недорогой вариант для студентов.", "image": "lab2/crazywolf.jpg"},
    {"name": "Tornado Energy", "desc": "Российский бренд энергетиков, часто встречается в супермаркетах.", "image": "lab2/tornado.jpg"},
    {"name": "Black Monster", "desc": "Вариация Monster в чёрной банке, более крепкий вкус.", "image": "lab2/blackmonster.jpg"},
    {"name": "Hype Energy", "desc": "Энергетик из Великобритании, ориентирован на спорт и музыку.", "image": "lab2/hype.jpg"},
    {"name": "LitEnergy", "desc": "Российский энергетик, выпускаемый блогером Михаилом Литивном.", "image": "lab2/lit.jpg"},
    {"name": "Celsius", "desc": "Функциональный энергетик для ЗОЖ, без сахара.", "image": "lab2/celsius.jpg"},
    {"name": "Mother Energy", "desc": "Популярный бренд в Австралии и Новой Зеландии.", "image": "lab2/mother.jpg"},
    {"name": "V Energy", "desc": "Новозеландский энергетик с мягким вкусом и зелёной банкой.", "image": "lab2/v.jpg"},
    {"name": "Bang Energy", "desc": "Американский энергетик с аминокислотами и витаминами.", "image": "lab2/bang.jpg"},
    {"name": "Revo Energy", "desc": "Энергетик, ориентированный на молодёжь, яркий дизайн банок.", "image": "lab2/revo.jpg"},
    {"name": "E-ON", "desc": "Российский энергетик от Coca-Cola с необычными вкусами.", "image": "lab2/eon.jpg"},
]


@lab2.route('/lab2/energy')
def energy():
    return render_template("lab2/energy.html", drinks=energy_drinks)
