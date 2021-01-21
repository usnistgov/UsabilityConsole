from console.routes.utils import *
from console.db import Database
from http import HTTPStatus
import json
import logging
import time
import datetime

# if there is no active session, a new one will be created with the timestamp as the name with session owner being whoever is associated with the generated api key

###################################################################################
# application/json; charset=UTF-8
#
# [
# 	{
# 		"id": 1,
# 		"timestamp": "20190829121900",
# 		"category": "External",
# 		"message_data": "BUTTON TRIGGER"
# 	}, {
# 		"id": 2,
# 		"timestamp": "20190829121930",
# 		"category": "External",
# 		"message_data": "TELEPORT (13.5, 43.1) TO (18.2, 50.0)"
# 	}
# ]
###################################################################################


@app.route('/ext/<api_key>/<session_id>', methods=['POST'])
def ext_post_event(api_key, session_id):
    logging.debug("EXTERNAL: Event posted")

    payload = request.data

    if len(payload) == 0:
        return "No payload / message body received", HTTPStatus.BAD_REQUEST.value

    db = Database()
    user = db.get_user_by_api_key(api_key)

    if user is None:
        return "Provided API key ('{}') is not associated with any registered user".format(api_key), HTTPStatus.UNAUTHORIZED.value

    try:
        parsed = json.loads(payload)
    except json.decoder.JSONDecodeError as ex:
        return ex.msg, HTTPStatus.BAD_REQUEST.value

    if session_id is None:
        return "No unique session identifier provided", HTTPStatus.BAD_REQUEST.value

    # if get_current_session_id() is None:
        # ext_create_new_session(api_key)
        # session_name = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        # logging.debug("Creating new session: %s (userid: %s)", session_name, user['user_id'])
        # session_id = db.create_session(session_name, user['user_id'])
        # logging.debug("New session id: %s", session_id)
        # set_current_session(session_id, session_name)

    for message in parsed:
        try:
            print(message)
            db.add_entry(session_id, user['user_id'], message['message_data'])
        except (TypeError, KeyError) as ex:
            print(ex)
            return "Payload / message body has invalid formatting", HTTPStatus.BAD_REQUEST.value

    return "OK"


@app.route('/ext/<api_key>/new_session', methods=['POST'])
def ext_create_new_session(api_key):
    logging.debug("EXTERNAL: Create new Session")

    db = Database()
    user = db.get_user_by_api_key(api_key)

    if user is None:
        return "Provided API key ('{}') is not associated with any registered user".format(api_key), HTTPStatus.UNAUTHORIZED.value

    session_name = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    logging.debug("Creating new session: %s (userid: %s)", session_name, user['user_id'])
    session_id = db.create_session(session_name, user['user_id'])
    logging.debug("New session id: %s", session_id)
    set_current_session(session_id, session_name)

    return "New Session ID: '{}'".format(session_id)


@app.route('/ext/<api_key>/<session_id>/alerts', methods=['GET'])
def ext_get_alerts(api_key, session_id):
    if session_id is None or session_id == '':
        return "No unique session identifier provided", HTTPStatus.BAD_REQUEST.value

    db = Database()
    # db_alerts = db.get_all_alerts_and_disable_for_session_id(get_current_session_id())
    db_alerts = db.get_all_alerts_and_disable_for_session_id(session_id)
    alerts = []

    for db_alert in db_alerts:
        alert = {'value': db_alert['value'],
                 'time_created': db_alert['time_created']}
        alerts.append(alert)

    return json.dumps(alerts)
