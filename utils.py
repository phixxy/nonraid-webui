from pydantic import BaseModel
import subprocess

class CommandResult(BaseModel):
    command: str
    output: str
    success: bool

def run_cmd(cmd: list[str]) -> CommandResult:
    try:
        result = subprocess.run(cmd, text=True, capture_output=True)
        return CommandResult(command=" ".join(cmd), output=result.stdout.strip(), success=True)
    except subprocess.CalledProcessError as e:
        output = (e.stdout or "") + (e.stderr or "")
        return CommandResult(command=" ".join(cmd), output=output.strip(), success=False)
