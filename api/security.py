# -*- coding: utf-8 -*-
#  Copyright (c) 2021 Ricardo Bartels. All rights reserved.
#
#  wordpress-hash-event-api
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see file LICENSE.txt included in this
#  repository or visit: <https://opensource.org/licenses/MIT>.

from fastapi.security.api_key import APIKeyHeader, APIKey
from fastapi import Security, HTTPException
from starlette.status import HTTP_403_FORBIDDEN

API_KEY_HEADER_NAME = "Authorization"

api_key = None

api_key_header = APIKeyHeader(name=API_KEY_HEADER_NAME, auto_error=True)


async def get_api_key(api_key_string: str = Security(api_key_header)):

    global api_key

    if api_key is None:
        return None

    if api_key_string == f"Token {api_key}":
        return api_key
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="API token validation failed"
        )

def set_api_key(key: str = None) -> None:
    global api_key

    if key is None:
        return

    api_key = str(key)

# EOF
