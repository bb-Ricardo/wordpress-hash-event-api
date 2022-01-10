# -*- coding: utf-8 -*-
#  Copyright (c) 2021 Ricardo Bartels. All rights reserved.
#
#  wordpress-hash-event-api
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see file LICENSE.txt included in this
#  repository or visit: <https://opensource.org/licenses/MIT>.

from pydantic import Field

from config.models import EnvOverridesBaseSettings
from config.log import default_log_level


class MainConfigSettings(EnvOverridesBaseSettings):
    log_level: str = Field(default_log_level, env={"log_level", "main_log_level"})

    class Config:
        env_prefix = f"{__name__.split('.')[-1]}_"
