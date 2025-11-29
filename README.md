# Spotify Audio Features Project

## Running the Application

### Backend (FastAPI)
```bash
# From the backend directory:
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

The backend will run on `http://localhost:8000`

### Frontend (React + Vite)
```bash
# From the frontend directory:
cd frontend
npm run dev
```

The frontend will run on `http://localhost:5173`

## Project Structure
```
Spotify Audio Features Project/
├── backend/
│   ├── venv/
│   ├── main.py          # FastAPI app
│   ├── features.py      # Audio analysis engine
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── Dashboard.jsx
│   │   ├── App.jsx
│   │   └── index.css
│   └── package.json
└── test.wav             # Sample audio file
```

## Features
- **Energy**: RMS loudness + spectral centroid
- **Danceability**: Beat stability analysis
- **Tempo**: BPM detection
- **Acousticness**: Spectral flatness (inverted)
- **Valence**: Major/Minor key detection
