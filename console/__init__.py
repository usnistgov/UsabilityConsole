from flask import Flask,render_template
from flask_session import Session
from flask_fontawesome import FontAwesome


app = Flask(__name__)
fa = FontAwesome(app)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

global global_var
global_var = dict()

app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = b'\xcfJ\xa1\x8fQ\x86\xd4\xfc\xd6\xf0\x93\xf0\xe3M>\x9eB\xbds@P\xfb\xe2\xb8' 	# os.urandom(24)

Session(app)

import console.routes.accounts
import console.routes.base
import console.routes.external
import console.routes.session
import console.routes.settings