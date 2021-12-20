from fastapi import APIRouter, HTTPException
from models.run import Hash
from typing import List, Optional
from factory.factory import get_hash_runs

router_runs = APIRouter(
    prefix="/runs",
    tags=["runs"]
)

@router_runs.get("/all", response_model=List[Hash], summary="List of runs", description="Returns all runs")
async def get_runs():

    return get_hash_runs()

@router_runs.get("/{id}", response_model=Hash, summary="Returns a single run")
async def get_run(id: int):
    """
        To view all details related to a single run

        - **id**: The integer id of the run you want to view details.
    """

    run = get_hash_runs(id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return run