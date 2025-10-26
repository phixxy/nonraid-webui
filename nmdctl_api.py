# nmdctl python api
import os
from fastapi import APIRouter, HTTPException
from utils import run_cmd, CommandResult

router = APIRouter(prefix="/array", tags=["nmdctl"])

STATE_FILE = "/var/lib/nonraid/array.running"

@router.get("/status", response_model=CommandResult)
def array_status():
    cmd = ["nmdctl", "status", "-o", "json"]
    return run_cmd(cmd)

@router.post("/{action}/{extra:path}", response_model=CommandResult)
def array_action(action: str, extra: str = ""):
    if action not in ["start", "reload", "replace", "mount", "unmount", "check"]:
        raise HTTPException(status_code=400, detail="Invalid action")
    if extra:
        extra_args = extra.split("/")
    else:
        extra_args = []
    cmd = ["nmdctl", action] + extra_args
    return run_cmd(cmd)

@router.post("/stop", response_model=CommandResult)
def stop_array():
    cmd = ["nmdctl", "stop"]
    result = run_cmd(cmd)
    if result.success:
        try:
            if os.path.exists(STATE_FILE):
                os.remove(STATE_FILE)
                print(f"Removed state file: {STATE_FILE}")
        except Exception as e:
            #TODO add logging
            print(f"Warning: could not remove {STATE_FILE}: {e}")
    return result