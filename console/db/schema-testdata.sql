/***********************************************************************************************************************
    TEST DATA
***********************************************************************************************************************/

INSERT INTO users (role_id, username, password, first_name, last_name, api_key) VALUES (2, 'testuser', 'p4ssw0rd', 'Test', 'User', 'qwerty12345678');          -- user_id: 2
INSERT INTO users (role_id, username, password, first_name, last_name, api_key) VALUES (1, 'js1', 'p4ssw0rd', 'John', 'Smith', 'qwerty12345678');              -- user_id: 3
INSERT INTO users (role_id, username, password, first_name, last_name) VALUES (2, 'alice', 'p4ssw0rd', 'Alice', 'Cooper');          -- user_id: 4
INSERT INTO users (role_id, username, password, first_name, last_name) VALUES (2, 'rmcdonald', 'p4ssw0rd', 'Ronald', 'McDonald');   -- user_id: 5

INSERT INTO security_answers (question_id, user_id, answer) VALUES 
(1, 2,'answer1'), (5, 2,'answer2'), (9, 2,'answer3'),
(1, 3,'answer1'), (5, 3,'answer2'), (9, 3,'answer3'),
(1, 4,'answer1'), (5, 4,'answer2'), (9, 4,'answer3'),
(1, 5,'answer1'), (5, 5,'answer2'), (9, 5,'answer3'),
(1, 1,'john doe'),(5, 1,'pizzaparadise'),(9, 1,'petone');


INSERT INTO sessions (creator_id, name) VALUES (2, "Test Study 1 - P037");      -- session_id: 1
INSERT INTO sessions (creator_id, name) VALUES (4, "Alice's Study - P314");     -- session_id: 2

INSERT INTO entries (session_id, creator_id, value) VALUES (1, 2, "Entry 1-1");       -- entry_id: 1
INSERT INTO entries (session_id, creator_id, value) VALUES (1, 3, "Entry 1-2");       -- entry_id: 2
INSERT INTO entries (session_id, creator_id, value) VALUES (2, 5, "Entry 2-1");       -- entry_id: 3
INSERT INTO entries (session_id, creator_id, value) VALUES (2, 5, "Entry 2-2");       -- entry_id: 4
INSERT INTO entries (session_id, creator_id, value) VALUES (1, 5, "Entry 1-3");       -- entry_id: 5
INSERT INTO entries (session_id, creator_id, value) VALUES (2, 2, "Entry 2-3");       -- entry_id: 6
INSERT INTO entries (session_id, creator_id, value) VALUES (1, 4, "Entry 1-4");       -- entry_id: 7
