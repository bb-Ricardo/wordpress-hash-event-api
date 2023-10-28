# -*- coding: utf-8 -*-
#  Copyright (c) 2022 Ricardo Bartels. All rights reserved.
#
#  wordpress-hash-event-api
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see file LICENSE.txt included in this
#  repository or visit: <https://opensource.org/licenses/MIT>.

from config.models import EnvOverridesBaseSettings


class CalendarConfigSettings(EnvOverridesBaseSettings):
    name: str = "Hash events"
    enable_event_alarm: bool = False
    num_past_weeks_exposed: int = 2

    class Config:
        env_prefix = f"{__name__.split('.')[-1]}_"
