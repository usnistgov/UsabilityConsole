from console.routes.utils import *
from console import app
from console.db import Database
from flask import flash
import logging

########################################################################################################################
#   SETTINGS
########################################################################################################################


def create_session():
    if not is_logged_in():
        flash('You must be logged in to perform this operation.', 'danger')
        return redirect('/')

    if request.method.upper() == 'GET':
        return render_template('create_session.html')
    elif request.method.upper() == 'POST':
        session_name = request.form['session_name']
    if session_name is None or len(session_name) == 0:
        flash('Invalid session name.', 'danger')
        return redirect('/')

    else:
        db = Database()

        if db.does_session_name_exist(session_name):
            flash('Session name already exists.', 'danger')
            return redirect('/')

        else:
            session_id = db.create_session(session_name, flask_session['user_id'])
            set_current_session(session_id, session_name)
            return redirect('/')

@app.route('/settings', methods=['POST'])
def update_settings():
    if not is_logged_in():
        flash('You must be logged in to perform this operation.', 'danger')
        return redirect('/')

    user_id = get_current_user_id()
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']

    db = Database()
    db.update_user_first_name(user_id, first_name)
    db.update_user_last_name(user_id, last_name)
    db.update_user_email_address(user_id, email)

    answer1 = request.form['answer1']
    answer2 = request.form['answer2']
    answer3 = request.form['answer3']
    if (answer1 or answer2 or answer3): 
        question1 = request.form['question1']
        question2 = request.form['question2']
        question3 = request.form['question3']

        if len([question1, question2, question3]) != len(list(set([question1, question2, question3]))):
            flash('Questions are the same', 'danger')
            return redirect_to_referrer()
        db.delete_user_answers(user_id)
        db.create_answer(user_id,question1,answer1)
        db.create_answer(user_id,question2,answer2)
        db.create_answer(user_id,question3,answer3)

    refresh_cache()

    password = request.form['password']
    password2 = request.form['confirm_password']

    if len(password) > 0 and len(password2) > 0:
        if password == password2:
            db.update_user_password(user_id, password)
        else:
            flash('There was an issue; passwords were not updated.', 'danger')
            return redirect('/settings')

    questions = db.list_questions()
    return render_template('user_settings.html', success_message='Settings updated successfully', questions=questions)


@app.route('/settings', methods=['GET'])
def settings():
    if not is_logged_in():      # REDIRECT TO LOGIN
        flash('You must be logged in to view this.', 'danger')
        return redirect('/error')

    db = Database()
    questions = db.list_questions()

    return render_template('user_settings.html', questions=questions)