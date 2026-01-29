# -*- coding: utf-8 -*-
#  Copyright (c) 2022 - 2026 Ricardo Bartels. All rights reserved.
#
#  wordpress-hash-event-api
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see file LICENSE.txt included in this
#  repository or visit: <https://opensource.org/licenses/MIT>.

from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvOverridesBaseSettings(BaseSettings):
    """
    overrides order of settings read int model
    """

    model_config = SettingsConfigDict(
        env_prefix="",
        case_sensitive=False,
    )

    @classmethod
    def config_section_name(cls):
        return cls.model_config.get("env_prefix", "")[:-1]

    @classmethod
    def defaults_dict(cls):
        return {x: y.default for x, y in cls.model_fields.items()}
