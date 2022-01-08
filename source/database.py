# -*- coding: utf-8 -*-
#  Copyright (c) 2021 Ricardo Bartels. All rights reserved.
#
#  wordpress-hash-event-api
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see file LICENSE.txt included in this
#  repository or visit: <https://opensource.org/licenses/MIT>.

from datetime import datetime
from typing import Any, Dict, List, AnyStr, Union
import mysql.connector
from common.log import get_logger

log = get_logger()

db_setting_attributes = {
    "db_username": None,
    "db_password": None,
    "db_name": None,
    "db_host": None
}

conn = None


class DBConnection:

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

    def init_session(self) -> None:
        log.debug("Initiating DB session")
        try:
            self.session = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
        except mysql.connector.Error as e:
            log.error(f"DB error occurred: {e}")
            return

        log.debug("Successfully initiated DB connection")

        # disable caching
        self.session.autocommit = True

    def execute_select_query(self, query: str) -> List[Dict]:
        log.debug(f"Performing DB query: {query}")

        if self.session is None or self.session.is_connected() is not True:
            self.init_session()

        try:
            cursor = self.session.cursor(dictionary=True)
            cursor.execute(query)
            rows = cursor.fetchall()
            if rows is not None:
                log.debug(f"DB returned '{len(rows)}' result%s" % ("s" if len(rows) != 1 else ""))
            return rows
        except mysql.connector.Error as e:
            log.error(f"DB error occurred: {e}")

        return list()

    def execute_update_query(self, query: str, content: Any) -> List[Dict]:
        log.debug(f"Performing DB query: {query}")

        if self.session is None or self.session.is_connected() is not True:
            self.init_session()

        try:
            cursor = self.session.cursor()
            cursor.execute(query, (content,))
            self.session.commit()
            log.debug(f"DB updated '{cursor.rowcount}' row%s" % ("s" if cursor.rowcount != 1 else ""))
            return cursor.rowcount
        except mysql.connector.Error as e:
            log.error(f"DB error occurred: {e}")

        return None

    def get_posts(self, post_id: int = None, last_update: datetime = None, compare_type: str = "eq", max: int = None) -> List[Dict]:

        if compare_type not in ["lt", "gt", "eq"]:
            raise ValueError("attribute 'compare_type' must be one of: lt, gt, eq")

        if last_update is not None and not isinstance(last_update, datetime):
            raise ValueError(f"attribute 'last_update' must be of type 'datetime' got: {type(last_update)}")

        query = "SELECT p.id, p.post_content, p.post_title, p.post_modified, p.post_status, p.guid, " \
                "wp_t.name as post_category " \
                "FROM wp_posts as p " \
                "LEFT JOIN wp_term_relationships as t ON p.id = t.object_id " \
                "LEFT JOIN wp_terms as wp_t ON t.term_taxonomy_id = wp_t.term_id " \
                "WHERE p.post_type = 'event_listing'"
        if post_id is not None:
            query += f" AND p.id = {post_id}"

        if last_update is not None:
            compare_string = "="
            if compare_type == "lt":
                compare_string = "<"
            elif compare_type == "gt":
                compare_string = ">"

            query += f" AND p.post_modified_gmt {compare_string} '{last_update}'"

        query += " ORDER BY p.id DESC"

        if isinstance(max, int):
            query += f" LIMIT {max}"

        return self.execute_select_query(query)

    def get_posts_meta(self, post_id: int = None) -> List[Dict]:
        query = "SELECT * FROM `wp_postmeta`"
        if post_id is not None:
            query += f" WHERE post_id = {post_id}"

        return self.execute_select_query(query)

    def get_users(self, user_id: int = None) -> List[Dict]:
        query = "SELECT id, display_name FROM `wp_users`"
        if user_id is not None:
            query += f" WHERE id = {user_id}"

        return self.execute_select_query(query)

    def get_config(self, item: str = None) -> List[Dict]:
        query = "SELECT * from `wp_options`"
        if item is not None:
            query += f" WHERE `option_name` = '{item}'"

        return self.execute_select_query(query)

    def get_config_item(self, item: str = None) -> Union[AnyStr, None]:
        if not isinstance(item, str):
            log.error("get_config_item() Requested config item name must be a string.")
            return

        result = self.get_config(item)
        return_value = None
        if len(result) > 0:
            return_value = result[0].get("option_value")

        return return_value

    def update_config_item(self, item: str, content: Any) -> bool:
        if not isinstance(item, str):
            log.error("update_config_item() Requested config item name must be a string.")
            return False

        query = f'UPDATE `wp_options` SET `option_value`=%s WHERE `wp_options`.`option_name` = "{item}"'

        num_rows = self.execute_update_query(query, content)

        if num_rows is None or num_rows == 0:
            return False

        return True

    def close(self):
        log.debug("Closing DB session")
        if self.session is not None:
            self.session.close()


def get_db_handler() -> Union[DBConnection, None]:
    global conn
    return conn


def setup_db_handler(host_name: str, user_name: str, user_password: str, db_name: str) -> DBConnection:
    global conn
    conn = DBConnection(host_name=host_name, user_name=user_name, user_password=user_password, db_name=db_name)
    return conn

# EOF
