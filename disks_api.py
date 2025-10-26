from fastapi import APIRouter, HTTPException
from utils import run_cmd, CommandResult

router = APIRouter(prefix="/disks", tags=["disks"])

@router.get("/list", response_model=CommandResult)
def list_disks():
    cmd = ["lsblk", "-J"]
    return run_cmd(cmd)