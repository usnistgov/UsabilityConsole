import sqlite3
import os
import sys


class Database:
    __ROOT = os.path.dirname(os.path.realpath(__file__))
    DEBUG = True

    def __init__(self, database_name='database.db'):
        self.database_name = database_name
        self.database = None
        self.__establish_connection()
        pass

    def __del__(self):
        self.database.close()

    def __establish_connection(self):
        if self.database is None:
            self.database = sqlite3.connect(os.path.join(Database.__ROOT, self.database_name), detect_types=sqlite3.PARSE_DECLTYPES)
            self.database.row_factory = sqlite3.Row

        self.__initialize()

    def __reset(self):
        conn = self.database
        sql = open(os.path.join(Database.__ROOT, 'schema.sql'), 'r').read()
        conn.executescript(sql)

        if Database.DEBUG:
            sql = open(os.path.join(Database.__ROOT, 'schema-testdata.sql'), 'r').read()
            conn.executescript(sql)

    def __initialize(self):
        if self.fetchone("SELECT COUNT(name) FROM sqlite_master WHERE type='table';")[0] == 0:
            self.__reset()

    def get_cursor(self):
        return self.database.cursor()

    def close(self):
        if self.database is not None:
            self.database.close()

    def fetchone(self, sql, *params):
        c = self.get_cursor()
        c.execute(sql, params)
        return c.fetchone()

    def fetchall(self, sql, *params):
        c = self.get_cursor()
        c.execute(sql, params)
        return c.fetchall()

    def update(self, sql, *params):
        conn = self.database
        conn.execute(sql, params)

        result = self.fetchone("SELECT last_insert_rowid()")[0]
        conn.commit()

        return result

########################################################################################################################
#  SETTINGS
########################################################################################################################

    # def get_all_settings(self):
    #     return self.fetchall("SELECT key, value FROM settings")
    #
    # def add_setting(self, key, value):
    #     return self.update("INSERT INTO settings (key, value) VALUES (?, ?)", key, value)
    #
    # def get_setting(self, key):
    #     return self.fetchone("SELECT * FROM settings WHERE key=?", key)
    #
    # def update_setting(self, key, value):
    #     return self.update("UPDATE SETTINGS SET value=? WHERE key=?", value, key)
    #
    # def delete_setting(self, key):
    #     return self.update("DELETE FROM settings WHERE key=?", key)
    #
    # def does_setting_exist(self, key):
    #     return self.fetchone("SELECT COUNT(*) FROM settings WHERE key=?", key)[0] > 0

########################################################################################################################
#  ROLES
########################################################################################################################

    def list_roles(self):
        return self.fetchall("SELECT * FROM roles")

    def get_administrator_role_id(self):
        return self.fetchone("SELECT role_id FROM roles WHERE name LIKE 'Administrator'")['role_id']

    def get_user_role_id(self):
        return self.fetchone("SELECT role_id FROM roles WHERE name LIKE 'User'")['role_id']

