# -*- coding: utf-8 -*-
#  Copyright (c) 2022 Ricardo Bartels. All rights reserved.
#
#  wordpress-hash-event-api
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see file LICENSE.txt included in this
#  repository or visit: <https://opensource.org/licenses/MIT>.

from pydantic.dataclasses import dataclass
from typing import Any, Dict, List
from pydantic import BaseModel


@dataclass
class SendNewsletterParams:
    user: int
    token: str


class MailingListModel(BaseModel):
    id: int
    name: str


class ListmonkReturnData(BaseModel):
    id: int
    created_at: str
    updated_at: str
    views: int
    clicks: int
    bounces: int
    lists: List[MailingListModel]
    started_at: Any
    to_send: int
    sent: int
    uuid: str
    type: str
    name: str
    subject: str
    from_email: str
    body: str
    altbody: Any
    send_at: Any
    status: str
    content_type: str
    tags: List
    headers: List
    template_id: int
    messenger: str
    archive: bool
    archive_template_id: int
    archive_meta: Dict[str, Any]


class ListmonkReturnDataList(BaseModel):
    data: ListmonkReturnData
