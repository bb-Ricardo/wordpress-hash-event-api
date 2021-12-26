#!/usr/bin/env python3.9
#  Copyright (c) 2021 Ricardo Bartels. All rights reserved.
#
#  wordpress-hash-event-api
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see file LICENSE.txt included in this
#  repository or visit: <https://opensource.org/licenses/MIT>.

from logging.config import dictConfig

from fastapi import FastAPI
from starlette.responses import RedirectResponse
from pydantic import BaseSettings, ValidationError

from source.database import setup_db_handler, db_setting_attributes
import common.config as config
from common.log import setup_logging
from source.manage_evnet_fields import update_event_manager_fields
from routers import runs
from config.log import request_logger_config

settings_file = "config.ini"
default_log_level = "INFO"
log = None


class APISettings(BaseSettings):
    description = 'Hash Run API for wordpress Event Manager'
    title = 'Kennel Runs API'
    openapi_url = "/openapi.json"
    root_path = "/"
    version = '0.1'
    debug = False


def get_app() -> FastAPI:

    global log

    api_settings = APISettings()

    # get config file path
    config_file = config.get_config_file(settings_file)

    # get config handler
    config_handler = config.open_config_file(config_file)

    # set log level
    log_level = default_log_level
    
    # config overwrites default
    log_level = config_handler.get("main", "log_level", fallback=log_level)

    # setup logging
    log = setup_logging(log_level)

    log.info(f"Starting {api_settings.description} v{api_settings.version}")

    if log_level == "DEBUG":
        api_settings.debug = True

    # configure request logger
    request_logger_config["loggers"]["uvicorn.access"]["level"] = log_level
    dictConfig(request_logger_config)

    db_settings = config.get_config(config_handler, section="database", valid_settings=db_setting_attributes)

    conn = setup_db_handler(
        host_name=db_settings.get("db_host"),
        user_name=db_settings.get("db_username"),
        user_password=db_settings.get("db_password"),
        db_name=db_settings.get("db_name")
    )

    if conn is not None and conn.session is not None:
        log.info("Database connection successfully started")
    else:
        log.error("Exit due to database connection error")
        exit(1)

    api_config = config.get_config(config_handler, section="main", valid_settings=config.main_config_values)

    if api_config.get("api_root_path") is not None:
        api_settings.root_path = api_config.get("api_root_path")

    # check installed Event Manager version
    installed_event_manager_version = conn.get_config_item("wp_event_manager_version")
    if installed_event_manager_version is None:
        log.error("Wordpress event manager plugin not installed")
        exit(1)
    else:
        log.debug(f"Installed Wordpress Event Manager version: {installed_event_manager_version}")
        fersion_supported = False
        # try to compare versions
        try:
            version_split = installed_event_manager_version.split(".")
            if int(version_split[0]) == 3 and int(version_split[1]) >= 1 and int(version_split[2]) >= 21:
                fersion_supported = True
        except Exception:
            pass

        if fersion_supported is False:
            log.error(f"Wordpress Event Manager version '{installed_event_manager_version}' unsupported. "
                       "Minimal version needed '3.1.21'. Please update plugin.")
            exit(1)

    # read app settings from config and try to find settings in wordpress db if not defined in config
    app_settings_config = config.get_config(
        config_handler, section="app_config", valid_settings=config.app_settings.dict())

    # try to find further settings in DB if undefined
    for key, value in app_settings_config.items():
        if value is None:
            db_setting = conn.get_config_item(key)
            if db_setting is not None:
                log.debug(f"Config: updating app_config.{key} = {db_setting}")
                value = db_setting

        app_settings_config[key] = value

    # update time zone if defined in event manager
    event_manager_timezone_setting = conn.get_config_item("event_manager_timezone_setting")
    if event_manager_timezone_setting is not None and event_manager_timezone_setting != "site_timezone":
        log.debug(f"Config: updating app_config.timezone_string = {event_manager_timezone_setting}")
        app_settings_config["timezone_string"] = event_manager_timezone_setting

    # parse settings
    try:
        config.app_settings = config.AppSettings(**app_settings_config)
    except ValidationError as e:
        e = str(e).replace('\n', ":")
        log.error(f"Unable to parse config: {e}")
        exit(1)

    # create FastAPI instance
    server = FastAPI(**api_settings.dict())

    # add default route redirect to docs
    @server.get("/", include_in_schema=False)
    def redirect_to_docs() -> RedirectResponse:
        return RedirectResponse(f"{api_settings.root_path}/docs")

    @server.get("/status", include_in_schema=False)
    def status():
        return {"status": "ok"}

    # close DB connection on shutdown
    @server.on_event("shutdown")
    async def shutdown():
        if conn is not None:
            conn.close()

    # update event manager fields in database
    update_event_manager_fields()

    # add runs routes
    server.include_router(runs.router_runs)

    return server


app = get_app()

# EOF
