#!/usr/bin/env python3.9
#  Copyright (c) 2021 Ricardo Bartels. All rights reserved.
#
#  wordpress-hash-event-api
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see file LICENSE.txt included in this
#  repository or visit: <https://opensource.org/licenses/MIT>.

from logging.config import dictConfig as logDictConfig
import os

from fastapi import FastAPI
from starlette.responses import RedirectResponse

from config.models.api import APIConfigSettings
from config.models.app import AppSettings
from config.models.database import DBSettings
from config.models.main import MainConfigSettings
from config.log import default_log_level, request_logger_config
from config.api import BasicAPISettings
import config
from api.security import api_key_valid, set_api_key
from api.routers import runs
from source.database import setup_db_handler
from source.manage_event_fields import update_event_manager_fields
from common.log import setup_logging

settings_file = "config.ini"
log = None


def get_app() -> FastAPI:

    global log

    basic_api_settings = BasicAPISettings()

    # get config file path
    config_file = config.get_config_file(settings_file)

    log_level = default_log_level

    # get config handler
    config_handler = None
    if os.path.exists(config_file):

        config_handler = config.open_config_file(config_file)
    
        # config overwrites default
        if config_handler is not None:
            log_level = config_handler.get(MainConfigSettings.config_section_name(), "log_level", fallback=log_level)

    # env overwrites config value
    log_level = MainConfigSettings(log_level=log_level).log_level

    # setup logging
    log = setup_logging(log_level)

    log.info(f"Starting {basic_api_settings.description} v{basic_api_settings.version}")

    if not os.path.exists(config_file):
        log.warning(f"Config file '{config_file}' not found. Reading config from env vars")
    elif config_handler is None:
        log.warning(f"Problems while reading config file. Reading config from env vars")

    if log_level == "DEBUG":
        basic_api_settings.debug = True

    # configure request logger
    request_logger_config["loggers"]["uvicorn.access"]["level"] = log_level
    logDictConfig(request_logger_config)

    # parse settings for db and initialize db connection
    db_settings = config.get_config_object(config_handler, DBSettings)
    conn = setup_db_handler(
        host_name=db_settings.host,
        user_name=db_settings.username,
        user_password=db_settings.password,
        db_name=db_settings.name,
        db_port=db_settings.port
    )

    if conn is None or conn.session is None:
        log.error("Exit due to database connection error")
        exit(1)

    log.info("Database connection successfully started")

    # read app settings from config and try to find settings in wordpress db if not defined in config
    app_settings = config.get_config_object(config_handler, AppSettings)

    # try to find further settings in DB if undefined
    for key, value in app_settings:
        if value is None:
            db_setting = conn.get_config_item(key)
            if db_setting is not None:
                log.debug(f"Config: updating {AppSettings.config_section_name()}.{key} = {db_setting}")
                value = db_setting

        setattr(app_settings, key, value)

    # parse settings
    config.app_settings = config.validate_config_object(AppSettings, app_settings.dict())

    # update event manager fields in database
    update_event_manager_fields()

    # initialize FastAPI app
    # parse api settings from config
    api_settings = config.get_config_object(config_handler, APIConfigSettings)
    if api_settings.root_path is not None:
        basic_api_settings.root_path = api_settings.root_path

    # set api key if defined
    set_api_key(api_settings.token)

    # create FastAPI instance
    server = FastAPI(**basic_api_settings.dict())

    # close DB connection on shutdown
    @server.on_event("shutdown")
    async def shutdown():
        if conn is not None:
            conn.close()

    # disable API authorization if no token is defined
    if api_settings.token is None:
        log.info("No API token defined, disabling API Authentication")
        server.dependency_overrides[api_key_valid] = lambda: None

    # add default route redirect to docs
    @server.get("/", include_in_schema=False)
    def redirect_to_docs() -> RedirectResponse:
        return RedirectResponse(f"{basic_api_settings.root_path}/docs")

    @server.get("/status", include_in_schema=False)
    def status():
        return {"status": "ok"}

    # add runs routes
    server.include_router(runs.router_runs)

    return server


app = get_app()

# EOF
