# -*- coding: utf-8 -*-
#  Copyright (c) 2022 Ricardo Bartels. All rights reserved.
#
#  wordpress-hash-event-api
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see file LICENSE.txt included in this
#  repository or visit: <https://opensource.org/licenses/MIT>.

from typing import Tuple, Any

from pydantic import BaseModel, ConfigDict
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvOverridesBaseSettings(BaseSettings):
    """
    overrides order of settings read int model
    """

    model_config = SettingsConfigDict(
        env_prefix="",
        env_settings_sources=("dotenv-env", "env"),
    )

    @classmethod
    def config_section_name(cls):
        return cls.model_config.get("env_prefix", "")[:-1]

    @classmethod
    def defaults_dict(cls):
        return {x: y.default for x, y in cls.model_fields.items()}

    # class Config:
    #     env_prefix = ""

    #     @classmethod
    #     def customise_sources(
    #         cls,
    #         init_settings: SettingsSourceCallable,
    #         env_settings: SettingsSourceCallable,
    #         file_secret_settings: SettingsSourceCallable,
    #     ) -> Tuple[SettingsSourceCallable, ...]:
    #         return env_settings, init_settings, file_secret_settings
