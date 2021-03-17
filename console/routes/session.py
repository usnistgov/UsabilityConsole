from console.routes.utils import *
from console.db import Database
import logging
from flask import Flask, render_template, request, flash, redirect, session, url_for
import datetime
import calendar
import sys


########################################################################################################################
#   SESSION / ENTRY
########################################################################################################################

@app.route('/entry/posttext', methods=['POST'])
def add_freetext():
    if not is_logged_in():
        return 'User is not logged in; creator_id is not set'

    if not is_current_session_set():
        return 'Current session is not set'
    db = Database()

    value = request.data.decode()
    category_id = db.get_category_id_by_name("FREETEXT")

    db.add_entry_with_category(get_current_session_id(), get_current_user_id(), category_id, value)

    return "OK"


# application/x-www-form-urlencoded
# UTF-8
# https://stackoverflow.com/questions/6396101/pure-javascript-send-post-data-without-a-form
@app.route('/entry/post', methods=['POST'])
def add_event():
    if not is_logged_in():
        return 'User is not logged in; creator_id is not set'

    if not is_current_session_set():
        return 'Current session is not set'

    data = request.data.decode()
    category = data[data.index('=') + 1 : data.index('\n')]
    data = data[data.index('\n') + 1 : ]

    db = Database()

    if category.upper() == "ALERT":
        logging.info("ALERT posted")
        db.add_alert(get_current_session_id(), get_current_user_id(), data)
    else:
        logging.info("EVENT posted")
        db.add_entry_with_category(get_current_session_id(), get_current_user_id(), db.get_category_id_by_name(category), data)
    return 'OK'


@app.route('/entry/modify/<int:entry_id>', methods=['POST'])
def modify_entry(entry_id):
    if not is_logged_in():
        return 'User is not logged in; creator_id is not set'

    if not is_current_session_set():
        return 'Session_id is not set'

    db = Database()
    db_entry = db.get_entry(entry_id)

    if db_entry['creator_id'] == get_current_user_id() or db.is_user_id_administrator(get_current_user_id()):
        new_value = request.data.decode('utf-8')
        db.update_entry(entry_id, new_value)

        return "OK"
        # clear entry_option_id
        # clear category_id??
        # update user id?? (if admin changed it)
    else:
        return "Invalid permissions"


@app.route('/entry/delete/<int:entry_id>')
def delete_entry(entry_id):
    if not is_logged_in():
        return 'User is not logged in; creator_id is not set'

    db = Database()
    db_entry = db.get_entry(entry_id)

    if db_entry['creator_id'] == get_current_user_id() or db.is_user_id_administrator(get_current_user_id()):
        db.disable_entry(entry_id)
    else:
        return "Invalid permissions"

    return redirect_to_referrer()


########################################################################################################################
#   CONSOLE
########################################################################################################################

@app.route('/session/console')
def console():
    if not is_logged_in():      # REDIRECT TO LOGIN
        flash('You must be logged in to view this.', 'danger')
        return redirect('/')

    if not is_current_session_set():    # REDIRECT TO VIEW SESSIONS PAGE
        flash('You must have a current session set to view this.', 'danger')
        return redirect('/')

    db = Database()
    actions_ul = []
    actions_ur = []
    actions_ll = []

    for action in db.get_entry_options_by_category_id(1):
        actions_ul.append({'value': action['value'], 'color_class': action['color_class'], 'category': action['category_name']})

    for action in db.get_entry_options_by_category_id(2):
        actions_ur.append({'value': action['value'], 'color_class': action['color_class'], 'category': action['category_name']})

    for action in db.get_entry_options_by_category_id(3):
        actions_ll.append({'value': action['value'], 'color_class': action['color_class'], 'category': action['category_name']})
        actions_ul.append({'value': action['value'], 'color_class': action['color_class'], 'category': action['category_name']})
    
    session_id = session['current_session_id']
    dates=[]

    for db_entry in db.get_entries_for_session(session_id):
        dates += [getDate(db_entry['time_created'])]
    dates = list(sorted(set(dates), key=dates.index))
    data = getData(dates, db.get_internal_entries_for_session(session_id))

    return render_template('console.html', actions_ul=actions_ul, actions_ur=actions_ur, actions_ll=actions_ll, data=data)

