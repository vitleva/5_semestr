import os
from flask import Blueprint, render_template, request, session, current_app
import psycopg2
from psycopg2.extras import RealDictCursor
import sqlite3
from os import path, stat

lab6 = Blueprint('lab6', __name__)

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
        print("[lab6] Warning: commit failed:", e)
    try:
        cur.close()
    except Exception:
        pass
    try:
        conn.close()
    except Exception:
        pass


@lab6.route('/lab6/')
def main():
    return render_template('lab6/lab6.html')

@lab6.route('/lab6/json-rpc-api/', methods=['POST'])
def api():
    data = request.json or {}
    id = data.get('id')
    method = data.get('method')

    if method == 'info':
        conn, cur = db_connect()
        try:
            cur.execute("SELECT number, tenant, price FROM offices ORDER BY number;")
            rows = cur.fetchall()
            offices = []
            for r in rows:
                offices.append({
                    'number': r['number'],
                    'tenant': r['tenant'] or '',
                    'price': r['price']
                })

        finally:
            db_close(conn, cur)

        return {
            'jsonrpc': '2.0',
            'result': offices,
            'id': id
        }

    login = session.get('login')
    if not login:
        return {
            'jsonrpc': '2.0',
            'error': {
                'code': 1,
                'message': 'Unauthorized'
            },
            'id': id
        }

    if method == 'booking':
        office_number = data.get('params')
        try:
            office_number = int(office_number)
        except Exception:
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': -32602,
                    'message': 'Invalid params'
                },
                'id': id
            }

        conn, cur = db_connect()
        # получение текущего tenant
        if current_app.config.get('DB_TYPE') == 'postgres':
            cur.execute("SELECT tenant FROM offices WHERE number = %s;", (office_number,))
            row = cur.fetchone()
        else:
            cur.execute("SELECT tenant FROM offices WHERE number = ?;", (office_number,))
            row = cur.fetchone()

        if not row:
            db_close(conn, cur)
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': -32602,
                    'message': 'Invalid params'
                },
                'id': id
            }

        if isinstance(row, dict):  # psycopg2 RealDictRow
            current_tenant = row.get('tenant') or ''
        else:  # sqlite3.Row
            current_tenant = row['tenant'] if row['tenant'] is not None else ''

        if current_tenant != '':
            db_close(conn, cur)
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': 2,
                    'message': 'Already booked'
                },
                'id': id
            }

        # обновляем запись
        if current_app.config.get('DB_TYPE') == 'postgres':
            cur.execute("UPDATE offices SET tenant = %s WHERE number = %s;", (login, office_number))
        else:
            cur.execute("UPDATE offices SET tenant = ? WHERE number = ?;", (login, office_number))

        db_close(conn, cur)
        return {
            'jsonrpc': '2.0',
            'result': 'success',
            'id': id
        }

    if method == 'cancellation':
        office_number = data.get('params')
        try:
            office_number = int(office_number)
        except Exception:
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': -32602,
                    'message': 'Invalid params'
                },
                'id': id
            }

        conn, cur = db_connect()
        # получить tenant текущий
        if current_app.config.get('DB_TYPE') == 'postgres':
            cur.execute("SELECT tenant FROM offices WHERE number = %s;", (office_number,))
            row = cur.fetchone()
        else:
            cur.execute("SELECT tenant FROM offices WHERE number = ?;", (office_number,))
            row = cur.fetchone()

        if not row:
            db_close(conn, cur)
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': -32602,
                    'message': 'Invalid params'
                },
                'id': id
            }

        if isinstance(row, dict):
            current_tenant = row.get('tenant') or ''
        else:
            current_tenant = row['tenant'] if row['tenant'] is not None else ''

        # проверка, что офис арендован
        if current_tenant == '':
            db_close(conn, cur)
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': 3,
                    'message': 'Not rented'
                },
                'id': id
            }

        # проверка, что арендатор - текущий пользователь
        if current_tenant != login:
            db_close(conn, cur)
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': 4,
                    'message': 'Not tenant'
                },
                'id': id
            }

        # снимаем аренду (обнуляем tenant)
        if current_app.config.get('DB_TYPE') == 'postgres':
            cur.execute("UPDATE offices SET tenant = %s WHERE number = %s;", ('', office_number))
        else:
            cur.execute("UPDATE offices SET tenant = ? WHERE number = ?;", ('', office_number))

        db_close(conn, cur)
        return {
            'jsonrpc': '2.0',
            'result': 'success',
            'id': id
        }

    # метод не найден
    return {
        'jsonrpc': '2.0',
        'error': {
            'code': -32601,
            'message': 'Method not found'
        },
        'id': id
    }
