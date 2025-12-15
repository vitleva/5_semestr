from flask import Blueprint, render_template, request, session, current_app
import random
import sqlite3
from os import path
import psycopg2
from psycopg2.extras import RealDictCursor

lab9 = Blueprint('lab9', __name__)

MAX_OPENED = 3
TOTAL_BOXES = 10

GREETINGS = [
    "🎄 С Новым годом! Дай Бог без депрессии в новом году!",
    "❄️ Пусть в новом году у Деда Мороза не придется просить... пощады",
    "🎁 С Новым Годом, пусть он заберет еще больше нервных клеток!",
    "☃️ Ура! Еще 365 поводов для нервного срыва!",
    "✨ Желаю в Новом году еще больше эмоциональных качель!",
    "🎅 С Новым Годом! Желаю дожить до следующей сессии!",
    "🎆 В Новом Году желаю килограмм новопассита бесплатно!",
    "🌟 В Новом Году желаю дождаться Макана из армии!",
    "🍾 Пусть Новый год переплюнет старый: депрессия заиграет новыми красками!",
    "💫 В Новогоднюю ночь желаю не уехать в дурдом (хотя может это не так плохо)"
]

GIFT_IMAGES = [
    "/static/lab9/gifts/gift1.jpg",
    "/static/lab9/gifts/gift2.jpg",
    "/static/lab9/gifts/gift3.jpg",
    "/static/lab9/gifts/gift4.jpg",
    "/static/lab9/gifts/gift5.jpg",
    "/static/lab9/gifts/gift6.jpg",
    "/static/lab9/gifts/gift7.jpg",
    "/static/lab9/gifts/gift8.jpg",
    "/static/lab9/gifts/gift9.jpg",
    "/static/lab9/gifts/gift10.jpg",
]

BOX_IMAGES = [
    "/static/lab9/boxes/box1.png",
    "/static/lab9/boxes/box2.png",
    "/static/lab9/boxes/box3.png",
    "/static/lab9/boxes/box4.png",
    "/static/lab9/boxes/box5.png",
    "/static/lab9/boxes/box6.png",
    "/static/lab9/boxes/box7.png",
    "/static/lab9/boxes/box8.png",
    "/static/lab9/boxes/box9.png",
    "/static/lab9/boxes/box10.png",
]

BOX_POSITIONS = [
    (20, 2),
    (40, 3),
    (66, 1),
    (15, 35),
    (35, 37),
    (55, 36),
    (71, 29),
    (25, 65),
    (45, 65),
    (65, 62)
]



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
        print("[lab9] Warning: commit failed:", e)
    try:
        cur.close()
    except Exception:
        pass
    try:
        conn.close()
    except Exception:
        pass


def init_boxes():
    conn, cur = db_connect()
    try:
        cur.execute("SELECT COUNT(*) as cnt FROM gift_boxes;")
        if cur.fetchone()['cnt'] == 0:

            greetings = GREETINGS.copy()
            gifts = GIFT_IMAGES.copy()
            boxes = BOX_IMAGES.copy()

            for i in range(TOTAL_BOXES):
                x, y = BOX_POSITIONS[i]
                if current_app.config.get('DB_TYPE') == 'postgres':
                    cur.execute("""
                        INSERT INTO gift_boxes (x, y, greeting, gift_image, box_image)
                        VALUES (%s, %s, %s, %s, %s);
                    """, (
                        x,
                        y,
                        greetings[i],
                        gifts[i],
                        boxes[i]
                    ))
                else:
                    cur.execute("""
                        INSERT INTO gift_boxes (x, y, greeting, gift_image, box_image)
                        VALUES (?, ?, ?, ?, ?);
                    """, (
                        x,
                        y,
                        greetings[i],
                        gifts[i],
                        boxes[i]
                    ))

    finally:
        db_close(conn, cur)


@lab9.route('/lab9')
def main():
    init_boxes()

    if 'opened_count' not in session:
        session['opened_count'] = 0

    conn, cur = db_connect()
    try:
        cur.execute("SELECT * FROM gift_boxes;")
        boxes = [dict(row) for row in cur.fetchall()]
    finally:
        db_close(conn, cur)

    unopened = sum(1 for b in boxes if b['opened'] == 0)

    return render_template(
        'lab9/index.html',
        boxes=boxes,
        unopened=unopened,
        opened_count=session['opened_count']
    )


@lab9.route('/lab9/api/open', methods=['POST'])
def open_box():
    data = request.get_json()
    box_id = data.get('id')

    if session.get('opened_count', 0) >= MAX_OPENED:
        return {'error': 'Можно открыть не более 3 коробок'}, 403

    conn, cur = db_connect()
    try:
        if current_app.config.get('DB_TYPE') == 'postgres':
            cur.execute("SELECT * FROM gift_boxes WHERE id = %s;", (box_id,))
        else:
            cur.execute("SELECT * FROM gift_boxes WHERE id = ?;", (box_id,))

        box = cur.fetchone()

        if not box or box['opened']:
            return {'error': 'Коробка уже пуста'}, 400

        if current_app.config.get('DB_TYPE') == 'postgres':
            cur.execute("UPDATE gift_boxes SET opened = 1 WHERE id = %s;", (box_id,))
        else:
            cur.execute("UPDATE gift_boxes SET opened = 1 WHERE id = ?;", (box_id,))

    finally:
        db_close(conn, cur)

    session['opened_count'] += 1

    return {
        'greeting': box['greeting'],
        'gift_image': box['gift_image'],
        'opened_count': session['opened_count']
    }
