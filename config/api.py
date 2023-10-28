# -*- coding: utf-8 -*-
#  Copyright (c) 2022 Ricardo Bartels. All rights reserved.
#
#  wordpress-hash-event-api
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see file LICENSE.txt included in this
#  repository or visit: <https://opensource.org/licenses/MIT>.

from pydantic import BaseModel


class BasicAPISettings(BaseModel):
    description: str = 'Hash Run API for WordPress Event Manager'
    title: str = 'Kennel Runs API'
    openapi_url: str = "/openapi.json"
    root_path: str = "/api/v1"
    version: str = '1.0.1'
    debug: bool = False

# EOF