########################################################################################################################
#  USER
########################################################################################################################

    def does_username_exist(self, username):
        return self.fetchone("SELECT COUNT(*) FROM users WHERE username=? AND enabled=1", username)[0] > 0

    def get_user(self, username, password):
        user_id = self.authenticate_user(username, password)
        if user_id is not None:
            return self.fetchone("SELECT * FROM users_no_password WHERE user_id=?", user_id)
        else:
            return None

    def get_user_questions_guess(self, user_id):
        return self.fetchone("SELECT questions_guess FROM users WHERE user_id=?", user_id)['questions_guess']

    def authenticate_user(self, username, password):
        rs = self.fetchone("SELECT user_id FROM users WHERE username=? AND password=? AND enabled=1", username, password)

        if rs is not None:
            return rs['user_id']
        else:
            return None

    def generate_api_key(self, username):
        import uuid
        return username + str(uuid.uuid4()).replace('-', '')

    def create_user(self, role_id, username, password, first_name=None, last_name=None, email_address=None):
        return self.update("""INSERT INTO users (role_id, username, password, first_name, last_name, email_address, api_key) 
                        VALUES (?, ?, ?, ?, ?, ?, ?)""", role_id, username, password, first_name, last_name, email_address, self.generate_api_key(username))

    def delete_user(self, user_id):
        # return self.update("DELETE FROM users WHERE user_id=?", user_id)
        return self.disable_user(user_id)

    def get_user_by_id(self, user_id):
        return self.fetchone("SELECT * FROM users_no_password WHERE user_id=?", user_id)

    def get_user_by_api_key(self, api_key):
        user_id = self.fetchone("SELECT * FROM users WHERE api_key=?", api_key)

        if user_id is None:
            return None

        user_id = user_id["user_id"]
        return self.get_user_by_id(user_id)

    def get_user_by_username(self, username):
        return self.fetchone("SELECT * FROM users_no_password WHERE username=? AND enabled=1", username)

    def update_user(self, user_id, password, first_name=None, last_name=None, email_address=None):
        return self.update("""UPDATE users 
                            SET password=?,
                            first_name=?,
                            last_name=?,
                            email_address=?
                            WHERE user_id=?""", password, first_name, last_name, email_address, user_id)

    def update_user_password(self, user_id, password):
        return self.update("UPDATE users SET password=? WHERE user_id=?", password, user_id)

    def update_user_first_name(self, user_id, first_name):
        return self.update("UPDATE users SET first_name=? WHERE user_id=?", first_name, user_id)

    def update_user_last_name(self, user_id, last_name):
        return self.update("UPDATE users SET last_name=? WHERE user_id=?", last_name, user_id)

    def update_user_email_address(self, user_id, email_address):
        return self.update("UPDATE users SET email_address=? WHERE user_id=?", email_address, user_id)

    def update_users_role(self, user_id, role_id):
        return self.update("""UPDATE users 
                                    SET role_id=?
                                    WHERE user_id=?""", role_id, user_id)

    def update_user_question_guess(self, user_id, questions_guess):
        return self.update("UPDATE users SET questions_guess=? WHERE user_id=?", questions_guess, user_id)

    def get_user_count(self, role_id=None):
        if role_id is None:
            return self.fetchone("SELECT COUNT(*) FROM users WHERE enabled=1")[0]
        else:
            return self.fetchone("SELECT COUNT(*) FROM users WHERE role_id=? AND enabled=1", role_id)[0]

    def is_user_id_administrator(self, user_id):
        return self.fetchone("SELECT role_id FROM users WHERE user_id=?", user_id)['role_id'] == self.get_administrator_role_id()

    def get_user_id(self, username):
        return self.fetchone("SELECT user_id FROM users WHERE username=? AND enabled=1", username)['user_id']

    def get_all_users(self):
        return self.fetchall("SELECT * FROM users_no_password WHERE enabled=1")

    def disable_user(self, user_id):
        return self.update("UPDATE users SET enabled=0 WHERE user_id=?", user_id)

    def enable_user(self, user_id):
        return self.update("UPDATE users SET enabled=1 WHERE user_id=?", user_id)


########################################################################################################################
#  SESSION
########################################################################################################################

    def get_all_sessions(self):
        return self.fetchall("SELECT * FROM sessions WHERE enabled=1 ORDER BY session_id DESC, time_created DESC")

    def create_session(self, session_name, creator_id):
        return self.update("INSERT INTO sessions (name, creator_id) VALUES (?, ?)", session_name, creator_id)

    def delete_session(self, session_id):
        # return self.update("DELETE FROM sessions WHERE session_id=?", session_id)
        return self.disable_session(session_id)

    def update_session(self, session_id, new_name):
        return self.update("UPDATE sessions SET name=? WHERE session_id=?", new_name, session_id)

    def get_session_name(self, session_id):
        return self.fetchone("SELECT name FROM sessions WHERE session_id=?", session_id)['name']

    def does_session_name_exist(self, session_name):
        return self.fetchone("SELECT COUNT(*) FROM sessions WHERE name=? AND enabled=1", session_name)[0] > 0

    def disable_session(self, session_id):
        return self.update("UPDATE sessions SET enabled=0 WHERE session_id=?", session_id)

    def enable_session(self, session_id):
        return self.update("UPDATE sessions SET enabled=1 WHERE session_id=?", session_id)

    def get_session_time_created(self, session_id):
        return self.fetchone("SELECT time_created FROM sessions WHERE session_id=?", session_id)['time_created']


