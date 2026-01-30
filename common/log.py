# -*- coding: utf-8 -*-
#  Copyright (c) 2022 - 2026 Ricardo Bartels. All rights reserved.
#
#  wordpress-hash-event-api
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see file LICENSE.txt included in this
#  repository or visit: <https://opensource.org/licenses/MIT>.

import logging


def get_logger():
    """
    common function to retrieve common log handler in project files

    Returns
    -------
    log handler
    """

    # return uvicorn default logger
    return logging.getLogger("uvicorn.error")

# EOF
