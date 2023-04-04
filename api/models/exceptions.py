# -*- coding: utf-8 -*-
#  Copyright (c) 2022 Ricardo Bartels. All rights reserved.
#
#  wordpress-hash-event-api
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see file LICENSE.txt included in this
#  repository or visit: <https://opensource.org/licenses/MIT>.

from fastapi import HTTPException
from starlette.status import HTTP_403_FORBIDDEN, HTTP_422_UNPROCESSABLE_ENTITY


class RequestValidationError(HTTPException):
    """
        return Validation Error
    """
    def __init__(self, loc, msg, typ):
        super().__init__(HTTP_422_UNPROCESSABLE_ENTITY, [{'loc': loc, 'msg': msg, 'type': typ}])


class APITokenValidationFailed(HTTPException):
    """
        return a forbidden due to wrong API token
    """
    def __init__(self):
        super().__init__(status_code=HTTP_403_FORBIDDEN, detail="API token validation failed")


class CredentialsInvalid(HTTPException):
    """
        return a forbidden due to wrong API token
    """
    def __init__(self):
        super().__init__(status_code=HTTP_403_FORBIDDEN, detail="Credentials invalid")
