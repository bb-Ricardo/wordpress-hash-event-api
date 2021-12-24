# -*- coding: utf-8 -*-
#  Copyright (c) 2021 Ricardo Bartels. All rights reserved.
#
#  wordpress-hash-event-api
#
#  This work is licensed under the terms of the MIT license.
#  For a copy, see file LICENSE.txt included in this
#  repository or visit: <https://opensource.org/licenses/MIT>.

from typing import List

from fastapi import APIRouter, HTTPException

from models.run import Hash
from factory.factory import get_hash_runs

router_runs = APIRouter(
    prefix="/runs",
    tags=["runs"]
)


@router_runs.get("/all", response_model=List[Hash], summary="List of runs", description="Returns all Hash runs")
async def get_runs():
    return get_hash_runs()


@router_runs.get("/{id}", response_model=Hash, summary="Returns a single Hash run")
async def get_run(run_id: int):
    """
        To view all details related to a single run

        - **id**: The integer id of the run you want to view details.
    """

    run = get_hash_runs(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return run

# EOF
