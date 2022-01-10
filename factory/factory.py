# -*- coding: utf-8 -*-
#  Copyright (c) 2021 Ricardo Bartels. All rights reserved.
#
#  wordpress-hash-event-api
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see file LICENSE.txt included in this
#  repository or visit: <https://opensource.org/licenses/MIT>.

from datetime import datetime
import pytz
import html
from typing import List

from pydantic import ValidationError

from api.models.run import Hash, HashParams, HashScope
import config
from common.log import get_logger
from common.misc import php_deserialize
from source.database import get_db_handler


log = get_logger()


def get_event_manager_field_data(event_manager_fields: dict, field_name: str, field_value: str = None):

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

    def compare_attributes(value, event_value):
        if type(value) == type(event_value):
            if "__gt" in key and event_value > value:
                return True
            elif "__lt" in key and event_value < value:
                return True
            elif event_value == value:
                return True
        return False

    matches = list()
    for key, value in params.dict().items():
        if value is None or key == "id":
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


def get_hash_runs(params: HashParams) -> List:
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

    post_meta = conn.get_posts_meta(params.id)
    event_manager_form_fields = php_deserialize(conn.get_config_item("event_manager_submit_event_form_fields"))

    error = None

    import pprint
    #pprint.pprint(event_manager_form_fields)
    return_list = list()
    for post in posts or list():

        post_attr = {x.get("meta_key"): x.get("meta_value") for x in
                     [d for d in post_meta
                      if d.get("post_id") == post.get("id") and len(str(d.get("meta_value"))) != 0
                      ]
                     }

        # pprint.pprint(post_attr)
        pprint.pprint(post.get("post_status"))

        # if start date is not set, ignore event
        if post_attr.get("_event_start_date") is None:
            continue

        if post.get("post_content") is None or len(str(post.get("post_content"))) == 0:
            continue

        hash_data = {
            "id": post.get("id"),
            "last_update": post.get("post_modified"),
            "event_name": post.get("post_title"),
            "kennel_name": config.app_settings.default_kennel,
            "event_description": post.get("post_content"),
            "event_type": post.get("post_category") or "Regular Run",
            "start_date": post_attr.get("_event_start_date"),
            "end_date": post_attr.get("_event_end_date"),
            "run_number": post_attr.get("_hash_run_number"),
            "run_is_counted": True,
            "hares": post_attr.get("_hash_hares"),
            "contact": post_attr.get("_hash_contact"),
            "geo_lat": post_attr.get("geolocation_lat"),
            "geo_long": post_attr.get("geolocation_long"),
            "geo_location_name": post_attr.get("geolocation_formatted_address"),
            "location_name": post_attr.get("_event_location"),
            "location_additional_info": post_attr.get("_hash_location_specifics"),
            "facebook_group_id": config.app_settings.default_facebook_group_id,
            "hash_cash_members": config.app_settings.default_hash_cash,
            "hash_cash_non_members": config.app_settings.default_hash_cash,
            "event_currency": config.app_settings.default_currency,
            "hash_cash_extras": post_attr.get("_hash_cash_extras"),
            "extras_description": post_attr.get("_hash_extras_description"),
            "event_hidden": True if post_attr.get("_hash_event_hidden") == '1' else False
        }

        # valide time attributes
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
        else:
            hash_data["deleted"] = True

        # update hash cash if present
        if post_attr.get("_hash_cash") is not None and len(str(post_attr.get("_hash_cash"))) > 0:
            hash_data["hash_cash_members"] = post_attr.get("_hash_cash")
        
        if post_attr.get("_hash_cash_non_members") is not None and len(str(post_attr.get("_hash_cash_non_members"))) > 0:
            hash_data["hash_cash_non_members"] = post_attr.get("_hash_cash_non_members")
        else:
            hash_data["hash_cash_non_members"] = hash_data["hash_cash_members"]

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
        kennel_name = get_event_manager_field_data(event_manager_form_fields, "_hash_kennel", post_attr.get("_hash_kennel"))
        if kennel_name is not None and kennel_name in config.app_settings.hash_kennels:
            hash_data["kennel_name"] = kennel_name

        # get event geo scope
        event_geographic_scope = post_attr.get("_hash_scope")
        if event_geographic_scope is not None and event_geographic_scope in [e.value for e in HashScope]:
            hash_data["event_geographic_scope"] = event_geographic_scope
        else:
            hash_data["event_geographic_scope"] = HashScope.Unspecified

        # get event attributes
        event_attributes = get_event_manager_field_data(
            event_manager_form_fields, "_hash_attributes", post_attr.get("_hash_attributes"))
        if event_attributes is not None and isinstance(event_attributes, list):
            hash_data["event_attributes"] = event_attributes

        # parse event data
        #pprint.pprint(hash_data)

        try:
            run = Hash(**hash_data)
        except ValidationError as e:
            e = str(e).replace('\n', ":")
            log.error(f"Event (id: {post.get('id')}) parsing error: {e}")
            # pprint.pprint(post_attr)
            # pprint.pprint(post)
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

        #print(run.json(indent=4, sort_keys=True))

        # apply filters
        if passes_filter_params(params, run) is False:
            continue

        return_list.append(run)

        if params.limit is not None and len(return_list) >= params.limit:
            break

    log.debug(f"returning '{len(return_list)}' run/event results")

    # 2nd return value is currently unused
    return return_list, error

# EOF