def getData(dates, entries):
    data=[]
    for date in dates:
        data.append(
            dict(
                date=date, 
                day=getDay(date), 
                timesValues=[(getTime(entry['time_created']), entry['value']) for entry in entries if getDate(entry['time_created'])==date],
                value=[entry['value'] for entry in entries if getDate(entry['time_created'])==date],
                entry_id=[entry['entry_id'] for entry in entries if getDate(entry['time_created'])==date]
            )
        )
    return data

def getDate(date):
    index=date.index(' ')
    dateOfEntry=date[:index]
    return dateOfEntry

def getDay(date):
    formattedDate=datetime.datetime.strptime(date , '%Y-%m-%d')
    return(formattedDate.strftime('%A'))

def getTimeSpent(sessionStarted, entryTime):
    sessionStarted = datetime.datetime.strptime(sessionStarted, '%Y-%m-%d %H:%M:%S')
    entryTime = datetime.datetime.strptime(entryTime, '%Y-%m-%d %H:%M:%S')
    time_spent = entryTime - sessionStarted
    return '+' + str(time_spent.seconds // 60 % 60) + ':' + str(time_spent)[-2:]

def getTime(date):
    index=date.index(' ')+1
    time=date[index:]
    return time

########################################################################################################################
#   SESSION
########################################################################################################################

@app.route('/session/create', methods=['GET', 'POST'])
def create_session():
    if not is_logged_in():
        flash('You must be logged in to perform this operation', 'danger')
        return redirect('/')

    if request.method.upper() == 'GET':
        return render_template('create_session.html')
    elif request.method.upper() == 'POST':
        session_name = request.form['session_name']
        if session_name is None or len(session_name) == 0:
            flash('Invalid session name', 'danger')
            return redirect('/')
        else:
            db = Database()

            if db.does_session_name_exist(session_name):
                flash('Session name already exists', 'danger')
                return redirect('/')
            else:
                session_id = db.create_session(session_name, flask_session['user_id'])
                set_current_session(session_id, session_name)
                return redirect('/session/console')

@app.route('/session/viewall')
def view_sessions():
    db = Database()

    is_admin = False

    if is_logged_in() and db.is_user_id_administrator(flask_session['user_id']):
        is_admin = True

    sessions = []
    for db_session in db.get_all_sessions():
        session = {'name': db_session['name'], 'session_id': db_session['session_id'], 'time_created': db_session['time_created']}

        if is_logged_in():
            session['can_resume'] = True

            if is_admin or flask_session['user_id'] == db_session['creator_id']:
                session['has_control'] = True
            else:
                session['has_control'] = False
        last_modified = db.last_modified(db_session['session_id'])[0]
        if (last_modified != None): 
            session['last_modified'] = last_modified
        else: 
            session['last_modified'] = 'NAN'
        sessions.append(session)
    return render_template('view_sessions.html', sessions=sessions)

@app.route('/session/select/<int:session_id>')
def select_session(session_id):
    db = Database()
    name = db.get_session_name(session_id)
    set_current_session(session_id, name)
    session['session_id'] = session_id
    return redirect('/session/console')

@app.route('/session/set/<int:session_id>')
def set_session(session_id):
    db = Database()
    name = db.get_session_name(session_id)
    set_current_session(session_id, name)
    session['session_id'] = session_id
    return redirect('/session/view/'+ str(session_id))

@app.route('/session/delete/<int:session_id>')
def delete_session(session_id):
    db = Database()
    db.disable_session(session_id)
    if is_current_session_set() and (get_current_session_id() == session_id):
        clear_current_session()
    return redirect_to_referrer()

@app.route('/session/view/<int:session_id>')
def show_current_session(session_id=None):
    if session_id is None:
        return redirect('/session/viewall')

    db = Database()
    # get all current entries and load up
    session_name = db.get_session_name(session_id)
    entries = []
    for db_entry in db.get_entries_for_session(session_id):
        entry = {'entry_id': db_entry['entry_id'],
                 'value': db_entry['value'],
                 'time_created': db_entry['time_created']}

        if not is_logged_in():
            entry['can_update'] = False
        else:
            if db.is_user_id_administrator(flask_session['user_id']) or db_entry['creator_id'] == flask_session['user_id']:
                entry['can_update'] = True
        entries.append(entry)
    return render_template('view_session.html', session_name=session_name, entries=entries)