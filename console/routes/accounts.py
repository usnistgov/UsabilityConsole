from console.routes.utils import *
from console.db import Database
from flask import Flask, url_for, session, flash, request
import requests
import sqlite3
import sys

########################################################################################################################
#   ACCOUNTS AND AUTHENTICATION
########################################################################################################################


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method.upper() == 'GET':
        db=Database()
        questions = db.list_questions()
        return render_template('register.html', questions = questions)
    elif request.method.upper() == 'POST':
        username = request.form['username']
        password = request.form['password']
        password2 = request.form['confirm_password']
        question1 = request.form['question1']
        question2 = request.form['question2']
        question3 = request.form['question3']
        answer1 = request.form['answer1']
        answer2 = request.form['answer2']
        answer3 = request.form['answer3']

        if password != password2:
            flash('Passwords are not the same', 'danger')
            return redirect_to_referrer()

        db = Database()

        if db.does_username_exist(username):
            flash('Username already exists', 'danger')
            return redirect_to_referrer()
        if len([question1, question2, question3]) != len(list(set([question1, question2, question3]))):
            flash('Questions are the same', 'danger')
            return redirect_to_referrer()
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email_address = request.form['email_address']

        if len(first_name) == 0:
            first_name = None

        if len(last_name) == 0:
            last_name = None

        if len(email_address) == 0:
            email_address = None
        
        userId = db.create_user(db.get_user_role_id(), username, password, first_name, last_name, email_address)
        user = db.get_user(username, password)
        db.create_answer(userId,question1,answer1)
        db.create_answer(userId,question2,answer2)
        db.create_answer(userId,question3,answer3)

        for key in user.keys():
            flask_session[key] = user[key]

        questions = db.list_questions()

    return render_template('user_settings.html', questions=questions, success_message='Account created successfully')

@app.route('/logout')
def logout():
    flask_session.clear()
    flash('Successfully logged out', 'success')
    return redirect('/')

@app.route('/session/login', methods=['GET', 'POST'])
def login():
    if request.method.upper() == 'GET':
        return render_template('/session/viewall.html')
    elif request.method.upper() == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = Database()
        user = db.get_user(username, password)

        if user is None:
            flash('Invalid Credentials.', 'danger')
            return redirect('/error')
        else:
            for key in user.keys():
                flask_session[key] = user[key]
            flash('Successfully logged in', "success")
            db.update_user_question_guess(user['user_id'],3)
            return redirect('/session/viewall')
    else:
        redirect_to_referrer()


@app.route('/user/viewall')
def view_all_users():
    db = Database()

    if is_logged_in() and db.is_user_id_administrator(flask_session['user_id']):
        users = []

        for db_user in db.get_all_users():
            is_admin = db.is_user_id_administrator(db_user['user_id'])

            user = { 'user_id': db_user['user_id'],
                     'username': db_user['username'],
                     'first_name': db_user['first_name'],
                     'last_name': db_user['last_name'],
                     'admin': 1 if is_admin else 0}

            users.append(user)
        return render_template('view_users.html', users = users)
    else:
        flash('You must be logged in as an administrator to view this page.', 'danger')
        return redirect('/')

@app.route('/user/admin/<int:user_id>')
def toggle_admin_for_user(user_id):
    db = Database()

    if is_logged_in() and db.is_user_id_administrator(flask_session['user_id']):
        user = db.get_user_by_id(user_id)
        role_id = user['role_id']
        if role_id == db.get_administrator_role_id():
            role_id = db.get_user_role_id()
        else:
            role_id = db.get_administrator_role_id()

        db.update_users_role(user_id, role_id)
        return redirect_to_referrer()
    else:
        flash('You must be logged in as an administrator to perform this operation.', 'danger')
        return redirect_to_referrer()


@app.route('/user/delete/<int:user_id>')
def delete_user(user_id):
    db = Database()

    if is_logged_in() and db.is_user_id_administrator(flask_session['user_id']):
        db.delete_user(user_id)

    return redirect_to_referrer()

## Page where questions are asked to retrieve password. 
@app.route('/questions', methods=['GET', 'POST'])
def questions():
    hideStatusForm='hidden'
    if request.method.upper() == 'GET':
        return render_template('questions.html', hideStatusForm=hideStatusForm)
    elif request.method.upper() == 'POST':
        req = request.form
        username = req.get('username')
        return redirect('/questions/' + username)

@app.route('/questions/<string:username>', methods=['GET', 'POST'])
def user_questions(username):
    db = Database()
    try:
        userId = db.get_user_id(username)
        questionsID = db.get_user_questionsId(userId)
        for i in range(len(questionsID)):
            questionsID[i]=questionsID[i]['question_id']
        questions = db.get_questions(questionsID)
        for j in range(len(questions)):
            questions[j]=questions[j]['question']
        questions_guess=db.get_user_questions_guess(userId)
        question = questions[questions_guess-1]
        if request.method.upper() == 'GET':
            if questions_guess > 0:
                return render_template('questions.html', question=question, username = username, questions_guess=questions_guess)
            else:
                flash('No additional password recovery mechanism attempts remaining.', 'danger')
                flash('Please contact your system administrator to reset your password.', 'danger')
                return redirect('/')

        elif request.method.upper() == 'POST':
            req = request.form
            userAnswer = req.get('answer')
            realAnswer = db.get_user_answer(questionsID[questions_guess-1], userId)
            if (userAnswer == realAnswer):
                session['userId'] = userId
                return redirect('/reset_password')
            else:
                if(questions_guess<1):
                    flash('Failed security questions too many times', 'danger')
                    flash('Contact administrator at: admin@nist.gov', 'danger')
                    return redirect('/')
                else:
                    flash('The answer you gave is incorrect', 'danger')
                    db.update_user_question_guess( userId,questions_guess-1)
                    return redirect('/questions/' + username)
            return render_template('questions.html', question=question, username = username, questions_guess=questions_guess+1)
    except Exception as e:
        flash('Username not found', "danger")
        print(e, file = sys.stderr)
        return redirect('/questions')

@app.route('/reset_password', methods=['GET','POST'])
def reset_password():
    if request.method.upper() == 'GET':
        return render_template('reset_password.html')
    else:
        db=Database()
        userId = session['userId']   
        password = request.form['password']
        password2 = request.form['confirm_password']
        if len(password) > 0 and len(password2) > 0:
            if password == password2:
                db.update_user_question_guess(userId, 3)
                db.update_user_password(userId, password)
                flash('Password was successfully updated', 'success')
                return redirect('/')
            else: 
                flash('There was an issue; passwords were not updated', 'danger')
                return redirect(request.url)
            return render_template('questions.html')