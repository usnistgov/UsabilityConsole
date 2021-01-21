from console import app
from config import DEBUG, HOST, PORT, RESET_DATABASE_ON_START
from flask import session as flask_session
import os
import logging
import utils

logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] [%(levelname)s] -- %(message)s', datefmt='%d-%b-%y %H:%M:%S')


if __name__ == "__main__":
    logging.debug("Starting server. DEBUG=%s", DEBUG)
    try:
        if DEBUG and RESET_DATABASE_ON_START:
            utils.delete_file_if_exists(os.path.join('console', 'db', 'database.db'), 'Deleting previous database...')

    finally:
        app.run(debug=DEBUG, host=HOST, port=PORT)
