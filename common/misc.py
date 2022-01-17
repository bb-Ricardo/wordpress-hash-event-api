# -*- coding: utf-8 -*-
#  Copyright (c) 2022 Ricardo Bartels. All rights reserved.
#
#  wordpress-hash-event-api
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see file LICENSE.txt included in this
#  repository or visit: <https://opensource.org/licenses/MIT>.

from typing import List, Any, Union
import re

from phpserialize import loads, dumps


def format_slug(text: str = None, max_len: int = 50) -> str:
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

    from: "first, string", second string
    to: ['first, string', 'second string']

    Parameters
    ----------
    string_to_split: str
        string to split in parts
    character_to_split_at: int
        character to split the string at
    strip: bool
        strip each part from white spaces
    Returns
    -------
    list: separated string parts
    """

    if not isinstance(string_to_split, str):
        return [string_to_split]

    parts = list()
    for string_part in re.split(rf"{character_to_split_at}(?=(?:[^\"']*[\"'][^\"']*[\"'])*[^\"']*$)", string_to_split):
        if strip is True:
            string_part = string_part.strip()
        parts.append(string_part)

    return parts


def php_deserialize(input_data: str) -> Any:
    """
    deserialize a php array/object

    Parameters
    ----------
    input_data: str
        string to deserialize

    Returns
    -------
    any: deserialized object
    """

    if not isinstance(input_data, str):
        return

    # noinspection PyBroadException
    try:
        return loads(input_data.encode('utf-8'), charset='utf-8', decode_strings=True)
    except Exception:
        pass


def php_serialize(data: dict) -> Union[str, None]:
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

    if isinstance(data, dict):
        # noinspection PyBroadException
        try:
            return dumps(data).decode("utf-8")
        except Exception:
            pass

# EOF
