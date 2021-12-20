# -*- coding: utf-8 -*-
#  Copyright (c) 2020 - 2021 Ricardo Bartels. All rights reserved.
#
#  netbox-sync.py
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see file LICENSE.txt included in this
#  repository or visit: <https://opensource.org/licenses/MIT>.

import os
import logging
from logging.handlers import RotatingFileHandler

# define valid log levels
valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]


def get_logger():
    """
    common function to retrieve common log handler in project files

    Returns
    -------
    log handler
    """

    return logging.getLogger("MyFastAPI")


def setup_logging(log_level=None, log_file=None):
    """
    Set up logging for the whole program and return a log handler

    Parameters
    ----------
    log_level: str
        valid log level to set logging to
    log_file: str
        name of the log file to log to

    Returns
    -------
    log handler to use for logging
    """

    log_file_max_size_in_mb = 10
    log_file_max_rotation = 5

    log_format = '%(asctime)s - %(levelname)s: %(message)s'

    if log_level is None or log_level == "":
        raise Exception("ERROR: log level undefined or empty. Check config please.")

    # check set log level against self defined log level array
    if not log_level.upper() in valid_log_levels:
        raise Exception(f"ERROR: Invalid log level: {log_level}")

    # check the provided log level
#        logging.basicConfig(level=logging.DEBUG, format=log_format)
    numeric_log_level = getattr(logging, log_level.upper(), None)

    log_format = logging.Formatter(log_format)

    # create logger instance
    logger = get_logger()

    logger.setLevel(numeric_log_level)

    # setup stream handler
    # in DEBUG3 the root logger gets redefined, that would print every log message twice
    if log_level != "DEBUG3":
        log_stream = logging.StreamHandler()
        log_stream.setFormatter(log_format)
        logger.addHandler(log_stream)

    # setup log file handler
    if log_file is not None:
        # base directory is three levels up
        base_dir = os.sep.join(__file__.split(os.sep)[0:-3])
        if log_file[0] != os.sep:
            log_file = f"{base_dir}{os.sep}{log_file}"

        log_file_handler = None
        try:
            log_file_handler = RotatingFileHandler(
                filename=log_file,
                maxBytes=log_file_max_size_in_mb * 1024 * 1024,  # Bytes to Megabytes
                backupCount=log_file_max_rotation
            )
        except Exception as e:
            raise Exception(f"ERROR: Problems setting up log file: {e}")

        log_file_handler.setFormatter(log_format)
        logger.addHandler(log_file_handler)

    return logger