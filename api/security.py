# -*- coding: utf-8 -*-
#  Copyright (c) 2022 Ricardo Bartels. All rights reserved.
#
#  wordpress-hash-event-api
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see file LICENSE.txt included in this
#  repository or visit: <https://opensource.org/licenses/MIT>.

from fastapi.security.api_key import APIKeyHeader
from fastapi import Security

from api.models.exceptions import APITokenValidationFailed

API_KEY_HEADER_NAME = "Authorization"
API_KEY_TYPE = "Token"
api_key = None

api_key_header = APIKeyHeader(name=API_KEY_HEADER_NAME, auto_error=True)


async def api_key_valid(api_key_string: str = Security(api_key_header)) -> bool:

    # return
    if api_key is None:
        return True

    if api_key_string == f"{API_KEY_TYPE} {api_key}":
        return True
    else:
        raise APITokenValidationFailed


def set_api_key(key: str = None) -> None:
    global api_key

    if key is None:
        return

    api_key = str(key)

# EOF
