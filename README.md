# SCOUTING ANALYTICS | Ecosistema Analítico Deportivo

Aplicación académica para apoyar el scouting deportivo mediante un modelo Random Forest que clasifica jugadores como **Élite** o **Estándar** a partir de edad, estatura y posición.

## 1. Arquitectura

- **MySQL:** fuente relacional de jugadores.
- **Python / pandas:** extracción y preparación.
- **Scikit-learn:** árboles de decisión, Random Forest y GridSearchCV.
- **Joblib:** persistencia del modelo y metadatos.
- **FastAPI + Pydantic:** API REST validada.
- **HTML, CSS y JavaScript:** interfaz web que consume la API mediante `fetch`.

## 2. Requisitos

- Python 3.10 o superior.
- MySQL 8 o compatible.
- Base de datos con tabla `players` y columnas `player_id`, `name`, `position`, `height_in_cm`, `date_of_birth`, `market_value_in_eur`.

El ZIP conserva el esquema de datos de los ejercicios anteriores. Si tu base tiene otro nombre o estructura, ajusta únicamente la consulta en `exportar_modelo.py`.

## 3. Instalación en Windows (PowerShell)

Abre la terminal dentro de la carpeta del proyecto:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Si PowerShell bloquea la activación, puedes ejecutar los comandos usando `.\.venv\Scripts\python.exe` sin activar el entorno.

Crea tu configuración local:

```powershell
Copy-Item .env.example .env
```

Edita `.env` con el host, puerto, usuario, contraseña y nombre de tu base MySQL. **No compartas ese archivo.**

## 4. Base de datos

La consulta del entrenamiento utiliza la tabla `players` con los campos indicados arriba. En el ZIP original también se encuentra `data_muestra_transfermarkt.sql`, que puede servir para crear una base de práctica si todavía no tienes la base del curso.

Para usar ese SQL:
1. Crea la base `mineria_datos` en MySQL.
2. Importa el archivo `data_muestra_transfermarkt.sql`.
3. Configura `.env` con `DB_NAME=mineria_datos`.

La base de muestra es pequeña y sirve para comprobar el flujo técnico; para el análisis académico final utiliza la base real suministrada por el profesor.

## 5. Entrenar y exportar el modelo

Desde la raíz del proyecto:

```powershell
python exportar_modelo.py
```

El proceso:
1. Consulta MySQL.
2. Calcula el umbral del percentil 75 del valor comercial.
3. Imputa la estatura con mediana por posición y la edad con mediana de entrenamiento.
4. Aplica One-Hot Encoding.
5. Compara árbol libre y árbol podado.
6. Optimiza Random Forest con GridSearchCV y `class_weight='balanced'`.
7. Calcula Accuracy, Precision, Recall, F1 y ROC-AUC.
8. Genera las gráficas y guarda `models/modelo_scouting_rf.joblib`.

El modelo no se incluye preentrenado en esta entrega porque debe generarse con la base de datos disponible en tu equipo. Así se evita presentar como reales resultados que no se han ejecutado allí.

## 6. Iniciar la API y el aplicativo

En una terminal:

```powershell
uvicorn main_api:app --reload
```

Abre:
- Aplicativo: http://127.0.0.1:8000
- Documentación interactiva: http://127.0.0.1:8000/docs
- Estado: http://127.0.0.1:8000/health

Primero debes haber ejecutado `python exportar_modelo.py`.

## 7. Prueba de predicción

La interfaz web presenta un formulario para edad, estatura y posición. La API recibe JSON en `POST /predict` y devuelve clase estimada y probabilidad.

Ejemplo de cuerpo:

```json
{
  "edad": 22,
  "estatura_cm": 182,
  "posicion": "Attack"
}
```

La predicción es una herramienta de apoyo académico, no una valoración definitiva del talento deportivo. El modelo utiliza variables limitadas y el objetivo se deriva del valor comercial histórico.

## 8. Seguridad implementada

- Secretos fuera del código fuente mediante `.env`.
- `.env` excluido por `.gitignore` y no incluido en el ZIP.
- Conexión MySQL con tiempo límite y cierre garantizado.
- Entrenamiento mediante consulta SELECT fija.
- Validación de tipos y rangos con Pydantic.
- API sin endpoints que ejecuten SQL arbitrario.
- CORS limitado al origen local del aplicativo.
- Rutas de archivos construidas desde `Path(__file__)`, sin rutas absolutas dependientes del computador.

## 9. Archivos principales

```text
scouting_analytics_final/
├── main_api.py
├── exportar_modelo.py
├── index.html
├── requirements.txt
├── .env.example
├── src/
│   └── database/
│       └── connection2.py
├── models/
├── reports/
│   └── figures/
└── static/
    ├── styles.css
    └── app.js
```

## 10. Antes de entregar

- Ejecuta el entrenamiento conectado a la base real.
- Verifica que `reports/metricas_modelo.json` y las figuras se hayan generado.
- Inicia la API y realiza pruebas con jugadores de ejemplo.
- Toma capturas reales de la API y de la interfaz funcionando.
- Completa el informe ejecutivo con las métricas obtenidas en tu ejecución.
