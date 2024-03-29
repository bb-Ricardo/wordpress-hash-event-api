# -*- coding: utf-8 -*-
#  Copyright (c) 2022 Ricardo Bartels. All rights reserved.
#
#  wordpress-hash-event-api
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see file LICENSE.txt included in this
#  repository or visit: <https://opensource.org/licenses/MIT>.

import configparser
import os

from pydantic import ValidationError

from config.models.app import AppSettings
from config.models.calendar import CalendarConfigSettings
from common.log import get_logger

logger = get_logger()


app_settings = AppSettings(hash_kennels="EMPTY")
calendar_settings = CalendarConfigSettings()


def validate_config_object(config_class, settings):

    settings_object = None
    try:
        settings_object = config_class(**settings)
    except ValidationError as e:
        e = str(e).replace('\n', ": ")
        logger.error(f"Unable to parse config (also check defined env vars): {e}")
        exit(1)

    return settings_object


def get_config_object(handler, config_class):

    config_section = config_class.config_section_name()

    # read db settings from config file
    settings_dict = dict()
    if handler is not None:
        settings_dict = get_config(handler, section=config_section, valid_settings=config_class.defaults_dict())

    settings_object = validate_config_object(config_class, settings_dict)

    for item, value in settings_object:
        # take care of logging sensitive data
        for sensitive_item in ["token", "pass"]:

            if sensitive_item.lower() in item.lower() and isinstance(value, str):
                value = value[0:3] + "***"

        logger.debug(f"Config: {config_section}.{item} = {value}")

    return settings_object


def get_config_file(config_file):
    """
    get absolute path to provided config file string

    Parameters
    ----------
    config_file: str
        config file path

    Returns
    -------
    str: absolute path to config file
    """

    if config_file is None or config_file == "":
        raise Exception("ERROR: Config file not defined.")

    base_dir = os.sep.join(__file__.split(os.sep)[0:-2])
    if config_file[0] != os.sep:
        config_file = f"{base_dir}{os.sep}{config_file}"

    return os.path.realpath(config_file)


def open_config_file(config_file):
    """
    Open config file with a ConfigParser and return handler. Bail out of opening or parsing fails

    Parameters
    ----------
    config_file: str
        absolute path of config file to open

    Returns
    -------
    ConfigParser: handler with supplied config file
    """

    if config_file is None or config_file == "":
        raise Exception("ERROR: Config file not defined.")

    # setup config parser and read config
    config_handler = configparser.ConfigParser(strict=True, allow_no_value=True, empty_lines_in_values=False)

    # noinspection PyBroadException
    try:
        config_handler.read_file(open(config_file))
    except (configparser.Error, AttributeError) as e:
        logger.warning(f"Problem while config file '{config_file}' parsing: {e}")
        return
    except Exception:
        logger.warning(f"Unable to open file '{config_file}'")
        return

    return config_handler


def get_config(config_handler=None, section=None, valid_settings=None, deprecated_settings=None, removed_settings=None):
    """
    read config items from a defined section

    Parameters
    ----------
    config_handler: ConfigParser
        a config file handler to read config data from
    section: str
        name of the section to read
    valid_settings: dict
        a dictionary with valid config items to read from this section.
        key: is the config item name
        value: default value if config option is undefined
    deprecated_settings: dict
        a dictionary of deprecated config settings
        key: name of deprecated setting
        value: name of superseding setting or None if no substitution applies
    removed_settings: dict
        a dictionary of removed setting names
        key: name of removed setting
        value: name of superseding setting or None if no substitution applies

    Returns
    -------
    dict:   parsed config items from defined $section

    """

    def get_config_option(this_section, item, default=None):

        if isinstance(default, bool):
            value = config_handler.getboolean(this_section, item, fallback=default)
        elif isinstance(default, int):
            value = config_handler.getint(this_section, item, fallback=default)
        else:
            value = config_handler.get(this_section, item, fallback=default)

        if value == "":
            value = None

        config_dict[item] = value

    config_dict = {}

    if valid_settings is None:
        logger.error("No valid settings passed to config parser!")

    # read specified section section
    if section is None:
        return config_dict

    if section not in config_handler.sections():
        logger.error(f"Section '{section}' not found in config_file")
        return config_dict

    for config_item, default_value in valid_settings.items():
        get_config_option(section, config_item, default=default_value)

    # check for deprecated settings
    if isinstance(deprecated_settings, dict):
        for deprecated_setting, alternative_setting in deprecated_settings.items():
            if config_handler.get(section, deprecated_setting, fallback=None) is not None:
                log_text = f"Setting '{deprecated_setting}' is deprecated and will be removed soon."
                if alternative_setting is not None:
                    log_text += f" Consider changing your config to use the '{alternative_setting}' setting."
                logger.warning(log_text)

    # check for removed settings
    if isinstance(removed_settings, dict):
        for removed_setting, alternative_setting in removed_settings.items():
            if config_handler.get(section, removed_setting, fallback=None) is not None:
                log_text = f"Setting '{removed_setting}' has been removed " \
                           f"but is still defined in config section '{section}'."
                if alternative_setting is not None:
                    log_text += f" You need to switch to '{alternative_setting}' setting."
                logger.warning(log_text)

    return config_dict

# EOF
