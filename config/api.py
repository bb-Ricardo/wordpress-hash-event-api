# -*- coding: utf-8 -*-
#  Copyright (c) 2021 Ricardo Bartels. All rights reserved.
#
#  wordpress-hash-event-api
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see file LICENSE.txt included in this
#  repository or visit: <https://opensource.org/licenses/MIT>.

from pydantic import BaseModel


class BasicAPISettings(BaseModel):
    description = 'Hash Run API for WordPress Event Manager'
    title = 'Kennel Runs API'
    openapi_url = "/openapi.json"
    root_path = "/api/v1"
    version = '0.1'
    debug = False

# EOF
