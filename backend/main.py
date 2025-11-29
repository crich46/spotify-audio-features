from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import shutil
import os
import uuid
from .features import AudioFeatureExtractor

# Database Setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./songs.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Song(Base):
    __tablename__ = "songs"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    features = Column(JSON)

Base.metadata.create_all(bind=engine)

# App Setup
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Feature Extractor
extractor = AudioFeatureExtractor()

class AnalysisResponse(BaseModel):
    filename: str
    features: dict

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_audio(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Save file temporarily
    temp_filename = f"temp_{uuid.uuid4()}.{file.filename.split('.')[-1]}"
    with open(temp_filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # Extract features
        features = extractor.extract_features(temp_filename)
        if features is None:
            raise HTTPException(status_code=400, detail="Could not analyze audio file")
        
        # Save to DB
        db_song = Song(filename=file.filename, features=features)
        db.add(db_song)
        db.commit()
        db.refresh(db_song)
        
        return {"filename": file.filename, "features": features}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

@app.get("/history")
def get_history(db: Session = Depends(get_db)):
    songs = db.query(Song).all()
    return [{"filename": s.filename, "features": s.features} for s in songs]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
