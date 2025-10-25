# nmdctl python api
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import subprocess
import uvicorn

app = FastAPI(title="nmdctl Web API")

class CommandResult(BaseModel):
    command: str
    output: str
    success: bool

def run_cmd(cmd: list[str]) -> CommandResult:
    try:
        result = subprocess.run(cmd, text=True, capture_output=True, check=True)
        return CommandResult(command=" ".join(cmd), output=result.stdout.strip(), success=True)
    except subprocess.CalledProcessError as e:
        return CommandResult(command=" ".join(cmd), output=result.stderr.strip(), success=False)

# This really needs to be removed in the long run so it isn't run as root.
@app.get("/")
def read_root():
    return FileResponse("webui.html")

@app.get("/array/status", response_model=CommandResult)
def array_status():
    cmd = ["nmdctl", "status", "-o", "json"]
    return run_cmd(cmd)

@app.post("/array/{action}/{extra:path}", response_model=CommandResult)
def array_action(action: str, extra: str = ""):
    if action not in ["start", "stop", "reload", "replace", "mount", "unmount", "check"]:
        raise HTTPException(status_code=400, detail="Invalid action")
    if extra:
        extra_args = extra.split("/")
    else:
        extra_args = []
    cmd = ["nmdctl", action] + extra_args
    return run_cmd(cmd)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
