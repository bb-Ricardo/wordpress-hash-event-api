# -*- coding: utf-8 -*-
#  Copyright (c) 2021 Ricardo Bartels. All rights reserved.
#
#  wordpress-hash-event-api
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see file LICENSE.txt included in this
#  repository or visit: <https://opensource.org/licenses/MIT>.

from datetime import datetime
from source.database import get_db_handler
from models.run import Hash
import html
from phpserialize import loads
import common.config as config
from pydantic import ValidationError
from common.logging import get_logger

log = get_logger()

def get_event_manager_field_data(event_manager_fields: dict, field_name: str, field_value: str = None):

    if not isinstance(event_manager_fields, dict) or event_manager_fields.get("event") is None:
        return field_value

    if field_name is None or field_name[0] != "_":
        return field_value

    field_data = event_manager_fields.get("event").get(field_name[1:])

    if field_data is None:
        return field_value

    try:
        if field_data.get("type") in ["select", "radio"]:
            return field_data.get("options").get(field_value)
        elif field_data.get("type") == "file":
            return php_deserialize(field_value).get(0)
        elif field_data.get("type") == "multiselect":
            ret_list = list()
            for field in php_deserialize(field_value).values():
                ret_list.append(field_data.get("options").get(field))
            return ret_list
        else:
            return field_value
    except Exception:
        pass

    return None

def php_deserialize(string: str):

    try: 
        return loads(string.encode('utf-8'), charset='utf-8', decode_strings=True)
    except Exception:
        pass

def get_hash_runs(id: int = None):

    conn = get_db_handler()

    posts = conn.get_posts(id)
    post_meta = conn.get_posts_meta(id)
    event_manager_form_fields = php_deserialize(conn.get_config_item("event_manager_form_fields"))

    return_list = list()
    single_run = None
    for post in posts or list():

        post_attr = {x.get("meta_key"): x.get("meta_value") for x in 
                        [d for d in post_meta 
                            if d.get("post_id") == post.get("id") and len(str(d.get("meta_value"))) != 0
                        ]
                    }

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
            "run_number": post_attr.get("_run_number"),
            "run_is_counted": True,
            "hares": post_attr.get("_hares"),
            "contact": post_attr.get("_contact"),
            "geo_lat": post_attr.get("geolocation_lat"),
            "geo_long": post_attr.get("geolocation_long"),
            "geo_long": post_attr.get("geolocation_long"),
            "geo_loncation_name": post_attr.get("geolocation_formatted_address"),
            "location_name": post_attr.get("_event_location"),
            "location_additional_info": post_attr.get("_location_specifics"),
            "facebook_group_id": config.app_settings.dafault_facebook_group_id,
            "hash_cash_members": config.app_settings.default_hash_cash,
            "hash_cash_non_members": config.app_settings.default_hash_cash,
            "event_currency": config.app_settings.default_currency,
            "hash_cash_extras": post_attr.get("_hash_cash_extras"),
            "extras_description": post_attr.get("_extras_description"),
        }

        # only publisched and expired events count as not deleted
        if post.get("post_status") in ["publish", "expired"] and post_attr.get("_cancelled") == "0":
            hash_data["deleted"] = False
        else:
            hash_data["deleted"] = True

        # update hash cash if present
        if post_attr.get("_hash_cash") is not None and len(str(post_attr.get("_hash_cash"))) > 0:
            hash_data["hash_cash_members"] = post_attr.get("_hash_cash")
            hash_data["hash_cash_non_members"] = post_attr.get("_hash_cash")

        # get event url and unescape the link
        try:
            hash_data["event_url"] = html.unescape(post.get("guid"))
        except Exception:
            pass

        # get image url from php serializer
        hash_data["image_url"] = get_event_manager_field_data(event_manager_form_fields, "_event_banner", post_attr.get("_event_banner"))

        # get kennel name
        kennel_name = get_event_manager_field_data(event_manager_form_fields, "_kennel", post_attr.get("_kennel"))
        if kennel_name is not None:
            hash_data["kennel_name"] = kennel_name

        # get event geo scope
        event_geographic_scope = get_event_manager_field_data(event_manager_form_fields, "_run_type", post_attr.get("_run_type"))
        if event_geographic_scope is not None:
            hash_data["event_geographic_scope"] = event_geographic_scope

        # get event attributes
        event_attributes = get_event_manager_field_data(event_manager_form_fields, "_attributes", post_attr.get("_attributes"))
        if event_attributes is not None and isinstance(event_attributes, list):
            hash_data["event_attributes"] = event_attributes

        # get end date
        if post_attr.get("_end_date") is not None:
            end_date = post_attr.get("_end_date")
            if post_attr.get("_end_time") is not None:
                end_date = f"{end_date} {post_attr.get('_end_time')}"
            hash_data["end_date"] = end_date

        # parse event data
        try:
            run = Hash(**hash_data)
        except ValidationError as e:
            e = str(e).replace('\n', ":")
            log.error(f"Event (id: {post.get('id')}) parsing error: {e}")
            #pprint.pprint(post_attr)
            #pprint.pprint(post)
            continue

        # add timezone information to timstamp
        if config.app_settings.timezone_string is not None:
            if isinstance(run.start_date, datetime):
                run.start_date = config.app_settings.timezone_string.localize(run.start_date)

            if isinstance(run.last_update, datetime):
                run.last_update = config.app_settings.timezone_string.localize(run.last_update)

            if isinstance(run.end_date, datetime):
                run.end_date = config.app_settings.timezone_string.localize(run.end_date)

        #print(run.json(indent=4, sort_keys=True))

        if id is not None:
            single_run = run
            break

        return_list.append(run)

    if id is not None:
        return single_run
    else:
        return return_list
