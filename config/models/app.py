# -*- coding: utf-8 -*-
#  Copyright (c) 2022 Ricardo Bartels. All rights reserved.
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


# noinspection PyMethodParameters
class AppSettings(EnvOverridesBaseSettings):
    hash_kennels: Union[str, List]
    default_hash_cash: int = None
    default_hash_cash_non_members: int = None
    default_run_type: str = "Regular Run"
    default_currency: str = None
    default_facebook_group_id: int = None
    timezone_string: str = None

    # currently not implemented in WP Event manager
    # default_kennel: str = None
    # default_run_attributes: Union[str, List] = None

    class Config:
        env_prefix = f"{__name__.split('.')[-1]}_"

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
        if isinstance(value, str):
            value = split_quoted_string(value, strip=True)
        return value

    """
    # currently not implemented in WP Event manager
    @validator("default_run_attributes")
    def split_run_attributes(cls, value):
        if isinstance(value, str):
            value = split_quoted_string(value, strip=True)
        return value

    @validator("default_kennel")
    def check_default_kennel(cls, value, values):
        if value is None:
            return

        if value not in values.get("hash_kennels"):
            raise ValueError(f"Hash kennel '{value}' must be in list of 'hash_kennels': {values.get('hash_kennels')}")

        return value
    """
