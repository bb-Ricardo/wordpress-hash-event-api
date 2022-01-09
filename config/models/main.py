# -*- coding: utf-8 -*-
#  Copyright (c) 2021 Ricardo Bartels. All rights reserved.
#
#  wordpress-hash-event-api
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see file LICENSE.txt included in this
#  repository or visit: <https://opensource.org/licenses/MIT>.


from config.models import EnvOverridesBaseSettings
from pydantic import Field

class MainConfigSettings(EnvOverridesBaseSettings):
    log_level: str = Field("INFO", env={"log_level", "main_log_level"})

    class Config:
        env_prefix = f"{__module__.split('.')[-1]}_"