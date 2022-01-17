# -*- coding: utf-8 -*-
#  Copyright (c) 2022 Ricardo Bartels. All rights reserved.
#
#  wordpress-hash-event-api
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see file LICENSE.txt included in this
#  repository or visit: <https://opensource.org/licenses/MIT>.

import logging

from config.log import run_by_systemd

# define valid log levels
valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]


def get_logger():
    """
    common function to retrieve common log handler in project files

    Returns
    -------
    log handler
    """

    return logging.getLogger("wordpress-hash-event-api")


def setup_logging(log_level=None):
    """
    Set up logging for the whole program and return a log handler

    Parameters
    ----------
    log_level: str
        valid log level to set logging to

    Returns
    -------
    log handler to use for logging
    """

    log_format = '%(asctime)s - %(levelname)s: %(message)s'

    if run_by_systemd is True:
        log_format = '%(levelname)s: %(message)s'

    if log_level is None or log_level == "":
        print("ERROR: log level undefined or empty. Check config please.")
        exit(1)

    # check set log level against self defined log level array
    if not log_level.upper() in valid_log_levels:
        print(f"ERROR: Invalid log level defined: {log_level}")
        exit(1)

    # check the provided log level
    numeric_log_level = getattr(logging, log_level.upper(), None)

    log_format = logging.Formatter(log_format)

    # create logger instance
    logger = get_logger()

    logger.setLevel(numeric_log_level)

    # setup stream handler
    log_stream = logging.StreamHandler()
    log_stream.setFormatter(log_format)
    logger.addHandler(log_stream)

    return logger

# EOF
