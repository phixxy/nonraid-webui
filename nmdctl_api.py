# nmdctl python api
from fastapi import APIRouter, HTTPException
from utils import run_cmd, CommandResult

router = APIRouter(prefix="/array", tags=["nmdctl"])

@router.get("/status", response_model=CommandResult)
def array_status():
    cmd = ["nmdctl", "status", "-o", "json"]
    return run_cmd(cmd)

@router.post("/{action}/{extra:path}", response_model=CommandResult)
def array_action(action: str, extra: str = ""):
    if action not in ["start", "stop", "reload", "replace", "mount", "unmount", "check"]:
        raise HTTPException(status_code=400, detail="Invalid action")
    if extra:
        extra_args = extra.split("/")
    else:
        extra_args = []
    cmd = ["nmdctl", action] + extra_args
    return run_cmd(cmd)

