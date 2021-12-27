# -*- coding: utf-8 -*-
#  Copyright (c) 2021 Ricardo Bartels. All rights reserved.
#
#  wordpress-hash-event-api
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see file LICENSE.txt included in this
#  repository or visit: <https://opensource.org/licenses/MIT>.

from common.misc import php_deserialize, php_serialize, format_slug
from source.database import get_db_handler
from common.log import get_logger
import common.config as config
from models.run import HashAttributes, HashScope


log = get_logger()

import pprint

# define event manager fields visible for a run/event
# all fields should be prefixed with "hash_"
# ToDo:
#   * transform to class
#   * add attributes to always update
#       * select and multiselect attributes
#       * event_and_date and event_end_time

def get_hash_event_manager_fields():
    return {
        "hash_attributes": {
            "label": "Attributes",
            "description": "select run attributes",
            "type": "multiselect",
            "required": False,
            "options": {e.value: e.name  for e in HashAttributes}
        },
        "hash_scope": {
            "label": "Event Promotion",
            "description": "Select a scope fot this run/event",
            "type": "select",
            "required": False,
            "options": {e.value: e.name  for e in HashScope}
        },
        "hash_run_number": {
            "label": "Run Number",
            "description": "The number of the run",
            "placeholder": "123",
            "type": "number",
            "required": False
        },
        "hash_contact": {
            "label": "Contact",
            "description": "eMail or phone number",
            "required": False,
            "type": "text"
        },
        "hash_hares": {
            "label": "Hares",
            "description": "Name of the Hares",
            "required": False,
            "type": "text"
        },
        "hash_cash": {
            "label": "Hash Cash",
            "description": 'Amount of Hash Cash',
            "placeholder": config.app_settings.default_hash_cash or "",
            "type": "number",
            "required": False
        },
        "hash_kennel": {
            "label": "Kennel",
            "description": "pick a Kennel",
            "type": "select",
            "required": False,
            "options": {format_slug(x): x for x in config.app_settings.hash_kennels},
            "default": format_slug(config.app_settings.default_kennel or "")
        },
#        "hash_location_specifics"
    }



def update_event_manager_fields():
    conn = get_db_handler()

    event_manager_form_fields = php_deserialize(conn.get_config_item("event_manager_form_fields"))
    if event_manager_form_fields is None and not isinstance(event_manager_form_fields, dict):
        log.warning("unable to update Wordpress Event Manager fields, unknown format")
        return
    
    event_fields = event_manager_form_fields.get("event", dict())

#    pprint.pprint(event_fields)
    print("x"*40)
    hash_fields = get_hash_event_manager_fields()
    print(php_serialize({**event_fields, **hash_fields}).decode("utf-8"))
#    for

#    pprint.pprint(php_deserialize())
    #pprint.pprint(php_deserialize())
    #pprint.pprint(php_serialize(php_deserialize(conn.get_config_item("event_manager_submit_event_form_fields"))))


# EOF
