import os
from flask import Blueprint, render_template, request, abort, current_app
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import sqlite3
from os import path

lab8 = Blueprint('lab8', __name__)

@lab8.route('/lab8')
def lab():
    return render_template('lab8/lab8.html')
