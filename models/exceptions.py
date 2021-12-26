# -*- coding: utf-8 -*-
#  Copyright (c) 2021 Ricardo Bartels. All rights reserved.
#
#  wordpress-hash-event-api
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see file LICENSE.txt included in this
#  repository or visit: <https://opensource.org/licenses/MIT>.

from fastapi import HTTPException

class RequestValidationError(HTTPException):
    """
        return Validation Error
    """
    def __init__(self, loc, msg, typ):
        super().__init__(422, [{'loc': loc, 'msg': msg, 'type': typ}])