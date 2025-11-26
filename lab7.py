from flask import Blueprint, render_template, request, abort
from datetime import datetime

lab7 = Blueprint('lab7', __name__)

@lab7.route('/lab7/')
def main():
    return render_template('lab7/index.html')

films = [
    {
        "title": "Zeleniy Slonik",
        "title_ru": "Зелёный слоник",
        "year": 1999,
        "description": "Два младших офицера, сидя в одной камере "
        "на гауптвахте, вынуждены решать острые социальные и психологические "
        "вопросы в небольшом пространстве."
    },
    {
        "title": "Yolki",
        "title_ru": "Ёлки",
        "year": 2010,
        "description": "Новогодние события происходят в 11 городах: "
        "Калининграде, Казани, Перми, Уфе, Бавлах, Екатеринбурге, Красноярске, "
        "Якутске, Новосибирске, Санкт-Петербурге и Москве. Герои фильма — таксист "
        "и поп-дива, бизнесмен и актер, сноубордист и лыжник, студент и пенсионерка, "
        "пожарный и директриса, вор и милиционер, гастарбайтер и президент России. "
        "Все они оказываются в самый канун Нового года в очень непростой ситуации, "
        "выйти из которой им поможет только чудо… или Теория шести рукопожатий, "
        "согласно которой каждый человек на земле знает другого через шесть знакомых."
    },
    {
        "title": "Fight Club",
        "title_ru": "Бойцовский клуб",
        "year": 1999,
        "description": "Сотрудник страховой компании страдает хронической бессонницей "
        "и отчаянно пытается вырваться из мучительно скучной жизни. Однажды в очередной "
        "командировке он встречает некоего Тайлера Дёрдена — харизматического торговца "
        "мылом с извращенной философией. Тайлер уверен, что самосовершенствование — удел "
        "слабых, а единственное, ради чего стоит жить, — саморазрушение."
    },
]

def validate_film(film):
    errors = {}
    title = film.get('title', '')
    title_ru = film.get('title_ru', '')
    year = film.get('year', None)
    description = film.get('description', '')

    title_ru_str = title_ru.strip() if isinstance(title_ru, str) else ''
    title_str = title.strip() if isinstance(title, str) else ''
    desc_str = description.strip() if isinstance(description, str) else ''

    if title_ru_str == '':
        errors['title_ru'] = 'Заполните русское название'
    if title_str == '' and title_ru_str == '':
        errors['title'] = 'Заполните название на оригинальном языке'

    if isinstance(year, str):
        year_raw = year.strip()
        if year_raw == '':
            year_val = None
        else:
            try:
                year_val = int(year_raw)
            except Exception:
                year_val = 'invalid'
    else:
        try:
            year_val = int(year) if year is not None else None
        except Exception:
            year_val = 'invalid'

    current_year = datetime.now().year
    if year_val == 'invalid':
        errors['year'] = 'Год должен быть числом'
    elif year_val is None:
        errors['year'] = f'Заполните год выпуска (от 1895 до {current_year})'
    else:
        if year_val < 1895 or year_val > current_year:
            errors['year'] = f'Год должен быть в диапазоне 1895–{current_year}'
        else:
            film['year'] = year_val

    if desc_str == '':
        errors['description'] = 'Заполните описание'
    elif len(desc_str) > 2000:
        errors['description'] = 'Описание не должно превышать 2000 символов'
    else:
        film['description'] = desc_str

    if film.get('title', '').strip() == '' and title_ru_str != '':
        film['title'] = title_ru_str

    if film.get('title_ru', '').strip() == '':
        film['title_ru'] = title_ru_str

    return errors

@lab7.route('/lab7/rest-api/films/', methods=['GET'])
def get_films():
    return films

@lab7.route('/lab7/rest-api/films/<int:id>', methods=['GET'])
def get_film(id):
    if id < 0 or id >= len(films):
        abort(404)
    return films[id]

@lab7.route('/lab7/rest-api/films/<int:id>', methods=['DELETE'])
def del_film(id):
    if id < 0 or id >= len(films):
        abort(404)
    del films[id]
    return '', 204

@lab7.route('/lab7/rest-api/films/<int:id>', methods=['PUT'])
def put_film(id):
    if id < 0 or id >= len(films):
        abort(404)
    film = request.get_json()
    if film is None:
        return {'error': 'Invalid JSON'}, 400
    errors = validate_film(film)
    if errors:
        return errors, 400
    films[id] = film
    return films[id]

@lab7.route('/lab7/rest-api/films/', methods=['POST'])
def add_film():
    film = request.get_json()
    if film is None:
        return {'error': 'Invalid JSON'}, 400
    errors = validate_film(film)
    if errors:
        return errors, 400
    films.append(film)
    new_id = len(films)-1
    return str(new_id), 201
