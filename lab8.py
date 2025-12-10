from flask import Blueprint, session, render_template, request, redirect, current_app, abort, g
from db import db
from db.models import users, articles
from flask_login import login_user, login_required, current_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import or_

lab8 = Blueprint('lab8', __name__)

@lab8.route('/lab8')
def lab():
    return render_template('lab8/lab8.html')

@lab8.route('/lab8/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('lab8/register.html')
    
    login_form = request.form.get('login')
    password_form = request.form.get('password')

    if not login_form:
        return render_template('lab8/register.html',
                               error='Имя пользователя не должно быть пустым')

    if not password_form:
        return render_template('lab8/register.html',
                               error='Пароль не должен быть пустым')

    login_exists = users.query.filter_by(login = login_form).first()
    if login_exists:
        return render_template('lab8/register.html',
                            error = 'Такой пользователь уже существует')
    
    password_hash = generate_password_hash(password_form)
    new_user = users(login = login_form, password = password_hash)
    db.session.add(new_user)
    db.session.commit()

    # Автоматический логин после регистрации
    login_user(new_user, remember=False)

    return redirect('/lab8')

@lab8.route('/lab8/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('lab8/login.html')
    
    login_form = request.form.get('login')
    password_form = request.form.get('password')
    remember_form = request.form.get('remember')  # checkbox: 'on' если отмечено

    if not login_form:
        return render_template('lab8/login.html',
                               error='Имя пользователя не должно быть пустым')

    if not password_form:
        return render_template('lab8/login.html',
                               error='Пароль не должен быть пустым')

    user = users.query.filter_by(login = login_form).first()

    if user:
        if check_password_hash(user.password, password_form):
            remember_flag = True if remember_form == 'on' else False
            login_user(user, remember = remember_flag)
            return redirect('/lab8')
    
    return render_template('/lab8/login.html', 
                           error = 'Ошибка входа: логин и/или пароль неверны')

@lab8.route('/lab8/articles/')
def article_list():
    if current_user.is_authenticated:
        # авторизованный пользователь
        my_id = current_user.id
        # получить все статьи: свои + публичные чужие
        all_articles = articles.query.join(users, articles.login_id == users.id)\
            .filter(
                (articles.login_id == my_id) |  # свои статьи
                (articles.is_public == True)    # публичные статьи других
            )\
            .order_by(
                # свои избранные статьи сверху
                (articles.login_id == my_id).desc(),
                articles.is_favorite.desc(),
                articles.id.desc()
            ).all()
    else:
        # неавторизованный: только публичные статьи
        all_articles = articles.query.join(users, articles.login_id == users.id)\
            .filter(articles.is_public == True)\
            .order_by(articles.id.desc()).all()

    return render_template('lab8/articles.html', articles=all_articles)



@lab8.route('/lab8/create', methods=['GET', 'POST'])
@login_required
def create_article():
    if request.method == 'GET':
        return render_template('lab8/create_article.html')

    title = request.form.get('title')
    text = request.form.get('article_text')
    is_public = True if request.form.get('is_public') == 'on' else False
    is_favorite = True if request.form.get('is_favorite') == 'on' else False

    if not title:
        return render_template('lab8/create_article.html', error='Заголовок не должен быть пустым')
    if not text:
        return render_template('lab8/create_article.html', error='Текст статьи не должен быть пустым')

    new_article = articles(
        login_id = current_user.id,
        title = title,
        article_text = text,
        is_public = is_public,
        is_favorite = is_favorite,
        likes = 0
    )
    db.session.add(new_article)
    db.session.commit()
    return redirect('/lab8/articles/')

@lab8.route('/lab8/edit/<int:article_id>', methods=['GET', 'POST'])
@login_required
def edit_article(article_id):
    article = articles.query.get_or_404(article_id)

    # доступ только владельцу
    if article.login_id != current_user.id:
        abort(403)

    if request.method == 'GET':
        return render_template('lab8/edit_article.html', article=article)

    title = request.form.get('title')
    text = request.form.get('article_text')
    is_public = True if request.form.get('is_public') == 'on' else False
    is_favorite = True if request.form.get('is_favorite') == 'on' else False

    if not title:
        return render_template('lab8/edit_article.html', article=article, error='Заголовок не должен быть пустым')
    if not text:
        return render_template('lab8/edit_article.html', article=article, error='Текст статьи не должен быть пустым')

    article.title = title
    article.article_text = text
    article.is_public = is_public
    article.is_favorite = is_favorite
    db.session.commit()
    return redirect('/lab8/articles/')

@lab8.route('/lab8/delete/<int:article_id>', methods=['POST'])
@login_required
def delete_article(article_id):
    article = articles.query.get_or_404(article_id)

    # доступ только владельцу
    if article.login_id != current_user.id:
        abort(403)

    db.session.delete(article)
    db.session.commit()
    return redirect('/lab8/articles/')

@lab8.route('/lab8/logout')
@login_required
def logout():
    logout_user()
    return redirect('/lab8')

@lab8.route('/lab8/toggle_favorite/<int:article_id>', methods=['POST'])
@login_required
def toggle_favorite(article_id):
    article = articles.query.get_or_404(article_id)
    
    # Меняем статус избранного для статьи
    article.is_favorite = not bool(article.is_favorite)
    db.session.commit()
    
    return redirect('/lab8/articles/')

@lab8.route('/lab8/search', methods=['GET', 'POST'])
def search_articles():
    query = request.args.get('q', '')  # получаем строку поиска из GET-параметра

    if current_user.is_authenticated:
        my_id = current_user.id
        # Поиск по своим + публичным статьям
        results = articles.query.join(users, articles.login_id == users.id)\
            .filter(
                ((articles.login_id == my_id) | (articles.is_public == True)) &
                (articles.title.ilike(f"%{query}%") | articles.article_text.ilike(f"%{query}%"))
            )\
            .order_by(articles.is_favorite.desc(), articles.id.desc()).all()
    else:
        # Неавторизованные пользователи: только публичные статьи
        results = articles.query.join(users, articles.login_id == users.id)\
            .filter(
                (articles.is_public == True) &
                (articles.title.ilike(f"%{query}%") | articles.article_text.ilike(f"%{query}%"))
            )\
            .order_by(articles.id.desc()).all()

    return render_template('lab8/search_results.html', articles=results, query=query)


