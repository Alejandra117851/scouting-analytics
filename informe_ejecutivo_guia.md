# Guía para el informe ejecutivo

Completa este documento después de ejecutar el proyecto con la base de datos real. No copies valores de ejemplo ni inventes métricas.

## 1. Portada institucional
- Universidad:
- Programa: Ingeniería de Sistemas
- Asignatura:
- Título: Ecosistema Analítico End-to-End para Scouting Deportivo
- Integrantes:
- Docente:
- Fecha:

## 2. Introducción y objetivos
Explica el problema de selección de talento, la utilidad de combinar datos y criterio profesional y la aplicación de las fases CRISP-DM: comprensión del negocio, comprensión de datos, preparación, modelado, evaluación y despliegue.

## 3. Marco teórico y glosario
Desarrolla los conceptos indicados por el docente: imputación por mediana agrupada, target binario por percentil 75, One-Hot Encoding, muestreo estratificado, overfitting, pre-pruning, paradoja de accuracy, class_weight='balanced', Random Forest y Bagging, GridSearchCV, ROC-AUC, Gini Importance, Joblib, API REST y arquitectura cliente-servidor.

## 4. Análisis de resultados
Incluye las figuras generadas en `reports/figures/` y utiliza los valores de `reports/metricas_modelo.json`.

- Diagnóstico de overfitting: compara accuracy de entrenamiento y prueba para árbol libre, árbol podado y Random Forest.
- ROC-AUC: interpreta el AUC real y compara la curva ROC del árbol podado y el bosque.
- Importancia de variables: describe las variables con mayor importancia sin atribuir causalidad.
- Métricas: reporta accuracy, precision, recall y F1; explica la matriz de confusión.

## 5. Arquitectura de despliegue
Describe MySQL → Python/pandas → preprocesamiento → Random Forest → Joblib → FastAPI → HTML/CSS/JS. Inserta capturas reales de `/docs`, `/health`, formulario y respuesta de `/predict`.

## 6. Conclusiones y recomendaciones
Explica cómo el sistema prioriza perfiles para revisión de scouting. Señala limitaciones: variables disponibles, tamaño y actualidad de los datos, sesgos de mercado y necesidad de validación humana.
