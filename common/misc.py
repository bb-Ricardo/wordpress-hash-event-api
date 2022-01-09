# -*- coding: utf-8 -*-
#  Copyright (c) 2021 Ricardo Bartels. All rights reserved.
#
#  wordpress-hash-event-api
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see file LICENSE.txt included in this
#  repository or visit: <https://opensource.org/licenses/MIT>.

from typing import List, Any
import sys
import re

from phpserialize import loads, dumps

def do_error_exit(log_text: str) -> None:
    """
    log an error and exit with return code 1

    Parameters
    ----------
    log_text : str
        the text to log as error
    """

    print(log_text, file=sys.stderr)
    exit(1)


def format_slug(text: str = None, max_len: int =50) -> str:
        """
        Format string to create slug with max length.

        Parameters
        ----------
        text: str
            name to format into a NetBox slug
        max_len: int
            maximum possible length of slug
        Returns
        -------
        str: input name formatted as slug und truncated if necessary
        """

        if text is None:
            raise AttributeError("Argument 'text' can't be None")

        if len(text) == 0:
            return ""

        permitted_chars = (
            "abcdefghijklmnopqrstuvwxyz"  # alphabet
            "0123456789"  # numbers
            "_-"  # symbols
        )

        # Replace separators with dash
        for sep in [" ", ",", "."]:
            text = text.replace(sep, "-")

        # Strip unacceptable characters
        text = "".join([c for c in text.lower() if c in permitted_chars])

        # Enforce max length
        return text[0:max_len]


def split_quoted_string(string_to_split: str, character_to_split_at: str = ",", strip: bool = False) -> List[str]:
    """
    Split a string but obey quoted parts.

    from: "asdf,asfsdf",sdfds
    to: ['"asdf,asfsdf"', 'sdfds']

    Parameters
    ----------
    string_to_split: str
        string to split in parts
    character_to_split_at: int
        character to split the string at
    strip: bool
        strip each splitted part from white spaces
    Returns
    -------
    list: splitted string parts
    """

    if not isinstance(string_to_split, str):
        return string_to_split

    parts = list()
    for string_part in re.split(rf"{character_to_split_at}(?=(?:[^\"']*[\"'][^\"']*[\"'])*[^\"']*$)", string_to_split):
        if strip is True:
            string_part = string_part.strip()
        parts.append(string_part)

    return parts


def php_deserialize(input: str) -> Any:
    """
    deserialize a php array/object

    Parameters
    ----------
    input: str
        string to deserialize

    Returns
    -------
    any: deserialized object
    """

    if not isinstance(input, str):
        return

    # noinspection PyBroadException
    try:
        return loads(input.encode('utf-8'), charset='utf-8', decode_strings=True)
    except Exception:
        pass

def php_serialize(data: dict) -> str:
    """
    serialize a dict into a php serialized string

    Parameters
    ----------
    data: dict
        object to serialize

    Returns
    -------
    str: serialized string
    """

    if not isinstance(data, dict):
        return

    # noinspection PyBroadException
    try:
        return dumps(data)
    except Exception:
        pass

# EOF
