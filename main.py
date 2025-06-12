from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# 🔐 Config
API_KEY = os.getenv("API_KEY", "NRCODEX")
ROOT_FOLDER = os.getenv("ROOT_FOLDER", "items")  # Matches your 'items' folder

# 🌍 CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", response_class=JSONResponse)
async def health_check():
    """Check if the server is running."""
    logger.info("Health check requested")
    return {"status": "ok"}

@app.get("/item-image", response_class=FileResponse, responses={
    200: {"content": {"image/png": {}}},
    401: {"description": "Unauthorized"},
    404: {"description": "Item not found"},
    500: {"description": "Server error"}
})
async def get_item_image(
    id: str = Query(..., description="Image ID without extension"),
    key: str = Query(..., description="API key")
):
    """Fetch PNG image by ID from batch folders under items/."""
    logger.info(f"Request for image ID: {id}")
    if key != API_KEY:
        logger.error(f"Invalid API key: {key}")
        raise HTTPException(status_code=401, detail="Invalid API key")

    logger.info(f"Checking root folder: {ROOT_FOLDER}")
    if not os.path.isdir(ROOT_FOLDER):
        logger.error(f"Root folder '{ROOT_FOLDER}' does not exist")
        raise HTTPException(status_code=500, detail=f"Root folder '{ROOT_FOLDER}' not found")

    for sub in os.listdir(ROOT_FOLDER):
        sub_path = os.path.join(ROOT_FOLDER, sub)
        logger.info(f"Checking subfolder: {sub_path}")
        if os.path.isdir(sub_path):
            file_path = os.path.join(sub_path, f"{id}.png")
            logger.info(f"Looking for file: {file_path}")
            if os.path.isfile(file_path):
                logger.info(f"File found: {file_path}")
                return FileResponse(file_path, media_type="image/png")

    logger.warning(f"Item not found for ID: {id}")
    raise HTTPException(status_code=404, detail="Item not found")

@app.get("/list-images", response_class=JSONResponse, responses={
    200: {"description": "List of PNG files"},
    401: {"description": "Unauthorized"},
    500: {"description": "Server error"}
})
async def list_images(
    key: str = Query(..., description="API key")
):
    """Scan all batch folders under items/ and list PNG files."""
    logger.info("Request to list all images")
    if key != API_KEY:
        logger.error(f"Invalid API key: {key}")
        raise HTTPException(status_code=401, detail="Invalid API key")

    logger.info(f"Checking root folder: {ROOT_FOLDER}")
    if not os.path.isdir(ROOT_FOLDER):
        logger.error(f"Root folder '{ROOT_FOLDER}' does not exist")
        raise HTTPException(status_code=500, detail=f"Root folder '{ROOT_FOLDER}' not found")

    batch_folders = [f"batch-{i}" for i in range(1, 7)]  # batch-1 to batch-6
    image_list = {}

    for batch in batch_folders:
        batch_path = os.path.join(ROOT_FOLDER, batch)
        logger.info(f"Scanning batch folder: {batch_path}")
        if os.path.isdir(batch_path):
            png_files = [f for f in os.listdir(batch_path) if f.lower().endswith(".png")]
            image_list[batch] = png_files
            logger.info(f"Found {len(png_files)} PNG files in {batch}: {png_files}")
        else:
            logger.warning(f"Batch folder not found: {batch_path}")
            image_list[batch] = []

    return JSONResponse(content={"images": image_list})
