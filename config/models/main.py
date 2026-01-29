# -*- coding: utf-8 -*-
#  Copyright (c) 2022 - 2026 Ricardo Bartels. All rights reserved.
#
#  wordpress-hash-event-api
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see file LICENSE.txt included in this
#  repository or visit: <https://opensource.org/licenses/MIT>.

from pydantic import Field
from pydantic_settings import SettingsConfigDict

from config.models import EnvOverridesBaseSettings
from config.log import default_log_level


class MainConfigSettings(EnvOverridesBaseSettings):
    log_level: str = Field(default=default_log_level, json_schema_extra={"env": ("log_level", "main_log_level")})

    model_config = SettingsConfigDict(
        env_prefix=f"{__name__.split('.')[-1]}_",
    )
