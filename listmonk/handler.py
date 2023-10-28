# -*- coding: utf-8 -*-
#  Copyright (c) 2022 Ricardo Bartels. All rights reserved.
#
#  wordpress-hash-event-api
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see file LICENSE.txt included in this
#  repository or visit: <https://opensource.org/licenses/MIT>.

import json
from requests import session, Request
from requests.exceptions import ConnectionError, ReadTimeout, JSONDecodeError as RequestsJSONDecodeError
from typing import Union

from config.api import BasicAPISettings
from common.log import get_logger
from common.misc import grab
from config.models.listmonk import ListMonkSettings

log = get_logger()

conn = None


class ListMonkHandler:

    def __init__(self, config: ListMonkSettings):

        global conn

        self.config = config
        self.session = None

        self.url = f"https://{self.config.host}/api/"

        self.init_session()
        if self.get_api_version() is False:
            log.error("Listmonk connection failed")
            self.finish()

        conn = self

    def init_session(self):

        header = {
            "User-Agent": f"wordpress-hash-event-api/{BasicAPISettings().version}",
            "Content-Type": "application/json"
        }

        self.session = session()
        self.session.auth = (self.config.username, self.config.password)
        self.session.headers.update(header)

    def finish(self):

        # closing Listmonk connection
        try:
            self.session.close()
        except Exception as e:
            log.error(f"unable to close Listmonk connection: {e}")

    def get_api_version(self):
        """
        Perform a /api/config GET request to retrieve Listmonk API version

        Returns
        -------
        bool: True if request was successful
        """

        log.debug("Initializing Listmonk connection")

        response = None
        try:
            response = self.request("config")
        except Exception as e:
            log.warning(f"Listmonk connection failed: {e}")

        if response is None:
            return False

        listmonk_version = grab(response, 'data.version')

        if listmonk_version is None:
            return False

        log.info(f"Successfully connected to Listmonk '{self.url}'")
        log.debug(f"Detected Listmonk API version: {listmonk_version}")

        return True

    def request(self, endpoint, req_type="GET", data=None, params=None):
        """
        Perform a Listmonk request for a certain endpoint.

        Parameters
        ----------
        endpoint: str
            ListmonkObject endpoint below "/api/
        req_type: str
            GET, PATCH, PUT, DELETE
        data: dict
            data which shall be send to Listmonk
        params: dict
            dict of URL params which should be passed to Listmonk

        Returns
        -------
        (dict, bool, None): of returned Listmonk data. If object was requested to be deleted and it was
                            successful then True will be returned. None if request failed or was empty
        """

        result = None

        request_url = f"{self.url}{endpoint.lstrip('/')}"

        if params is not None and not isinstance(params, dict):
            log.debug(f"Params passed to Listmonk request need to be a dict, got: {params}")
            params = dict()

        if req_type == "GET":

            if params is None:
                params = dict()

        # prepare request
        this_request = self.session.prepare_request(
                            Request(req_type, request_url, params=params, json=data)
                       )

        # issue request
        try:
            response = self.session.send(this_request, timeout=5)
        except (ConnectionError, ReadTimeout) as e:
            log.error(f"Request failed, trying again: {e}")
            return

        log.debug("Received HTTP Status %s.", response.status_code)

        try:
            result = response.json()
        except (json.decoder.JSONDecodeError, RequestsJSONDecodeError) as e:
            pass

        # token issues
        if response.status_code == 403:

            log.error("Listmonk returned: %s: %s" % (response.reason, grab(result, "detail")))
            result = None

        # we screw up something else
        elif 400 <= response.status_code < 500:

            log.error(f"Listmonk returned: {this_request.method} {this_request.path_url} {response.reason}")
            log.error(f"Listmonk returned body: {result}")
            result = None

        elif response.status_code >= 500:

            log.error(f"Listmonk returned: {response.status_code} {response.reason}")
            result = None

        return result

    def get_template(self, template_id: int):

        return self.request(f"/templates/{template_id}")

    def add_campaign(self, data: dict):
        return self.request(f"/campaigns", "POST", data=data)

    def set_campaign_status(self, campaign_id: int, status: str):
        return self.request(f"/campaigns/{campaign_id}/status", "PUT", data={"status": status})


def get_listmonk_handler() -> Union[ListMonkHandler, None]:
    global conn
    return conn
