# -*- coding: utf-8 -*-
#  Copyright (c) 2021 Ricardo Bartels. All rights reserved.
#
#  wordpress-hash-event-api
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see file LICENSE.txt included in this
#  repository or visit: <https://opensource.org/licenses/MIT>.

from common.misc import php_deserialize, php_serialize
from source.database import get_db_handler
from common.log import get_logger
from models.run import HashAttributes, HashScope

log = get_logger()

import pprint

def enum_to_options(enum):
    return {e.value: e.name  for e in HashAttributes}

event_manager_fields_config = {
    "_hash_attributes": {
        "label": "Attributes",
        "description": "select run attributes",
        "type": "multiselect",
        "required": False,
        "options": enum_to_options(HashAttributes)

    }
}

print(event_manager_fields_config)

def update_event_manager_fields():
    conn = get_db_handler()

    event_manager_form_fields = php_deserialize(conn.get_config_item("event_manager_form_fields"))
    if event_manager_form_fields is None and not isinstance(event_manager_form_fields, dict):
        log.warning("unable to update Wordpress Event Manager fields, unknown format")
        return
    
    event_fields = event_manager_form_fields.get("event", dict())

    #for 

#    pprint.pprint(php_deserialize())
    #pprint.pprint(php_deserialize())
    #pprint.pprint(php_serialize(php_deserialize(conn.get_config_item("event_manager_submit_event_form_fields"))))


# EOF
