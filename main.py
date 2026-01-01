from auth import router as auth_router
from fastapi import FastAPI, UploadFile, File
from fastapi import Depends
from auth import get_current_user
# import numpy as np
# from PIL import Image
# import tensorflow as tf
import os
import shutil
from datetime import datetime,timedelta
from disease_info import DISEASE_INFO
from fastapi.middleware.cors import CORSMiddleware
from models import PredictionHistory
from sqlalchemy.orm import Session
from database import get_db



app = FastAPI()
app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ "http://localhost:5173",
        "https://your-vercel-frontend.vercel.app"],  # React URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


MODEL_PATH = "model/trained_plant_disease_model.keras"
# model = tf.keras.models.load_model(MODEL_PATH)

CLASS_NAMES = [
    'Apple___Apple_scab',
    'Apple___Black_rot',
    'Apple___Cedar_apple_rust',
    'Apple___healthy',
    'Blueberry___healthy',
    'Cherry_(including_sour)___Powdery_mildew',
    'Cherry_(including_sour)___healthy',
    'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot',
    'Corn_(maize)___Common_rust_',
    'Corn_(maize)___Northern_Leaf_Blight',
    'Corn_(maize)___healthy',
    'Grape___Black_rot',
    'Grape___Esca_(Black_Measles)',
    'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)',
    'Grape___healthy',
    'Orange___Haunglongbing_(Citrus_greening)',
    'Peach___Bacterial_spot',
    'Peach___healthy',
    'Pepper,_bell___Bacterial_spot',
    'Pepper,_bell___healthy',
    'Potato___Early_blight',
    'Potato___Late_blight',
    'Potato___healthy',
    'Raspberry___healthy',
    'Soybean___healthy',
    'Squash___Powdery_mildew',
    'Strawberry___Leaf_scorch',
    'Strawberry___healthy',
    'Tomato___Bacterial_spot',
    'Tomato___Early_blight',
    'Tomato___Late_blight',
    'Tomato___Leaf_Mold',
    'Tomato___Septoria_leaf_spot',
    'Tomato___Spider_mites Two-spotted_spider_mite',
    'Tomato___Target_Spot',
    'Tomato___Tomato_Yellow_Leaf_Curl_Virus',
    'Tomato___Tomato_mosaic_virus',
    'Tomato___healthy'
]

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def home():
    return {
        "message": "MAIN.PY RUNNING",
        "file": __file__
    }

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    return {
        "disease": "Apple Scab",
        "confidence": 92.4
    }

# async def predict(
#     file: UploadFile = File(...),
#     current_user: dict = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     path = os.path.join(UPLOAD_DIR, file.filename)
#     with open(path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)
#
#     img = Image.open(path).convert("RGB")
#     img = img.resize((128, 128))
#
#     img_array = np.array(img)
#     img_array = np.expand_dims(img_array, axis=0)
#
#     preds = model.predict(img_array)
#     index = int(np.argmax(preds))
#     confidence = float(np.max(preds))
#     confidence_percent = round(confidence * 100, 2)
#
#     if confidence_percent < 50:
#         message = "Low confidence. Please upload a clear leaf image.The prediction may or may not be correct"
#     else:
#         message = "Prediction looks reliable."
#
#     predicted_class = CLASS_NAMES[index]
#     disease_details = DISEASE_INFO.get(predicted_class, {})
#
#     history = PredictionHistory(
#         user_id=current_user.id,
#         disease_name=predicted_class,
#         confidence=confidence_percent
#     )
#     db.add(history)
#     db.commit()
#
#     return {
#         "prediction": CLASS_NAMES[index],
#         "confidence": round(confidence * 100, 2),
#         "details": disease_details,
#         "message": message
#     }

@app.get("/history")
def get_history(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return (
        db.query(PredictionHistory)
        .filter(PredictionHistory.user_id == current_user.id)
        .order_by(PredictionHistory.created_at.desc())
        .all()
    )

from database import engine
from models import Base

Base.metadata.create_all(bind=engine)

from database import init_db

@app.on_event("startup")
def startup():
    init_db()



