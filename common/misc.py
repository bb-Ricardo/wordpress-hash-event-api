# -*- coding: utf-8 -*-
#  Copyright (c) 2021 Ricardo Bartels. All rights reserved.
#
#  wordpress-hash-event-api
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see file LICENSE.txt included in this
#  repository or visit: <https://opensource.org/licenses/MIT>.

import sys


def do_error_exit(log_text):
    """
    log an error and exit with return code 1
    Parameters
    ----------
    log_text : str
        the text to log as error
    """

    print(log_text, file=sys.stderr)
    exit(1)
