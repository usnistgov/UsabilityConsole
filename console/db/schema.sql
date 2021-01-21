/***********************************************************************************************************************
    CLEANUP DATA
***********************************************************************************************************************/

DROP TABLE IF EXISTS settings;
DROP TABLE IF EXISTS roles;
DROP TABLE IF EXISTS users;
DROP VIEW IF EXISTS users_no_password;
DROP TABLE IF EXISTS sessions;
DROP TABLE IF EXISTS alerts;
DROP TABLE IF EXISTS entries;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS entry_options;

/***********************************************************************************************************************
    CREATE TABLES / REFERENCES
***********************************************************************************************************************/

CREATE TABLE IF NOT EXISTS settings (
    setting_id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,
    value TEXT
);

CREATE TABLE IF NOT EXISTS roles (
    role_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    role_id INTEGER NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    first_name TEXT,
    last_name TEXT,
    email_address TEXT,
    questions_guess INTEGER DEFAULT 3,
    api_key TEXT,
    enabled BOOLEAN DEFAULT 1,
    FOREIGN KEY (role_id) REFERENCES roles(role_id)
);

CREATE VIEW IF NOT EXISTS users_no_password
AS
    SELECT user_id, role_id, username, first_name, last_name, email_address, enabled, api_key FROM users;

CREATE TABLE IF NOT EXISTS sessions (
    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
    creator_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    time_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    enabled BOOLEAN DEFAULT 1,
    FOREIGN KEY (creator_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS alerts (
    alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    creator_id INTEGER NOT NULL,
    time_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    value TEXT NOT NULL,
    enabled BOOLEAN DEFAULT 1,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id),
    FOREIGN KEY (creator_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS entries (
    entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    creator_id INTEGER NOT NULL,
    time_created DATETIME DEFAULT CURRENT_TIMESTAMP,
    value TEXT NOT NULL,
    entry_option_id INTEGER,
    category_id INTEGER,
    enabled BOOLEAN DEFAULT 1,
    FOREIGN KEY (session_id) REFERENCES sessions(session_id),
    FOREIGN KEY (creator_id) REFERENCES users(user_id),
    FOREIGN KEY (entry_option_id) REFERENCES entry_options(entry_option_id),
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

CREATE TABLE IF NOT EXISTS categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT NOT NULL,
    quadrant INTEGER,
    enabled BOOLEAN DEFAULT 1
);

CREATE TABLE IF NOT EXISTS security_questions (
    question_id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS security_answers (
    answer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    answer TEXT NOT NULL,
    question_id INTEGER,
    user_id INTEGER,
    FOREIGN KEY (question_id) REFERENCES security_questions(question_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS entry_options (
    entry_option_id INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_id INTEGER,
    category_id INTEGER,
    value TEXT NOT NULL,
    ordinal INTEGER,
    color_class TEXT,
    enabled BOOLEAN DEFAULT 1,
    FOREIGN KEY (parent_id) REFERENCES entry_options(entry_option_id),
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

/***********************************************************************************************************************
    DEFAULT DATA
***********************************************************************************************************************/

INSERT INTO users (role_id, username, password, first_name) VALUES
                (1, 'admin', 'admin', 'Administrator');               -- user_id: 1

INSERT INTO roles (name) VALUES
                ('Administrator'),      -- role_id: 1
                ('User');               -- role_id: 2

INSERT INTO categories (category_name, quadrant) VALUES
                ('CAT1', 1),        -- category_id: 1     --
                ('CAT2', 2),        -- category_id: 2     --
                ('ALERT', 3),      -- category_id: 3     -- used to alert to the environment that something needs to change
                ('FREETEXT', 3),    -- category_id: 4     -- free text
                ('EXTERNAL', 4);    -- category_id: 5     -- entries from third-party / external clients

INSERT INTO entry_options (category_id, value, color_class, ordinal) VALUES
                (1, 'System Lagged',              'blue',   3),    -- entry_option_id: 1
                (1, 'Session Started',            'yellow',  1),    -- entry_option_id: 2
                (1, 'Session Ended',              'yellow',  2),    -- entry_option_id: 3
                (2, 'User Made Verbal Comment',   'red',    1),    -- entry_option_id: 4
                (2, 'User Restarted Task',        'red',    2),    -- entry_option_id: 5
                (2, 'User Hesitated',             'red',    3),    -- entry_option_id: 6
                (2, 'Emotion Displayed',          'green',  4);    -- entry_option_id: 7
                -- (2, 'User Made Verbal Comment',   'red',    1),    -- entry_option_id: 2
                -- (2, 'User Restarted Task',        'red',    2),    -- entry_option_id: 3
                -- (2, 'User Hesitated',             'red',    3),    -- entry_option_id: 4
                -- (2, 'Emotion Displayed',          'green',  4),    -- entry_option_id: 5
                -- (3, 'Restart Office Fire',        'red',    1);

--INSERT INTO entry_options (category_id, value, color_class, ordinal, parent_id) VALUES
--                (3, 'Frustration',                'orange', 1, 7),  -- entry_option_id: 8
--                (3, 'Happiness',                  'orange', 2, 7);    -- entry_option_id: 9

INSERT INTO security_questions (question_id, question) VALUES
            (1,'What is the name of your favorite childhood friend?'),
            (2,'What street did you live on in third grade?'),
            (3,'What is your oldest sibling’s birthday month and year?  (e.g., January 1900)'),
            (4,'What school did you attend for sixth grade?'),
            (5,'What is the name of your favorite restaurant?'),
            (6,'What was the last name of your favorite teacher?'),
            (7,'What is your maternal grandmothers maiden name?'),
            (8,'In what city or town was your first job?'),
            (9,'What was the name of your first pet?'),
            (10,'What make and color was your first car?  (e.g., toyota blue)');