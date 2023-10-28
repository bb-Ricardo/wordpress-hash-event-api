# -*- coding: utf-8 -*-
#  Copyright (c) 2022 Ricardo Bartels. All rights reserved.
#
#  wordpress-hash-event-api
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see file LICENSE.txt included in this
#  repository or visit: <https://opensource.org/licenses/MIT>.

from config.models import EnvOverridesBaseSettings
from typing import Union


class APIConfigSettings(EnvOverridesBaseSettings):
    token: Union[str, None] = None
    root_path: str = "/api/v1"

    class Config:
        env_prefix = f"{__name__.split('.')[-1]}_"
