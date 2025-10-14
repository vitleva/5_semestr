from flask import Blueprint, render_template, request, make_response, redirect
lab3 = Blueprint('lab3', __name__)

@lab3.route('/lab3')
def lab():
    name = request.cookies.get('name') or 'Аноним'
    name_color = request.cookies.get('name_color')
    age = request.cookies.get('age') or 'Неизвестный'
    return render_template('lab3/lab3.html', name=name, name_color=name_color, age=age)

@lab3.route('/lab3/cookie')
def cookie():
    resp = make_response(redirect('/lab3'))
    resp.set_cookie('name', 'Alex', max_age=5)
    resp.set_cookie('age', '20')
    resp.set_cookie('name_color', 'magenta')
    return resp

@lab3.route('/lab3/del_cookie')
def del_cookie():
    resp = make_response(redirect('/lab3'))
    resp.set_cookie('name')
    resp.set_cookie('age')
    resp.set_cookie('name_color')
    return resp

@lab3.route('/lab3/form1')
def form1():
    errors = {}
    user = request.args.get('user')
    if user == '':
        errors['user'] = 'Заполните поле!'

    age = request.args.get('age')
    if age == '':
        errors['age'] = 'Заполните поле!'

    sex = request.args.get('sex')
    return render_template('lab3/form1.html', user=user,age=age, sex=sex, errors=errors)

@lab3.route('/lab3/order')
def order():
    return render_template('lab3/order.html')

@lab3.route('/lab3/pay')
def pay():
    price = 0
    drink = request.args.get('drink')
    if drink == 'coffee':
        price = 120
    elif drink == 'black-tea':
        price = 80
    else:
        price = 70
    
    if request.args.get('milk') == 'on':
        price += 30
    if request.args.get('sugar') == 'on':
        price += 10
    return render_template('lab3/pay.html', price=price, drink=drink)

@lab3.route('/lab3/success')
def success():
    price = request.args.get('price')
    return render_template('lab3/success.html', price=price)

@lab3.route('/lab3/settings')
def settings():
    color = request.args.get('color')
    bg_color = request.args.get('bg_color')
    font_size = request.args.get('font_size')
    font_family = request.args.get('font_family')
    
    if any([color, bg_color, font_size, font_family]):
        resp = make_response(redirect('/lab3/settings'))
        if color:
            resp.set_cookie('color', color)
        if bg_color:
            resp.set_cookie('bg_color', bg_color)
        if font_size:
            resp.set_cookie('font_size', font_size)
        if font_family:
            resp.set_cookie('font_family', font_family)
        return resp
    
    color = request.cookies.get('color')
    bg_color = request.cookies.get('bg_color')
    font_size = request.cookies.get('font_size')
    font_family = request.cookies.get('font_family')
    
    resp = make_response(render_template('lab3/settings.html', 
                                       color=color, 
                                       bg_color=bg_color, 
                                       font_size=font_size, 
                                       font_family=font_family))
    return resp

@lab3.route('/lab3/train_ticket')
def train_ticket():
    errors = {}
    data = {}

    data['fio'] = request.args.get('fio', '').strip()
    data['berth'] = request.args.get('berth', '')
    data['linen'] = request.args.get('linen') == 'on'
    data['baggage'] = request.args.get('baggage') == 'on'
    data['age'] = request.args.get('age', '').strip()
    data['from_city'] = request.args.get('from_city', '').strip()
    data['to_city'] = request.args.get('to_city', '').strip()
    data['date'] = request.args.get('date', '').strip()
    data['insurance'] = request.args.get('insurance') == 'on'

    if request.args:
        if not data['fio']:
            errors['fio'] = 'Введите ФИО'
        if not data['berth']:
            errors['berth'] = 'Выберите полку'
        if not data['age']:
            errors['age'] = 'Введите возраст'
        else:
            try:
                age_val = int(data['age'])
                if age_val < 1 or age_val > 120:
                    errors['age'] = 'Возраст должен быть от 1 до 120'
                data['age'] = age_val
            except ValueError:
                errors['age'] = 'Возраст должен быть числом'
        if not data['from_city']:
            errors['from_city'] = 'Введите пункт выезда'
        if not data['to_city']:
            errors['to_city'] = 'Введите пункт назначения'
        if not data['date']:
            errors['date'] = 'Выберите дату поездки'

        if not errors:
            price = 1000 if data['age'] >= 18 else 700
            if data['berth'] in ['нижняя', 'нижняя боковая']:
                price += 100
            if data['linen']:
                price += 75
            if data['baggage']:
                price += 250
            if data['insurance']:
                price += 150
            data['price'] = price
            data['ticket_type'] = 'Детский билет' if data['age'] < 18 else 'Взрослый билет'

            return render_template('lab3/train_ticket_result.html', data=data)

    return render_template('lab3/train_ticket.html', errors=errors, data=data)
