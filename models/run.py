# -*- coding: utf-8 -*-
#  Copyright (c) 2021 Ricardo Bartels. All rights reserved.
#
#  wordpress-hash-event-api
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see file LICENSE.txt included in this
#  repository or visit: <https://opensource.org/licenses/MIT>.

from typing import Optional, List
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, AnyHttpUrl, Field, validator

class HashAttributes(str, Enum):
    harriette_run = 'harriette-run'
    men_only_hash =  'men-only-hash'
    woman_only_hash = 'woman-only-hash'
    kids_allowed = 'kids-allowed'
    no_kids_allowed = 'no-kids-allowed'
    bring_flashlight = 'bring-flashlight'
    water_on_trail = 'water-on-trail'
    walker_trail = 'walker-trail'
    runner_trail = 'runner-trail'
    long_run_trail = 'long-run-trail'
    pub_crawl = 'pub-crawl'
    on_after = 'on-after'
    baby_jogger_friendly = 'baby-jogger-friendly'
    shiggy_run = 'shiggy-run'
    accessible_by_public_transport = 'accessible-by-public-transport'
    bike_hash = 'bike-hash'
    city_run = 'city-run'
    live_hare = 'live-hare'
    dead_hare = 'dead-hare'
    nighttime_run = 'nighttime-run'
    steep_hills = 'steep-hills'
    charity_event = 'charity-event'
    dog_friendly = 'dog-friendly'
    pick_up_hash = 'pick-up-hash'
    catch_the_hare = 'catch-the-hare'
    bring_cash_on_trail = 'bring-cash-on-trail'
    bag_drop_available = 'bag-drop-available'
    agm: 'AGM'

class HashScope(str, Enum):
    unspecified = 'unspecified'
    regular_run = 'regular-run'
    special_local_event = 'special-local-event'
    special_regional_event = 'special-regional-event'
    nash_hash_event = 'nash-hash-event'
    interhash_event = 'interhash-event'
    world_interhash_event = 'world-interhash-event'
    other_special_event = 'other-special-event'


class Hash(BaseModel):
    """
        The model of a Hash run/event
    """
    id: int
    last_update: datetime = Field(description="in ISO format")

    event_name: str
    kennel_name: str
    event_description: str
    event_type: str = Field(description="name of type of event")
    event_attributes: Optional[List[HashAttributes]] = None
    event_geographic_scope: Optional[HashScope] = Field(HashScope['unspecified'])

    start_date: datetime = Field(None, description="in ISO format")
    end_date: Optional[datetime] = Field(None, description="in ISO format")
    deleted: bool = False

    run_number: Optional[int] = Field(None, description="run number of this type of run")
    run_is_counted: bool = Field(None, description="True if this run should be counted")
    hares: Optional[str] = Field(None, description="Name of the runs hares")

    contact: Optional[str] = Field(None, description="phone number or email of a contact")
    geo_lat: Optional[str] = Field(None, description="geo location latitude")
    geo_long: Optional[str] = Field(None, description="geo location longtitude")
    geo_loncation_name: Optional[str] = Field(None, description="geo location name/address")
    geo_map_url: Optional[AnyHttpUrl] = Field(None, description="a url to the location")
    location_name: Optional[str] = Field(None, description="name of the location")
    location_additional_info: Optional[str] = Field(None, description="additional location description")

    image_url: Optional[AnyHttpUrl] = Field(None, description="public available url to image of this event")
    event_url: Optional[AnyHttpUrl] = Field(None, description="public available url to posting of this event")
    facebook_group_id: Optional[int] = None
    hash_cash_members: Optional[int] = None
    hash_cash_non_members: Optional[int] = None
    event_currency: Optional[str] = Field("€", description="name or currency symbol")
    hash_cash_extras: Optional[int] = None
    extras_description: Optional[str] = None

    class Config:
        json_encoders = {
            # custom output conversion for datetime
            datetime: lambda x: x.isoformat()
        }

    @validator("*")
    def set_empty_strings_to_none(cls, value):
        if isinstance(value, str) and len(value.strip()) == 0:
            return None
        return value

# EOF
