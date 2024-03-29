# -*- coding: utf-8 -*-
#  Copyright (c) 2022 Ricardo Bartels. All rights reserved.
#
#  wordpress-hash-event-api
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see file LICENSE.txt included in this
#  repository or visit: <https://opensource.org/licenses/MIT>.

from datetime import datetime
import html
import re
from typing import List, Any

from pydantic import ValidationError
import pytz

from api.models.run import Hash, HashParams, HashScope
import config
from common.log import get_logger
from common.misc import php_deserialize
from source.database import get_db_handler

log = get_logger()


def get_event_manager_field_data(event_manager_fields: dict, field_name: str, field_value: str = None) -> Any:

    if not isinstance(event_manager_fields, dict) or event_manager_fields.get("event") is None:
        return field_value

    if field_name is None or field_name[0] != "_":
        return field_value

    field_data = event_manager_fields.get("event").get(field_name[1:])

    if field_data is None:
        return field_value

    # noinspection PyBroadException
    try:
        if field_data.get("type") in ["select", "radio"]:
            return field_data.get("options").get(field_value)
        elif field_data.get("type") == "file":
            return php_deserialize(field_value).get(0)
        elif field_data.get("type") == "multiselect":
            ret_list = list()
            for field in php_deserialize(field_value).values():
                ret_list.append(field)
            return ret_list
        elif field_data.get("type") == "timezone":
            return pytz.timezone(field_value)
        else:
            return field_value
    except Exception:
        pass

    return None


def passes_filter_params(params: HashParams, hash_event: Hash) -> bool:

    def compare_attributes(value_a, value_b):

        if type(value_a) == type(value_b):
            if "__gt" in key and value_b > value_a:
                return True
            elif "__lt" in key and value_b < value_a:
                return True
            elif value_b == value_a:
                return True

        return False

    matches = list()
    for key, value in params.dict().items():

        # skip unsupported keys like: __pydantic_initialised__
        if key.startswith("__"):
            continue

        if value is None or key in ["id", "limit"]:
            continue

        # handled directly via DB query
        if key.startswith("last_update"):
            continue

        event_value = getattr(hash_event, key, None)
        if type(value) == type(event_value) == str and value.lower() in event_value.lower():
            matches.append(True)
            continue

        if type(value) == type(event_value) == bool and value == event_value:
            matches.append(True)
            continue

        if type(value) == HashScope and value == event_value:
            matches.append(True)
            continue

        if key.startswith("start_date") and compare_attributes(value, getattr(hash_event, "start_date")):
            matches.append(True)
            continue

        if key.startswith("run_number") and compare_attributes(value, getattr(hash_event, "run_number")):
            matches.append(True)
            continue

        matches.append(False)

    return False if False in matches else True


