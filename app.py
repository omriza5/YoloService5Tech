from fastapi import FastAPI 
from controllers.health_controller import router as health_router
from controllers.prediction_controller import router as prediction_router
from controllers.labels_controller import router as labels_router
from controllers.image_controller import router as image_router
from controllers.user_controller import router as user_router
from controllers.stats_controller import router as stats_router
from db.utils import init_db
import os

# Disable GPU usage
import torch
torch.cuda.is_available = lambda: False

app = FastAPI()

# Initialize database
init_db()

# Import middleware to ensure registration
import middlewares.auth

# app routes
app.include_router(health_router)
app.include_router(prediction_router)
app.include_router(labels_router)
app.include_router(image_router)
app.include_router(user_router)
app.include_router(stats_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)
