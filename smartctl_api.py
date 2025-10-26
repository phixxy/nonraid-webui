# smartctl python api
from fastapi import APIRouter, HTTPException
from utils import run_cmd, CommandResult

router = APIRouter(prefix="/smart", tags=["smartctl"])

@router.get("/{disk}", response_model=CommandResult)
def smart_status(disk: str):
    return run_cmd(["smartctl", "-j", "-a", disk])