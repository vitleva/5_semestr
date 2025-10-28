from flask import Blueprint, render_template, request, redirect, session
lab4 = Blueprint('lab4', __name__)

@lab4.route('/lab4')
def lab():
    return render_template('lab4/lab4.html')

@lab4.route('/lab4/div-form')
def div_form():
    return render_template('lab4/div-form.html')

@lab4.route('/lab4/div', methods = ['POST'])
def div():
    x1 = request.form.get('x1')
    x2 = request.form.get('x2')
    if x1 == '' or x2 == '':
        return render_template('/lab4/div.html', error='Оба поля должны быть заполнены!')
    if x2 == '0':
        return render_template('/lab4/div.html', error='На ноль делить нельзя!')
    x1 = int(x1)
    x2 = int(x2)
    result = x1 / x2
    return render_template('lab4/div.html', x1=x1, x2=x2, result=result)

@lab4.route('/lab4/sum-form')
def sum_form():
    return render_template('lab4/sum-form.html')

@lab4.route('/lab4/sum', methods=['POST'])
def sum_():
    x1 = request.form.get('x1')
    x2 = request.form.get('x2')
    x1 = int(x1) if x1 != '' else 0
    x2 = int(x2) if x2 != '' else 0
    result = x1 + x2
    return render_template('lab4/sum.html', x1=x1, x2=x2, result=result)

@lab4.route('/lab4/sub-form')
def sub_form():
    return render_template('lab4/sub-form.html')

@lab4.route('/lab4/sub', methods=['POST'])
def sub():
    x1 = request.form.get('x1')
    x2 = request.form.get('x2')
    if x1 == '' or x2 == '':
        return render_template('lab4/sub.html', error='Оба поля должны быть заполнены!')
    x1 = int(x1)
    x2 = int(x2)
    result = x1 - x2
    return render_template('lab4/sub.html', x1=x1, x2=x2, result=result)

@lab4.route('/lab4/mul-form')
def mul_form():
    return render_template('lab4/mul-form.html')

@lab4.route('/lab4/mul', methods=['POST'])
def mul():
    x1 = request.form.get('x1')
    x2 = request.form.get('x2')
    x1 = int(x1) if x1 != '' else 1
    x2 = int(x2) if x2 != '' else 1
    result = x1 * x2
    return render_template('lab4/mul.html', x1=x1, x2=x2, result=result)

@lab4.route('/lab4/pow-form')
def pow_form():
    return render_template('lab4/pow-form.html')

@lab4.route('/lab4/pow', methods=['POST'])
def pow_():
    x1 = request.form.get('x1')
    x2 = request.form.get('x2')
    if x1 == '' or x2 == '':
        return render_template('lab4/pow.html', error='Оба поля должны быть заполнены!')
    x1 = int(x1)
    x2 = int(x2)
    if x1 == 0 and x2 == 0:
        return render_template('lab4/pow.html', error='0⁰ не имеет смысла!')
    result = x1 ** x2
    return render_template('lab4/pow.html', x1=x1, x2=x2, result=result)

tree_count = 0

@lab4.route('/lab4/tree', methods = ['GET', 'POST'])
def tree():
    global tree_count
    if request.method == 'GET':
        return render_template('lab4/tree.html', tree_count=tree_count)
    
    operation = request.form.get('operation')

    if operation == 'cut' and tree_count > 0:
        tree_count -= 1
    elif operation == 'plant' and tree_count < 10:
        tree_count += 1

    return redirect('/lab4/tree')

users = [
    {'login': 'alex', 'password': '123', 'name': 'Алексей Смирнов', 'gender': 'm'},
    {'login': 'bob', 'password': '555', 'name': 'Роберт Браун', 'gender': 'm'},
    {'login': 'vitleva', 'password': '666', 'name': 'Анастасия Витлева', 'gender': 'f'},
    {'login': 'lame', 'password': '444', 'name': 'Лариса Мельникова', 'gender': 'f'}
]

