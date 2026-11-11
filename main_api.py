"""API REST para el modelo de scouting deportivo."""
from pathlib import Path
from typing import Literal
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ConfigDict

ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "models" / "modelo_scouting_rf.joblib"

app = FastAPI(
    title="Scouting Analytics API",
    description="API académica para clasificación de jugadores con Random Forest.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

app.mount("/static", StaticFiles(directory=str(ROOT / "static")), name="static")
app.mount("/reports", StaticFiles(directory=str(ROOT / "reports")), name="reports")


class PlayerInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    edad: int = Field(ge=15, le=50, description="Edad del jugador en años")
    estatura_cm: float = Field(ge=140, le=220, description="Estatura en centímetros")
    posicion: str = Field(min_length=2, max_length=50)


def load_package():
    if not MODEL_PATH.is_file():
        raise HTTPException(
            status_code=503,
            detail="Modelo no disponible. Ejecuta primero: python exportar_modelo.py"
        )
    try:
        return joblib.load(MODEL_PATH)
    except Exception:
        raise HTTPException(status_code=503, detail="No fue posible cargar el modelo exportado.")


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(ROOT / "index.html")


@app.get("/health")
def health():
    return {"status": "ok", "model_ready": MODEL_PATH.is_file(), "service": "scouting-analytics"}


@app.get("/metrics")
def metrics():
    path = ROOT / "reports" / "metricas_modelo.json"
    if not path.is_file():
        raise HTTPException(status_code=404, detail="No hay métricas. Ejecuta el entrenamiento.")
    import json
    return json.loads(path.read_text(encoding="utf-8"))


@app.get("/features")
def features():
    package = load_package()
    return {"features": package["columnas_X"], "positions": [
        col.replace("posicion_", "", 1)
        for col in package["columnas_X"] if col.startswith("posicion_")
    ]}


@app.post("/predict")
def predict(player: PlayerInput):
    package = load_package()
    position = player.posicion.strip()
    row = pd.DataFrame([{
        "edad": player.edad,
        "estatura_cm": player.estatura_cm,
        "posicion": position
    }])
    categorical = pd.get_dummies(row[["posicion"]], prefix="posicion", dtype=int)
    features = pd.concat([row[["edad", "estatura_cm"]].astype(float), categorical], axis=1)
    features = features.reindex(columns=package["columnas_X"], fill_value=0)

    model = package["modelo"]
    prediction = int(model.predict(features)[0])
    probabilities = model.predict_proba(features)[0]
    elite_probability = float(probabilities[list(model.classes_).index(1)])
    return {
        "jugador_clasificacion": "Élite" if prediction == 1 else "Estándar",
        "clase": prediction,
        "probabilidad_elite": round(elite_probability * 100, 2),
        "probabilidad_estandar": round((1 - elite_probability) * 100, 2),
        "posicion": position,
        "mensaje": (
            "El perfil presenta características similares a las observadas en la clase Élite."
            if prediction == 1 else
            "El perfil se aproxima más a la clase Estándar según las variables disponibles."
        ),
        "advertencia": "Resultado orientativo; no reemplaza la evaluación integral de un equipo de scouting."
    }
