# -*- coding: utf-8 -*-
#  Copyright (c) 2021 Ricardo Bartels. All rights reserved.
#
#  wordpress-hash-event-api
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see file LICENSE.txt included in this
#  repository or visit: <https://opensource.org/licenses/MIT>.

from typing import Tuple

from pydantic import BaseSettings
from pydantic.env_settings import SettingsSourceCallable


class EnvOverridesBaseSettings(BaseSettings):
    """
    overrides order of settings read int model
    """

    @classmethod
    def config_section_name(cls):
        return cls.Config.env_prefix[:-1]

    @classmethod
    def defaults_dict(cls):
        return {x.name: x.default for x in cls.__fields__.values()}

    class Config:        
        @classmethod
        def customise_sources(
            cls,
            init_settings: SettingsSourceCallable,
            env_settings: SettingsSourceCallable,
            file_secret_settings: SettingsSourceCallable,
        ) -> Tuple[SettingsSourceCallable, ...]:
            return env_settings, init_settings, file_secret_settings
