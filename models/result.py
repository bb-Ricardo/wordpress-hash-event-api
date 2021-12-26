# -*- coding: utf-8 -*-
#  Copyright (c) 2021 Ricardo Bartels. All rights reserved.
#
#  wordpress-hash-event-api
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see file LICENSE.txt included in this
#  repository or visit: <https://opensource.org/licenses/MIT>.

from typing import List

from pydantic import BaseModel

from models.run import Hash


class MultiResponse(BaseModel):
    count: int = 0
    results: List[Hash] = list()

# EOF
