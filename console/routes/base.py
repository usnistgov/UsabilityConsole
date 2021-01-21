from console.routes.utils import *
from console import app
from config import DEBUG
from console.db import Database
from flask import render_template
import logging

########################################################################################################################
#   ROUTES
########################################################################################################################


@app.route('/debug')
def debug():
    return render_template('__debug.html')

@app.route('/debug/clear')
def clear_session():
    clear_current_session()
    return render_template('index.html')

@app.route('/index')
def index():
    return render_template('index.html', debug=DEBUG)

@app.route('/error')
def error():
    return render_template('back.html', debug=DEBUG)

@app.route('/')
def home():
    return redirect('/session/viewall')