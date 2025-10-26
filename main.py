from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from nmdctl_api import router as nmdctl_router
from smartctl_api import router as smartctl_router
from disks_api import router as disks_router

app = FastAPI(title="NonRAID API")

# Mount /static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

# Mount all routers under /api
app.include_router(nmdctl_router, prefix="/api")
app.include_router(smartctl_router, prefix="/api")
app.include_router(disks_router, prefix="/api")

# Serve the web UI
@app.get("/")
def read_root():
    return FileResponse("webui.html")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
