import logging
import os
import shutil


def delete_file_if_exists(path, logging_message=None):
    logging.debug(logging_message)
    if os.path.exists(path):
        os.remove(path)


def delete_directory_if_exists(path, logging_message=None):
    logging.debug(logging_message)
    if os.path.exists(path):
        shutil.rmtree(path)