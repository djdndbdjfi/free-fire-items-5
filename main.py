from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# 🔐 Config
API_KEY = os.getenv("API_KEY", "NRCODEX")
ROOT_FOLDER = "all items"  # Root directory under which batch folders exist

# 🌍 Optional: CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/item-image", response_class=FileResponse, responses={
    200: {"content": {"image/png": {}}},
    401: {"description": "Unauthorized"},
    404: {"description": "Item not found"}
})
async def get_item_image(
    id: str = Query(..., description="Image ID without extension"),
    key: str = Query(..., description="Your API key")
):
    """
    Fetch PNG image by ID from dynamic batch folders under `all items/`.
    """
    if key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    # Ensure ROOT_FOLDER exists
    if not os.path.isdir(ROOT_FOLDER):
        raise HTTPException(status_code=500, detail=f"Root folder '{ROOT_FOLDER}' not found")

    # Scan all subfolders for the image
    for sub in os.listdir(ROOT_FOLDER):
        sub_path = os.path.join(ROOT_FOLDER, sub)
        if os.path.isdir(sub_path):
            file_path = os.path.join(sub_path, f"{id}.png")
            if os.path.isfile(file_path):
                return FileResponse(file_path, media_type="image/png")

    # If not found in any batch folder
    raise HTTPException(status_code=404, detail="Item not found")