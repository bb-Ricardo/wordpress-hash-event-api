# -*- coding: utf-8 -*-
#  Copyright (c) 2021 Ricardo Bartels. All rights reserved.
#
#  wordpress-hash-event-api
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see file LICENSE.txt included in this
#  repository or visit: <https://opensource.org/licenses/MIT>.

from typing import Union, List
from config.models import EnvOverridesBaseSettings
from pydantic import validator
import pytz

from common.misc import split_quoted_string

class AppSettings(EnvOverridesBaseSettings):
    blogname: str = None
    hash_kennels: Union[str,List]
    default_kennel: str = None
    default_hash_cash: int = None
    timezone_string: str = None
    default_currency: str = None
    default_facebook_group_id: int = None

    class Config:
        env_prefix = f"{__module__.split('.')[-1]}_"

    @validator("timezone_string")
    def check_time_zone_string(cls, value):
        if value is None:
            return

        # noinspection PyBroadException
        try:
            return pytz.timezone(value)
        except Exception:
            raise ValueError(f"Time zone unknown: {value}")

    @validator("hash_kennels")
    def split_hash_kennels(cls, value):
        return split_quoted_string(value, strip=True)

    @validator("default_kennel")
    def check_default_kennel(cls, value, values):
        if value is None:
            return

        if value not in values.get("hash_kennels"):
            raise ValueError(f"Hash kennel '{value}' must be in list of 'hash_kennels': {values.get('hash_kennels')}")

        return value
