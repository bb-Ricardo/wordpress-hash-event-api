# -*- coding: utf-8 -*-
#  Copyright (c) 2021 Ricardo Bartels. All rights reserved.
#
#  wordpress-hash-event-api
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see file LICENSE.txt included in this
#  repository or visit: <https://opensource.org/licenses/MIT>.

from typing import Optional, List, Dict, Any
from datetime import datetime
from pytz import UTC
from enum import Enum

from pydantic import BaseModel, AnyHttpUrl, Field, validator, root_validator
from pydantic.dataclasses import dataclass
from fastapi import Query
from fastapi.exceptions import RequestValidationError

from config.hash import hash_attributes, hash_scope
from common.misc import format_slug
from models.exceptions import RequestValidationError


# generate from config.hash lists
HashAttributes = Enum('HashAttributes', {x: format_slug(x) for x in hash_attributes}, type=str)
HashAttributes.__doc__ = "attributes which can be assigned to an run/event"

HashScope = Enum('HashScope', {x: format_slug(x) for x in hash_scope}, type=str)
HashScope.__doc__ = "scope of the event"

# assamble list of hash attributes to add to description
hash_attribute_list = ", ".join([e.value for e in HashAttributes])


@dataclass
class HashParams:
    """
        defines params to filter for event
        If more than one filter is defined, all filters have to match in oder to return an event
    """

    id: Optional[int] = None
    last_update: Optional[int] = Query(None, description="set as unix timestamp")
    last_update__gt: Optional[int] = Query(None, description="set as unix timestamp")
    last_update__lt: Optional[int] = Query(None, description="set as unix timestamp")
    event_name: Optional[str] = None
    kennel_name: Optional[str] = None
    event_type: Optional[str] = None
    event_attributes: Optional[str] = Query(None,
                                            description=f"comma separated list of event attributes - "
                                                        f"available values: {hash_attribute_list}")
    event_geographic_scope: Optional[HashScope] = None
    start_date: Optional[int] = Query(None, description="set as unix timestamp")
    start_date__gt: Optional[int] = Query(None, description="set as unix timestamp")
    start_date__lt: Optional[int] = Query(None, description="set as unix timestamp")
    deleted: Optional[bool] = None
    run_number: Optional[int] = None
    run_number__gt: Optional[int] = None
    run_number__lt: Optional[int] = None
    run_is_counted: Optional[bool] = None
    hares: Optional[str] = None
    location_name: Optional[str] = None
    limit: Optional[int] = None

    def dict(cls):
        return {k: v for k, v in cls.__dict__.items() if k != "__initialised__"}

    @root_validator()
    def check_everything(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if set(values.values()) == {None}:
            return values

        # check mutual exclusive params
        for mutual_exclusive in ["last_update", "start_date", "run_number"]:
            param_name_set = None
            for key, value in values.items():
                if value is None:
                    continue
                if key.startswith(mutual_exclusive):
                    if param_name_set is None:
                        param_name_set = key
                        continue
                    else:
                        raise RequestValidationError(loc=["query", mutual_exclusive],
                                                     msg=f"parma '{param_name_set}' and '{key}' cannot be set "
                                                         f"within the same request",
                                                     typ="value_error")

        # convert to datetime
        for timestamp_key in ["last_update", "start_date"]:
            for key, value in values.items():
                if value is None:
                    continue
                if key.startswith(timestamp_key):
                    try:
                        values[key] = datetime.fromtimestamp(value, tz=UTC)
                    except Exception as e:
                        raise RequestValidationError(loc=["query", key],
                                                     msg=f"parma '{key}' {e}: {value}",
                                                     typ="value_error")

        # check valid run attributes
        wrong_event_attributes = list()
        valid_event_attributes = [e.value for e in HashAttributes]
        
        if values.get("event_attributes") is not None:
            for event_attribute in values.get("event_attributes").split(","):
                if event_attribute not in valid_event_attributes:
                    wrong_event_attributes.append(event_attribute)

        if len(wrong_event_attributes) > 0:
            wrong_attributes_string = "', '".join(wrong_event_attributes)
            if len(wrong_event_attributes) == 1:
                msg = "param '{}' is an invalid event attribute"
            else:
                msg = "params '{}' are invalid event attributes"
            raise RequestValidationError(loc=["query", "event_attributes"],
                                         msg=msg.format(wrong_attributes_string), typ="value_error")

        return values


class Hash(BaseModel):
    """
        a Hash run/event object
    """
    id: int
    last_update: datetime = Field(description="in ISO format")

    event_name: str
    kennel_name: str
    event_description: str
    event_type: str = Field(description="name of type of event")
    event_attributes: Optional[List[HashAttributes]] = None
    event_geographic_scope: Optional[HashScope] = Field(HashScope['Unspecified'])

    start_date: datetime = Field(None, description="in ISO format")
    end_date: Optional[datetime] = Field(None, description="in ISO format")
    deleted: bool = False

    run_number: Optional[int] = Field(None, description="run number of this type of run")
    run_is_counted: bool = Field(None, description="True if this run should be counted")
    hares: Optional[str] = Field(None, description="Name of the runs hares")

    contact: Optional[str] = Field(None, description="phone number or email of a contact")
    geo_lat: Optional[str] = Field(None, description="geo location latitude")
    geo_long: Optional[str] = Field(None, description="geo location longitude")
    geo_location_name: Optional[str] = Field(None, description="geo location name/address")
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
    event_hidden: bool = False

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
