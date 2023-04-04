# -*- coding: utf-8 -*-
#  Copyright (c) 2022 Ricardo Bartels. All rights reserved.
#
#  wordpress-hash-event-api
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see file LICENSE.txt included in this
#  repository or visit: <https://opensource.org/licenses/MIT>.

from config.models import EnvOverridesBaseSettings
from pydantic import validator


# noinspection PyMethodParameters
class ListMonkSettings(EnvOverridesBaseSettings):
    enabled: bool = False
    send_campaign: bool = False
    username: str
    password: str
    host: str
    campaign_template_id: int = None
    body_template_id: int
    list_ids: str

    class Config:
        env_prefix = f"{__name__.split('.')[-1]}_"

    @validator("list_ids")
    def split_list_ids(cls, value):
        if isinstance(value, str):
            try:
                value = [int(x) for x in value.split(",")]
            except Exception as e:
                raise ValueError(f"unable to pars '{value}' into list of ints: {e}")
        return value