########################################################################################################################
#  ALERTS
########################################################################################################################

    def add_alert(self, session_id, creator_id, value):
        # self.add_entry(session_id, creator_id, self.get_category_id_by_name('ALERT'), value)
        return self.update("INSERT INTO alerts (session_id, creator_id, value) VALUES (?, ?, ?)",
                           session_id, creator_id, value)

    def get_all_alerts(self):
        return self.fetchall("SELECT * FROM alerts")

    def disable_alert(self, alert_id):
        return self.update("UPDATE entries SET enabled=0 WHERE alert_id=?", alert_id)

    def get_all_alerts_for_session_id(self, session_id):
        return self.fetchall("SELECT * FROM alerts WHERE session_id=? AND enabled=1", session_id)

    def get_all_alerts_and_disable_for_session_id(self, session_id):
        alerts = self.get_all_alerts_for_session_id(session_id)
        self.update("UPDATE alerts SET enabled=0 WHERE session_id=? AND enabled=1", session_id)

        return alerts

########################################################################################################################
#  ENTRY
########################################################################################################################

    def delete_entry(self, entry_id):
        # return self.update("DELETE FROM entries WHERE entry_id=?", entry_id)
        return self.disable_entry(entry_id)

    def add_entry(self, session_id, creator_id, value):
        return self.update("INSERT INTO entries (session_id, creator_id, value) VALUES (?, ?, ?)",
                           session_id, creator_id, value)

    def add_entry_with_category(self, session_id, creator_id, category_id, value):
        return self.update("INSERT INTO entries (session_id, creator_id, category_id, value) VALUES (?, ?, ?, ?)",
                           session_id, creator_id, category_id, value)

    def get_entries_for_session(self, session_id):
        return self.fetchall("SELECT * FROM entries WHERE session_id=? AND enabled=1 ORDER BY entry_id DESC, time_created DESC", session_id)

    def get_internal_entries_for_session(self, session_id):
        return self.fetchall("SELECT * FROM entries WHERE session_id=? AND enabled=1 AND category_id!=5 ORDER BY entry_id DESC, time_created DESC", session_id)

    def get_entry(self, entry_id):
        return self.fetchone("SELECT * FROM entries WHERE entry_id=?", entry_id)

    def update_entry(self, entry_id, new_value):
        return self.update("UPDATE entries SET value=?, entry_option_id=null WHERE entry_id=?", new_value, entry_id)

    def disable_entry(self, entry_id):
        return self.update("UPDATE entries SET enabled=0 WHERE entry_id=?", entry_id)

    def enable_entry(self, entry_id):
        return self.update("UPDATE entries SET enabled=1 WHERE entry_id=?", entry_id)

    def last_modified(self, session_id):
        return self.fetchone("SELECT MAX(time_created) FROM entries WHERE session_id=? AND enabled=1", session_id)

########################################################################################################################
#  ENTRY_OPTIONS
########################################################################################################################

    def get_primary_entry_options(self):
        return self.get_entry_options()

    def get_entry_options_by_category_name(self, category_name):
        #return self.fetchall("SELECT * FROM entry_options WHERE category_name=? AND enabled=1 ORDER BY ordinal ASC", category_name)
        return self.fetchall("SELECT * FROM entry_options INNER JOIN categories ON entry_options.category_id=categories.category_id WHERE entry_options.category_name=? AND entry_options.enabled=1  ORDER BY ordinal ASC", category_name)

    def get_entry_options_by_category_id(self, category_id):
        return self.fetchall("SELECT * FROM entry_options INNER JOIN categories ON entry_options.category_id=categories.category_id WHERE entry_options.category_id=? AND entry_options.enabled=1  ORDER BY ordinal ASC", category_id)

    def get_entry_options_by_quadrant(self, quadrant_number):
        #return self.fetchall("SELECT * FROM entry_options INNER JOIN categories ON entry_options.category_id=categories.category_id WHERE entry_options.category_id=? AND entry_options.enabled=1  ORDER BY ordinal ASC", category_id)
        # TODO get_entry_options_by_quadrant(quadrant_number)...
        pass

    def get_entry_options(self, parent_id=None):
        if parent_id is None:
            return self.fetchall("SELECT * FROM entry_options WHERE parent_id is null AND enabled=1")
        else:
            return self.fetchall("SELECT * FROM entry_options WHERE parent_id=? AND enabled=1", parent_id)

    def create_entry_option(self, category_id, value, ordinal, parent_id=None):
        return self.update("INSERT INTO entry_options (category_id, value, ordinal, parent_id) VALUES (?, ?, ?, ?)",
                                (category_id, value, ordinal, parent_id))

    def get_entry_option(self, entry_option_id):
        return self.fetchone("SELECT * FROM entry_options WHERE entry_option_id=?", entry_option_id)

    def delete_entry_option(self, entry_option_id):
        # return self.update("DELETE FROM entry_options WHERE entry_option_id=?", entry_option_id)
        return self.disable_entry_option(entry_option_id)

    def update_entry_option(self, entry_option_id, value, ordinal=None, category_id=None, parent_id=None, null_parent_id=False):
        params = [value]
        sql = "UPDATE entry_options SET value=?"

        if ordinal is not None:
            sql += ", ordinal=?"
            params.append(ordinal)

        if category_id is not None:
            sql += ", category_id=?"
            params.append(category_id)

        if parent_id is not None:       # explicitly listing a parent_id takes precedence over a null_parent_id=True
            sql += ", parent_id=?"
            params.append(parent_id)
        elif null_parent_id is True:
            sql += ", parent_id=null"

        sql += " WHERE entry_option_id=?"
        params.append(entry_option_id)

        return self.update(sql, params)

    def disable_entry_option(self, entry_option_id):
        return self.update("UPDATE entry_options SET enabled=0 WHERE entry_option_id=?", entry_option_id)

    def enable_entry_option(self, entry_option_id):
        return self.update("UPDATE entry_options SET enabled=1 WHERE entry_option_id=?", entry_option_id)