@lab4.route('/lab4/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if 'login' in session:
            authorized = True
            login = session['login']
            # ищем имя по логину
            user = next((u for u in users if u['login'] == login), None)
            name = user['name'] if user else login
        else:
            authorized = False
            login = ''
            name = ''
        return render_template('lab4/login.html', authorized=authorized, login=login, name=name)
    
    login_input = request.form.get('login', '').strip()
    password_input = request.form.get('password', '').strip()

    # Проверка на пустые поля
    if not login_input:
        error = 'Не введён логин'
        return render_template('lab4/login.html', error=error, authorized=False, login='')
    if not password_input:
        error = 'Не введён пароль'
        return render_template('lab4/login.html', error=error, authorized=False, login=login_input)

    for user in users:
        if login_input == user['login'] and password_input == user['password']:
            session['login'] = login_input
            return redirect('/lab4/login')
    
    error = 'Неверные логин и/или пароль'
    return render_template('lab4/login.html', error=error, authorized=False, login=login_input)

@lab4.route('/lab4/logout', methods=['POST'])
def logout():
    session.pop('login', None)
    return redirect('/lab4/login')

@lab4.route('/lab4/fridge', methods=['GET', 'POST'])
def fridge():
    if request.method == 'GET':
        return render_template('lab4/fridge.html')

    temp = request.form.get('temperature')

    if temp == '' or temp is None:
        return render_template('lab4/fridge.html', error='Ошибка: не задана температура')

    try:
        temp = int(temp)
    except ValueError:
        return render_template('lab4/fridge.html', error='Ошибка: введите число')

    if temp < -100 or temp > 100:
        # защита от неадекватных значений 
        return render_template('lab4/fridge.html', error='Ошибка: температура вне диапазона!')

    # проверяем диапазоны:
    if temp < -12:
        msg = 'Не удалось установить температуру — слишком низкое значение'
        return render_template('lab4/fridge.html', error=msg)
    elif temp > -1:
        msg = 'Не удалось установить температуру — слишком высокое значение'
        return render_template('lab4/fridge.html', error=msg)
    elif -12 <= temp <= -9:
        snowflakes = 3
    elif -8 <= temp <= -5:
        snowflakes = 2
    elif -4 <= temp <= -1:
        snowflakes = 1
    else:
        snowflakes = 0  # на случай непредусмотренного диапазона

    return render_template('lab4/fridge.html', temp=temp, snowflakes=snowflakes)

@lab4.route('/lab4/grain', methods=['GET', 'POST'])
def grain():
    prices = {
        'ячмень': 12000,
        'овёс': 8500,
        'пшеница': 9000,
        'рожь': 15000
    }

    if request.method == 'GET':
        return render_template('lab4/grain.html', prices=prices)

    grain_type = request.form.get('grain')
    weight = request.form.get('weight')

    # проверка
    if not weight:
        return render_template('lab4/grain.html', prices=prices, error='Ошибка: не указан вес!')
    try:
        weight = float(weight)
    except ValueError:
        return render_template('lab4/grain.html', prices=prices, error='Ошибка: вес должен быть числом!')

    if weight <= 0:
        return render_template('lab4/grain.html', prices=prices, error='Ошибка: вес должен быть больше нуля!')
    if weight > 100:
        return render_template('lab4/grain.html', prices=prices, error='Такого объёма сейчас нет в наличии!')

    # расчет стоимости
    price_per_ton = prices.get(grain_type, 0)
    total = price_per_ton * weight
    discount_text = None

    if weight > 10:
        discount = total * 0.1
        total -= discount
        discount_text = f'Применена скидка 10% за большой объём (−{discount:,.0f} руб).'.replace(',', ' ')

    return render_template(
        'lab4/grain.html',
        prices=prices,
        grain_type=grain_type,
        weight=weight,
        total=total,
        discount_text=discount_text
    )

@lab4.route('/lab4/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('lab4/register.html')

    login = request.form.get('login')
    password = request.form.get('password')
    confirm = request.form.get('confirm')
    name = request.form.get('name')
    gender = request.form.get('gender')

    # проверки
    if not login:
        return render_template('lab4/register.html', error='Не введён логин')
    if not password:
        return render_template('lab4/register.html', error='Не введён пароль')
    if password != confirm:
        return render_template('lab4/register.html', error='Пароль и подтверждение не совпадают')
    for user in users:
        if user['login'] == login:
            return render_template('lab4/register.html', error='Такой логин уже существует')

    # добавляем нового пользователя
    users.append({'login': login, 'password': password, 'name': name, 'gender': gender})
    session['login'] = login  # авторизуем сразу
    return redirect('/lab4/login')

@lab4.route('/lab4/users')
def users_list():
    if 'login' not in session:
        return redirect('/lab4/login')
    return render_template('lab4/users.html', users=users, current_user=session['login'])

@lab4.route('/lab4/delete/<login>', methods=['POST'])
def delete_user(login):
    global users
    if 'login' not in session or session['login'] != login:
        return redirect('/lab4/login')
    users = [u for u in users if u['login'] != login]
    session.pop('login', None)
    return redirect('/lab4/login')

@lab4.route('/lab4/edit/<login>', methods=['GET', 'POST'])
def edit_user(login):
    if 'login' not in session or session['login'] != login:
        return redirect('/lab4/login')

    user = next((u for u in users if u['login'] == login), None)
    if not user:
        return redirect('/lab4/users')

    if request.method == 'GET':
        return render_template('lab4/edit.html', user=user)

    new_login = request.form.get('login')
    new_name = request.form.get('name')
    new_password = request.form.get('password')
    confirm = request.form.get('confirm')
    gender = request.form.get('gender')

    if new_password or confirm:
        if new_password != confirm:
            return render_template('lab4/edit.html', user=user, error='Пароли не совпадают')
        user['password'] = new_password  # изменяем только если введено
    user['login'] = new_login
    user['name'] = new_name
    user['gender'] = gender

    session['login'] = new_login
    return redirect('/lab4/users')

