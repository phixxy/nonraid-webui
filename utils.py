from pydantic import BaseModel
import subprocess
import json
from typing import Any

class CommandResult(BaseModel):
    command: str
    output: Any
    success: bool

def run_cmd(cmd: list[str]) -> CommandResult:
    try:
        result = subprocess.run(cmd, text=True, capture_output=True)
        try:
            # Try parsing stdout as JSON
            output = json.loads(result.stdout)
        except json.JSONDecodeError:
            output = result.stdout.strip()
        return CommandResult(command=" ".join(cmd), output=output, success=True)
    except subprocess.CalledProcessError as e:
        output = (e.stdout or "") + (e.stderr or "")
        try:
            output = json.loads(output)
        except json.JSONDecodeError:
            pass
        return CommandResult(command=" ".join(cmd), output=output, success=False)
