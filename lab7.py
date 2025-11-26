from flask import Blueprint, render_template, request, abort

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
    if film['description'] == '':
        return {'description': 'Заполните описание'}, 400
    if film.get('title', '') == '' and film.get('title_ru', '') != '':
        film['title'] = film['title_ru']
    films[id] = film
    return films[id]

@lab7.route('/lab7/rest-api/films/', methods=['POST'])
def add_film():
    film = request.get_json()
    if film['description'] == '':
        return {'description': 'Заполните описание'}, 400
    if film.get('title', '') == '' and film.get('title_ru', '') != '':
        film['title'] = film['title_ru']
    films.append(film)
    new_id = len(films)-1
    return str(new_id), 201