def get_hash_runs(params: HashParams) -> List[Hash]:
    """

    """

    conn = get_db_handler()

    post_query_data = {
        "post_id": params.id
    }

    # filter last update directly via db query
    if params.last_update is not None:
        post_query_data["last_update"] = params.last_update
        post_query_data["compare_type"] = "eq"
    elif params.last_update__lt is not None:
        post_query_data["last_update"] = params.last_update__lt
        post_query_data["compare_type"] = "lt"
    elif params.last_update__gt is not None:
        post_query_data["last_update"] = params.last_update__gt
        post_query_data["compare_type"] = "gt"

    posts = conn.get_posts(**post_query_data)

    return_list = list()
    if isinstance(posts, list):
        post_ids = [post.get("id") for post in posts]
    else:
        log.error(f"DB query should return a list, got {type(posts)}")
        return return_list

    if len(posts) == 0:
        return return_list

    post_meta = conn.get_posts_meta(post_ids)
    event_manager_form_fields = php_deserialize(conn.get_config_item("event_manager_submit_event_form_fields"))

    for post in posts:

        post_attr = {x.get("meta_key"): x.get("meta_value") for x in
                     [d for d in post_meta
                      if d.get("post_id") == post.get("id") and len(str(d.get("meta_value"))) != 0
                      ]
                     }

        # if start date is not set, ignore event
        if post_attr.get("_event_start_date") is None:
            continue

        if post.get("post_content") is None or len(post.get("post_content")) == 0:
            continue

        hash_data = {
            "id": post.get("id"),
            "last_update": post.get("post_modified"),
            "event_name": post.get("post_title"),
            "kennel_name": config.app_settings.hash_kennels[0],
            "event_description": post.get("post_content"),
            "event_type": post.get("post_type") or config.app_settings.default_run_type,
            "event_geographic_scope": HashScope.Unspecified,
            "start_date": post_attr.get("_event_start_date"),
            "end_date": post_attr.get("_event_end_date"),
            "run_number": post_attr.get("_hash_run_number"),
            "run_is_counted": True,
            "deleted": True,
            "hares": post_attr.get("_hash_hares"),
            "contact": post_attr.get("_hash_contact"),
            "geo_lat": post_attr.get("geolocation_lat"),
            "geo_long": post_attr.get("geolocation_long"),
            "geo_location_name": post_attr.get("geolocation_formatted_address"),
            "geo_map_url": post_attr.get("_hash_geo_map_url"),
            "location_name": post_attr.get("_event_location"),
            "location_additional_info": post_attr.get("_hash_location_specifics"),
            "facebook_group_id": config.app_settings.default_facebook_group_id,
            "hash_cash_members": config.app_settings.default_hash_cash,
            "hash_cash_non_members": config.app_settings.default_hash_cash_non_members,
            "event_currency": config.app_settings.default_currency,
            "hash_cash_extras": post_attr.get("_hash_cash_extras"),
            "extras_description": post_attr.get("_hash_extras_description"),
            "event_hidden": True if post_attr.get("_hash_event_hidden") == '1' else False
        }

        # validate time attributes
        try:
            datetime.strptime(hash_data.get("start_date"), '%Y-%m-%d %H:%M:%S')
        except ValueError:
            log.error(f"Start date '{hash_data.get('start_date')}' is not set or missing the time string")
            continue

        if hash_data.get("end_date") is not None:
            try:
                datetime.strptime(hash_data.get("end_date"), '%Y-%m-%d %H:%M:%S')
            except ValueError:
                log.warning(f"End date '{hash_data.get('end_date')}' is not set or missing the time string")
                hash_data["end_date"] = None

        # only published and expired events count as not deleted
        if post.get("post_status") in ["publish", "expired"] and post_attr.get("_cancelled") == "0":
            hash_data["deleted"] = False

        # update hash cash if present
        if post_attr.get("_hash_cash") is not None and len(str(post_attr.get("_hash_cash"))) > 0:
            hash_data["hash_cash_members"] = post_attr.get("_hash_cash")

        if post_attr.get("_hash_cash_non_members") is not None and \
                len(str(post_attr.get("_hash_cash_non_members"))) > 0:

            hash_data["hash_cash_non_members"] = post_attr.get("_hash_cash_non_members")
        elif hash_data.get("hash_cash_non_members") is None:
            hash_data["hash_cash_non_members"] = hash_data.get("hash_cash_members")

        # get event url and unescape the link
        # noinspection PyBroadException
        try:
            hash_data["event_url"] = html.unescape(post.get("guid"))
        except Exception:
            pass

        # get image url from php serializer
        hash_data["image_url"] = get_event_manager_field_data(
            event_manager_form_fields, "_event_banner", post_attr.get("_event_banner"))

        # get kennel name
        kennel_name = get_event_manager_field_data(
            event_manager_form_fields, "_hash_kennel", post_attr.get("_hash_kennel"))

        if kennel_name is not None and kennel_name in config.app_settings.hash_kennels:
            hash_data["kennel_name"] = kennel_name

        # get event geo scope
        event_geographic_scope = post_attr.get("_hash_scope")
        if event_geographic_scope is not None and event_geographic_scope in [e.value for e in HashScope]:
            hash_data["event_geographic_scope"] = event_geographic_scope

        # get event attributes
        event_attributes = get_event_manager_field_data(
            event_manager_form_fields, "_hash_attributes", post_attr.get("_hash_attributes"))

        if event_attributes is not None and isinstance(event_attributes, list):
            hash_data["event_attributes"] = event_attributes

        # handle geo_map_url
        if hash_data.get("geo_map_url") is None:
            if hash_data.get("geo_lat") is not None and hash_data.get("geo_long") is not None:

                hash_data["geo_map_url"] = config.app_settings.maps_url_template.format(
                    lat=hash_data.get("geo_lat"),
                    long=hash_data.get("geo_long")
                )

        # Parse coordinates out of OSM link (e.g. https://www.openstreetmap.org/#map=15/52.4512/13.4471)
        else:
            pattern = r"#map=\d+/(?P<latitude>[-]?\d+\.\d+)/(?P<longitude>[-]?\d+\.\d+)"
            if "google" in hash_data.get("geo_map_url"):
                pattern = r".*\!3d(?P<latitude>[-]?\d+\.\d+)\!4d(?P<longitude>[-]?\d+\.\d+).*"

            match = re.search(pattern, hash_data.get("geo_map_url"))
            if match:
                hash_data["geo_lat"] = float(match.group("latitude"))
                hash_data["geo_long"] = float(match.group("longitude"))

        # parse event data
        try:
            run = Hash(**hash_data)
        except ValidationError as e:
            e = str(e).replace('\n', ":")
            log.error(f"Event (id: {post.get('id')}) parsing error: {e}")
            continue

        event_time_zone = get_event_manager_field_data(event_manager_form_fields,
                                                       "_event_timezone", post_attr.get("_event_timezone"))

        if event_time_zone is None and config.app_settings.timezone_string is not None:
            event_time_zone = config.app_settings.timezone_string

        # add timezone information to timestamp
        if event_time_zone is not None:

            if isinstance(run.start_date, datetime):
                run.start_date = event_time_zone.localize(run.start_date)

            if isinstance(run.end_date, datetime):
                run.end_date = event_time_zone.localize(run.end_date)

        if config.app_settings.timezone_string is not None:
            if isinstance(run.last_update, datetime):
                run.last_update = config.app_settings.timezone_string.localize(run.last_update)

        # apply filters
        if passes_filter_params(params, run) is False:
            continue

        return_list.append(run)

        if params.limit is not None and len(return_list) >= params.limit:
            break

    log.debug(f"returning '{len(return_list)}' run/event results")

    return return_list
# EOF
