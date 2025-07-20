

from fastapi import HTTPException
from fastapi.responses import FileResponse
import os

def get_image_by_type_and_filename(type, filename):
    if type not in ["original", "predicted"]:
        raise HTTPException(status_code=400, detail="Invalid image type")
    path = os.path.join("uploads", type, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(path)