# -*- coding: utf-8 -*-
#  Copyright (c) 2022 Ricardo Bartels. All rights reserved.
#
#  wordpress-hash-event-api
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see file LICENSE.txt included in this
#  repository or visit: <https://opensource.org/licenses/MIT>.

from common.misc import php_deserialize, php_serialize, format_slug
from source.database import get_db_handler
from common.log import get_logger
import config
from api.models.run import HashAttributes, HashScope

log = get_logger()


class HashEventManagerData:

    filed_data = None
    default_field_updates = None

    def __init__(self):

        self.filed_data = {
            "hash_attributes": {
                "label": "Attributes",
                "description": "select run attributes",
                "type": "multiselect",
                "required": False,
                "options": {e.value: e.name for e in HashAttributes}
            },
            "hash_scope": {
                "label": "Event Promotion",
                "description": "Select a scope fot this run/event",
                "type": "select",
                "required": False,
                "options": {e.value: e.name for e in HashScope}
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
            "hash_cash_non_members": {
                "label": "Hash Cash Non Members",
                "description": 'Amount of Hash Cash which are visiting or not members of this kennel',
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
            "hash_location_specifics": {
                "label": "Location Specifics",
                "description": "additional description to find the location/event",
                "required": False,
                "type": "text"
            },
            "hash_cash_extras": {
                "label": "Hash Cash Extras",
                "description": "additional Hash Cash amount for specials (food/drinks)",
                "required": False,
                "type": "number"
            },
            "hash_extras_description": {
                "label": "Hash Cash Extras Description",
                "description": "What will other Hashers be provided for the extra buck",
                "required": False,
                "type": "text"
            },
            "hash_event_hidden": {
                "label": "Event Hidden",
                "description": "Hide event from exposure on consumer site (Harrier Central)",
                "required": False,
                "type": "checkbox"
            }
        }

        self.default_field_updates = {
            "event_end_date": {
                "visibility": 1,
                "required": "0",
            },
            "event_end_time": {
                "visibility": 1,
                "required": "0",
            },
            "hash_attributes": {
                "options": self.filed_data.get("hash_attributes").get("options")
            },
            "hash_scope": {
                "options": self.filed_data.get("hash_scope").get("options")
            },
            "hash_cash": {
                "placeholder": self.filed_data.get("hash_cash").get("placeholder")
            },
            "hash_kennel": {
                "options": self.filed_data.get("hash_kennel").get("options"),
                "default": self.filed_data.get("hash_kennel").get("default")
            }
        }


def check_event_manager_version():

    conn = get_db_handler()

    supported_version = "3.1.21"

    # check installed Event Manager version
    installed_event_manager_version = conn.get_config_item("wp_event_manager_version")

    if installed_event_manager_version is None:
        log.error("Wordpress event manager plugin not installed")
        exit(1)
    else:
        log.info(f"Installed Wordpress Event Manager version: {installed_event_manager_version}")
        version_supported = False
        # try to compare versions
        # noinspection PyBroadException
        try:
            version_split = installed_event_manager_version.split(".")
            supported_version_split = supported_version.split(".")
            if int(version_split[0]) == int(supported_version_split[0]) and \
                    int(version_split[1]) >= int(supported_version_split[1]) and \
                    int(version_split[2]) >= int(supported_version_split[2]):
                version_supported = True
        except Exception:
            pass

        if version_supported is False:
            log.error(f"Wordpress Event Manager version '{installed_event_manager_version}' unsupported. "
                      f"Minimal version needed '{supported_version}'. Please update plugin.")
            exit(1)


def update_event_manager_fields():

    check_event_manager_version()

    conn = get_db_handler()

    event_manager_form_fields = php_deserialize(conn.get_config_item("event_manager_form_fields"))
    if event_manager_form_fields is None or not isinstance(event_manager_form_fields, dict):
        log.warning("unable to update Wordpress Event Manager fields, unknown format")
        return False

    event_fields = event_manager_form_fields.get("event", dict())

    # initialize data to add
    event_manager_patch_data = HashEventManagerData()

    current_field_priority = max([x.get("priority", 0) for x in event_fields.values()])

    update_data = False

    # Add new fields
    for key, attributes in event_manager_patch_data.filed_data.items():

        if event_fields.get(key) is None:

            event_fields[key] = attributes
            event_fields[key]["priority"] = current_field_priority
            current_field_priority += 1
            update_data = True
            log.info(f"Added new field '{key}' to Event Manager")
    
    # check for changed fields
    for key, attributes in event_manager_patch_data.default_field_updates.items():

        for a_key, a_value in attributes.items():

            if str(event_fields[key].get(a_key)) != str(a_value):
                event_fields[key][a_key] = a_value
                update_data = True
                log.info(f"Updated Event Manager field '{key}' attribute '{a_key}' to '{a_value}'")

    if update_data is False:
        return True

    # update attribute data
    event_manager_form_fields["event"] = event_fields

    # update database
    updated_rows = conn.update_config_item("event_manager_form_fields", php_serialize(event_manager_form_fields))

    if updated_rows == 0:
        log.error("Updating Wordpress option 'event_manager_form_fields' failed.")
        return False

    log.info("Successfully updated Wordpress option 'event_manager_form_fields'")

    updated_rows = conn.update_config_item("event_manager_submit_event_form_fields",
                                           php_serialize({"event": event_fields}))

    if updated_rows == 0:
        log.error("Updating Wordpress option 'event_manager_submit_event_form_fields' failed.")
        return False

    log.info("Successfully updated Wordpress option 'event_manager_submit_event_form_fields'")

    return True

# EOF
