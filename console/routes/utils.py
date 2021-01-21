from console import app
from flask import render_template, request, redirect, g, session as flask_session
import datetime
import logging
from console.db import Database
from config import DEBUG, CLEAR_SESSION_ON_START

# http://flask.pocoo.org/docs/1.0/api/


@app.after_request      # http://flask.pocoo.org/snippets/53/
def after_request(response):
    flask_session['last_active'] = datetime.datetime.now()
    return response


@app.before_first_request
def before_first():
    if DEBUG and CLEAR_SESSION_ON_START:
        logging.debug("Clearing flask session data...")
        flask_session.clear()


@app.before_request
def before_request():
    g.flask_session = flask_session     # add session to all requests, so they are always available within templates

    # TODO Get rid of need for g.current_session_id and g.current_session_name and use g.flask_session.get_current_??
    g.current_session_id = get_current_session_id()         # needed to support old code when FileSystemCache was used
    g.current_session_name = get_current_session_name()     # needed to support old code when FileSystemCache was used

    if 'session_started' not in flask_session:
        flask_session['session_started'] = datetime.datetime.now()

########################################################################################################################
#   HELPER FUNCTIONS
########################################################################################################################


def refresh_cache():
    if is_logged_in():
        user_id = get_current_user_id()
        db = Database()
        user = db.get_user_by_id(user_id)

        for key in user.keys():
            flask_session[key] = user[key]
    pass


def is_logged_in():
    return 'user_id' in flask_session


def get_current_user_id():
    if is_logged_in():
        return flask_session['user_id']
    else:
        return None


def is_current_session_set():
    return 'current_session_id' in flask_session and flask_session['current_session_id'] is not None


def get_current_session_id():
    return flask_session['current_session_id'] if is_current_session_set() else None


def get_current_session_name():
    return flask_session['current_session_name'] if is_current_session_set() else None


def set_current_session(session_id, name):
    flask_session['current_session_id'] = session_id
    flask_session['current_session_name'] = name


def clear_current_session():
    del flask_session['current_session_id']
    del flask_session['current_session_name']


def redirect_to_referrer():
    if request.referrer is None:
        return redirect('/')
    else:
        return redirect(request.referrer)