########################################################################################################################
#  CATEGORY
########################################################################################################################

    def get_category_id_by_name(self, category_name):
        return self.fetchone("SELECT category_id FROM categories WHERE enabled=1 AND category_name=?", category_name)['category_id']

    def get_categories(self):
        return self.fetchall("SELECT * FROM categories WHERE enabled=1")

    def delete_category(self, category_id):
        # return self.update("DELETE FROM categories WHERE category_id=?", category_id)
        return self.disable_category(category_id)

    def create_category(self, name):
        sql = "INSERT INTO categories (category_name"
        values = "(?"
        params = [name]

        sql += ") VALUES " + values + ")"

        return self.update(sql, params)

    def get_category(self, category_id):
        return self.fetchone("SELECT * FROM categories WHERE category_id=?", category_id)

    def update_category(self, category_id, name):
        return self.update("UPDATE categories SET name=? category_id=?", name, category_id)

    def disable_category(self, category_id):
        return self.update("UPDATE categories SET enabled=0 WHERE category_id=?", category_id)

    def enable_category(self, category_id):
        return self.update("UPDATE categories SET enabled=1 WHERE category_id=?", category_id)


########################################################################################################################
#  QUESTIONS
########################################################################################################################

    def list_questions(self):
        return self.fetchall("SELECT * FROM security_questions")

    def get_question(self,question_id):
        return self.fetchone("SELECT question FROM security_questions WHERE question_id=?", question_id)

    def get_questions(self,questions_id):
        return self.fetchall("SELECT question FROM security_questions WHERE question_id IN " + str(tuple(questions_id)) + "")

########################################################################################################################
#  ANSWERS
########################################################################################################################


    def get_user_answer(self, question_id, user_id):
        return self.fetchone("SELECT answer FROM security_answers WHERE question_id=? AND user_id=? ", question_id, user_id)['answer']

    def get_user_questionsId(self, user_id):
        return self.fetchall("SELECT question_id FROM security_answers where user_id=?", user_id)

    def create_answer(self, user_id, question_id, answer):
        return self.update("INSERT INTO security_answers (user_id, question_id, answer) VALUES (?, ?, ?)", user_id, question_id, answer)

    def delete_user_answers(self, user_id):
        return self.update("DELETE FROM security_answers WHERE user_id =? ", user_id)

if __name__ == "__main__":
    db = Database()

    # self.fetchall("SELECT * FROM entry_options WHERE category_id=? AND enabled=1 ORDER BY ordinal ASC", category_id)

    for action in db.fetchall("SELECT * FROM entry_options INNER JOIN categories ON entry_options.category_id=categories.category_id WHERE entry_options.category_id=? AND entry_options.enabled=1  ORDER BY ordinal ASC", 4):
        print(action['value'], action['category_name'])
    db.close()

