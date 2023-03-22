# -*- coding: utf-8 -*-
#  Copyright (c) 2022 Ricardo Bartels. All rights reserved.
#
#  wordpress-hash-event-api
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see file LICENSE.txt included in this
#  repository or visit: <https://opensource.org/licenses/MIT>.

from datetime import datetime
from typing import Any, Dict, List, AnyStr, Union
# noinspection PyPackageRequirements
import mysql.connector
from common.log import get_logger

log = get_logger()
conn = None


class DBConnection:

    session = None
    host = None
    user = None
    password = None
    database = None
    port = None

    connection_timeout = 2

    def __init__(self, host_name: str, user_name: str, user_password: str, db_name: str, db_port: int = 3306) -> None:
        self.host = host_name
        self.user = user_name
        self.password = user_password
        self.database = db_name
        self.port = db_port

        if self.session is None:
            self.init_session()

    def init_session(self) -> None:
        log.debug("Initiating DB session")
        try:
            self.session = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                connection_timeout=self.connection_timeout
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

    def execute_insert_query(self, query: str) -> List[Dict]:
        log.debug(f"Performing DB query: {query}")

        if self.session is None or self.session.is_connected() is not True:
            self.init_session()

        try:
            cursor = self.session.cursor(dictionary=True)
            cursor.execute(query)
            self.session.commit()
        except mysql.connector.Error as e:
            self.session.rollback()
            log.error(f"DB error occurred: {e}")

        return list()

    def execute_update_query(self, query: str, content: Any) -> int:
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

        return 0

    def get_posts(
            self, post_id: int = None, last_update: datetime = None,
            compare_type: str = "eq", limit: int = None) -> List[Dict]:

        if compare_type not in ["lt", "gt", "eq"]:
            raise ValueError("attribute 'compare_type' must be one of: lt, gt, eq")

        if last_update is not None and not isinstance(last_update, datetime):
            raise ValueError(f"attribute 'last_update' must be of type 'datetime' got: {type(last_update)}")

        wordpress_post_type = "event_listing"
        wordpress_taxonomy_type = "event_listing_type"
        query = f"""
                SELECT p.id, p.post_content, p.post_title, p.post_modified, p.post_status, p.guid, event_type.name as post_type
                FROM wp_posts as p
                LEFT JOIN (
                    SELECT t.object_id, wp_t.name
                    FROM  wp_term_relationships as t
                    LEFT JOIN wp_terms as wp_t ON t.term_taxonomy_id = wp_t.term_id
                    LEFT OUTER JOIN wp_term_taxonomy as wp_tax ON t.term_taxonomy_id = wp_tax.term_taxonomy_id
                    WHERE wp_tax.taxonomy = '{wordpress_taxonomy_type}'
                ) event_type ON event_type.object_id = p.id WHERE p.post_type = '{wordpress_post_type}'
                """

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

        if isinstance(limit, int):
            query += f" LIMIT {limit}"

        return self.execute_select_query(query)

    def get_posts_meta(self, post_ids: List[int] = None) -> List[Dict]:
        query = "SELECT * FROM `wp_postmeta`"
        if isinstance(post_ids, list):
            query += f" WHERE `post_id` IN ({','.join(map(str, post_ids))})"

        return self.execute_select_query(query)

    def add_post_meta(self, post_id, meta_key, meta_value):
        query = "INSERT INTO `wp_postmeta` " \
                        "( `post_id`,   `meta_key`,   `meta_value`) " \
                f"VALUES ('{post_id}', '{meta_key}', '{meta_value}')"

        return self.execute_insert_query(query)

    def update_post_meta(self, post_id, meta_key, meta_value):
        query = "UPDATE `wp_postmeta` SET `meta_value`=%s WHERE " \
                f"`wp_postmeta`.`post_id` = '{post_id}' AND `wp_postmeta`.`meta_key` = '{meta_key}'"

        return self.execute_update_query(query, meta_value)

    def get_users(self, user_id: int = None) -> List[Dict]:
        query = "SELECT id, display_name FROM `wp_users`"
        if user_id is not None:
            query += f" WHERE `id` = {user_id}"

        return self.execute_select_query(query)

    def get_usermeta(self, user_id: int = None) -> List[Dict]:
        query = "SELECT * FROM `wp_usermeta`"
        if user_id is not None:
            query += f" WHERE `user_id` = {user_id}"

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


def setup_db_handler(
        host_name: str, user_name: str, user_password: str, db_name: str, db_port: int = 3306
) -> DBConnection:
    global conn
    conn = DBConnection(
        host_name=host_name, user_name=user_name, user_password=user_password, db_name=db_name, db_port=db_port)
    return conn

# EOF
