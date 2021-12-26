# -*- coding: utf-8 -*-
#  Copyright (c) 2021 Ricardo Bartels. All rights reserved.
#
#  wordpress-hash-event-api
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see file LICENSE.txt included in this
#  repository or visit: <https://opensource.org/licenses/MIT>.

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import ValidationError

from models.run import Hash, HashParams
from models.result import MultiResponse
from factory.factory import get_hash_runs

router_runs = APIRouter(
    prefix="/runs",
    tags=["runs"]
)


@router_runs.get("/all", response_model=List[Hash], summary="List of runs", description="Returns all Hash runs")
async def get_runs(params: HashParams = Depends(HashParams)):

    result, error = get_hash_runs(params)
    if error is not None:
        raise HTTPException(status_code=400, detail=error)

    return result


# noinspection PyShadowingBuiltins
@router_runs.get("/{id}", response_model=Hash, summary="Returns a single Hash run")
async def get_run(id: int):
    """
        To view all details related to a single run

        - **id**: The integer id of the run you want to view details.
    """

    result, error = get_hash_runs(HashParams(id=id))

    if error is not None:
        raise HTTPException(status_code=400, detail=error)
    if result is None or len(result) == 0:
        raise HTTPException(status_code=404, detail="Run not found")

    return result[0]

# EOF
