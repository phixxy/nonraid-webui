from fastapi import APIRouter, HTTPException
from utils import run_cmd, CommandResult

router = APIRouter(prefix="/disks", tags=["disks"])

@router.get("/list", response_model=CommandResult)
def list_disks():
    cmd = ["lsblk", "-J"]
    return run_cmd(cmd)

@router.get("/unassigned", response_model=CommandResult)
def list_unassigned_disks():
    try:
        # Get all disks from lsblk
        lsblk_cmd = [
            "lsblk",
            "-J",
            "-o",
            "NAME,KNAME,MODEL,SERIAL,UUID,SIZE,TYPE,MOUNTPOINT,FSTYPE"
        ]
        lsblk_res = run_cmd(lsblk_cmd)
        if not lsblk_res.success:
            raise HTTPException(status_code=500, detail="Failed to list disks")
        lsblk_json = lsblk_res.output

        # Get disks in the array
        array_cmd = ["nmdctl", "status", "-o", "json"]
        array_res = run_cmd(array_cmd)
        if not array_res.success:
            raise HTTPException(status_code=500, detail="Failed to get array status")
        array_json = array_res.output

        # Collect array disk names and ids
        array_disks = set()
        array_disk_ids = set()
        for d in array_json.get("disks", []):
            if d.get("disk_name"):
                array_disks.add(d["disk_name"])
            if d.get("disk_id"):
                array_disk_ids.add(d["disk_id"])

        # Filter out array disks
        def is_array_disk(disk):
            # Make model_serial for comparison
            model = (disk.get("model") or "").replace(" ", "_")
            serial = disk.get("serial") or ""
            model_serial = f"{model}_{serial}"
            return (
                disk.get("name") in array_disks      # matches nmdX devices
                or model_serial in array_disk_ids    # matches model_serial style disk_id
            )

        nonarray_disks = []
        for d in lsblk_json.get("blockdevices", []):
            if not is_array_disk(d):
                nonarray_disks.append(d)

        return CommandResult(
            command="lsblk -J + filtered non-array disks",
            output={"blockdevices": nonarray_disks},
            success=True
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/partition/{diskName}", response_model=CommandResult)
def partition_disk(diskName: str):
    try:
        cmd = ["sgdisk", "-o", "-a", "8", "-n", "1:32K:0", f"/dev/{diskName}"]
        result = run_cmd(cmd)
        if not result.success:
            raise HTTPException(status_code=500, detail=f"Failed to partition {diskName}")
        return CommandResult(
            command=" ".join(cmd),
            output=result.output,
            success=True
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/format/{diskName}/{fstype}", response_model=CommandResult)
def format_disk(diskName: str, fstype: str):
    try:
        cmd = [f"mkfs.{fstype}", f"/dev/{diskName}"]
        result = run_cmd(cmd)
        if not result.success:
            raise HTTPException(status_code=500, detail=f"Failed to format {diskName} as {fstype}")
        return CommandResult(
            command=" ".join(cmd),
            output=result.output,
            success=True
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))