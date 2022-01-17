# -*- coding: utf-8 -*-
#  Copyright (c) 2022 Ricardo Bartels. All rights reserved.
#
#  wordpress-hash-event-api
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see file LICENSE.txt included in this
#  repository or visit: <https://opensource.org/licenses/MIT>.

# taken from here: https://stackoverflow.com/questions/62934384/how-to-add-timestamp-to-each-request-in-uvicorn-logs

import psutil
import os

default_log_level = "INFO"

run_by_systemd = False

# if app is started via systemd then strip time stamp from log format
request_logger_config_format = '%(asctime)s - %(levelname)s: %(client_addr)s - "%(request_line)s" %(status_code)s'
try:
    if psutil.Process(psutil.Process(os.getpid()).ppid()).name() == "systemd":
        run_by_systemd = True
        request_logger_config_format = '%(levelname)s: %(client_addr)s - "%(request_line)s" %(status_code)s'
except Exception as e:
    print(f"unable to determine parent process name: {e}")


request_logger_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": request_logger_config_format,
            "use_colors": True
        },
    },
    "handlers": {
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
    },
    "loggers": {
        "uvicorn.access": {
            "handlers": ["access"],
            "level": "INFO",
            "propagate": False
        },
    },
}
