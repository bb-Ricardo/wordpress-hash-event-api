# -*- coding: utf-8 -*-
#  Copyright (c) 2021 Ricardo Bartels. All rights reserved.
#
#  wordpress-hash-event-api
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see file LICENSE.txt included in this
#  repository or visit: <https://opensource.org/licenses/MIT>.

from typing import Dict, List
import mysql.connector
from common.logging import get_logger

log = get_logger()

db_setting_attributes = {
    "db_username": None,
    "db_password": None,
    "db_name": None,
    "db_host": None
}

conn = None


class DBConnection():

    session = None
    host = None
    user = None
    password = None
    database = None

    def __init__(self, host_name: str, user_name: str, user_password: str, db_name: str) -> None:
        self.host = host_name
        self.user = user_name
        self.password = user_password
        self.database = db_name

        if self.session is None:
            self.init_session()

    def init_session(self):
        log.debug("Intiating DB session")
        try:
            self.session = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
        except mysql.connector.Error as e:
            log.error(f"DB error occured: {e}")
            return

        log.debug("Successfully initiated DB connection")

        # disable caching
        self.session.autocommit = True

    def execute_query(self, query):
        log.debug(f"Performing DB query: {query}")

        if self.session is None or self.session.is_connected() is not True:
            self.init_session()

        try:
            cursor = self.session.cursor(dictionary=True)
            cursor.execute(query)
            return cursor.fetchall()
        except mysql.connector.Error as e:
            log.error(f"DB error occured: {e}")

    def get_posts(self, post_id: int = None) -> List[Dict]:
        query = "SELECT p.id, p.post_content, p.post_title, p.post_modified, p.post_status, p.guid, " \
                "wp_t.name as post_category " \
                "FROM wp_posts as p " \
                "LEFT JOIN wp_term_relationships as t ON p.id = t.object_id " \
                "LEFT JOIN wp_terms as wp_t ON t.term_taxonomy_id = wp_t.term_id " \
                "WHERE p.post_type = 'event_listing'"
        if post_id is not None:
            query += f" AND p.id = {post_id}"
        return self.execute_query(query)

    def get_posts_meta(self, post_id: int = None) -> List[Dict]:
        query = "SELECT * FROM `wp_postmeta`"
        if post_id is not None:
            query += f" WHERE post_id = {post_id}"

        return self.execute_query(query)

    def get_users(self, user_id: int = None) -> List[Dict]:
        query = "SELECT id, display_name FROM `wp_users`"
        if user_id is not None:
            query += f" WHERE id = {user_id}"

        return self.execute_query(query)

    def get_config(self, item: str = None):
        query = "SELECT * from `wp_options`"
        if item is not None:
            query += f" WHERE `option_name` = '{item}'"
        return self.execute_query(query)

    def get_config_item(self, item: str = None):
        if item is None:
            log.error("get_config_item() Requested config item name must be a string.")
            return

        result = self.get_config(item) or list()
        return_value = None
        if len(result) > 0:
            return_value = result[0].get("option_value")

        return return_value

    def close(self):
        log.debug("Closing DB session")
        if self.session is not None:
            self.session.close()


def get_db_handler() -> DBConnection:
    global conn
    return conn


def setup_db_handler(host_name: str, user_name: str, user_password: str, db_name: str) -> DBConnection:
    global conn
    conn = DBConnection(host_name=host_name, user_name=user_name, user_password=user_password, db_name=db_name)
    return conn

# EOF
