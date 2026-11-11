
"""Entrenamiento, evaluación y serialización del ecosistema de scouting."""
from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, roc_curve, confusion_matrix, classification_report
)
from src.database.connection2 import MySQLConnector

ROOT = Path(__file__).resolve().parent
MODEL_DIR = ROOT / "models"
REPORT_DIR = ROOT / "reports"
FIG_DIR = REPORT_DIR / "figures"

QUERY = """
SELECT
    p.player_id,
    p.name AS jugador,
    p.position AS posicion,
    p.height_in_cm AS estatura_cm,
    TIMESTAMPDIFF(YEAR, p.date_of_birth, CURDATE()) AS edad,
    p.market_value_in_eur AS valor_mercado
FROM players AS p
WHERE p.market_value_in_eur IS NOT NULL
"""


def prepare_source(df):
    required = {"posicion", "estatura_cm", "edad", "valor_mercado"}
    missing = required - set(df.columns)

    if missing:
        raise ValueError(f"Faltan columnas en la consulta: {sorted(missing)}")

    data = df.copy()

    for col in ("estatura_cm", "edad", "valor_mercado"):
        data[col] = pd.to_numeric(data[col], errors="coerce")

    data = data.dropna(subset=["valor_mercado"]).copy()
    data["posicion"] = data["posicion"].fillna("Sin Posicion").astype(str)
    data = data.dropna(subset=["edad", "estatura_cm"], how="all")

    if len(data) < 20:
        raise ValueError(
            f"Solo hay {len(data)} registros utilizables. Se requieren al menos 20 "
            "para una evaluación exploratoria."
        )

    threshold = float(data["valor_mercado"].quantile(0.75))
    data["es_elite"] = (data["valor_mercado"] >= threshold).astype(int)

    if data["es_elite"].nunique() != 2 or data["es_elite"].value_counts().min() < 5:
        raise ValueError(
            "No hay suficientes ejemplos de ambas clases para dividir y validar."
        )

    return data, threshold


def impute_by_position(train, other=None):
    """Medianas calculadas solo con train; se reutilizan para test/inferencia."""

    medians = train.groupby("posicion")["estatura_cm"].median().to_dict()
    global_height = float(train["estatura_cm"].median())
    global_age = float(train["edad"].median())

    def apply(frame):
        out = frame.copy()

        out["estatura_cm"] = out.apply(
            lambda r: r["estatura_cm"] if pd.notna(r["estatura_cm"])
            else medians.get(r["posicion"], global_height),
            axis=1
        )

        out["edad"] = out["edad"].fillna(global_age)
        return out

    return (
        apply(train),
        apply(other) if other is not None else None,
        medians,
        global_height,
        global_age
    )


def make_features(frame, columns=None):
    cats = pd.get_dummies(
        frame[["posicion"]],
        prefix="posicion",
        dtype=int
    )

    matrix = pd.concat(
        [frame[["edad", "estatura_cm"]].astype(float), cats],
        axis=1
    )

    if columns is not None:
        matrix = matrix.reindex(columns=columns, fill_value=0)

    return matrix


def save_figures(y_test, tree_free, tree_pruned, forest, X_test, metrics):

    FIG_DIR.mkdir(parents=True, exist_ok=True)

    # Comparación de accuracy: entrenamiento vs prueba
    labels = ["Árbol libre", "Árbol podado", "Random Forest"]

    # CORRECCIÓN: convertir los diccionarios en listas de valores
    train_acc = [
        metrics["accuracy_train"][name] for name in labels
    ]

    test_acc = [
        metrics["accuracy_test"][name] for name in labels
    ]

    x = np.arange(len(labels))

    fig, ax = plt.subplots(figsize=(9, 5))

    ax.bar(x - .18, train_acc, .36, label="Train")
    ax.bar(x + .18, test_acc, .36, label="Test")

    ax.set_xticks(x, labels)
    ax.set_ylim(0, 1.08)
    ax.set_ylabel("Accuracy")
    ax.set_title("Diagnóstico de generalización")
    ax.legend()
    ax.grid(axis="y", alpha=.2)

    fig.tight_layout()
    fig.savefig(FIG_DIR / "overfitting_comparativo.png", dpi=170)
    plt.close(fig)

    # Curvas ROC
    fig, ax = plt.subplots(figsize=(7, 6))

    for label, model in [
        ("Árbol podado", tree_pruned),
        ("Random Forest", forest)
    ]:
        score = model.predict_proba(X_test)[:, 1]

        fpr, tpr, _ = roc_curve(y_test, score)
        auc = roc_auc_score(y_test, score)

        ax.plot(fpr, tpr, label=f"{label} (AUC={auc:.3f})")

    ax.plot(
        [0, 1], [0, 1],
        linestyle="--",
        label="Azar"
    )

    ax.set_xlabel("Tasa de falsos positivos")
    ax.set_ylabel("Tasa de verdaderos positivos")
    ax.set_title("Curvas ROC")
    ax.legend()
    ax.grid(alpha=.2)

    fig.tight_layout()
    fig.savefig(FIG_DIR / "curva_roc.png", dpi=170)
    plt.close(fig)

    # Importancia de variables
    importance = pd.Series(
        forest.feature_importances_,
        index=X_test.columns
    ).sort_values()

    fig, ax = plt.subplots(
        figsize=(9, max(4, len(importance) * .32))
    )

    importance.tail(15).plot(kind="barh", ax=ax)

    ax.set_title("Importancia de variables — Random Forest")
    ax.set_xlabel("Importancia Gini")

    fig.tight_layout()
    fig.savefig(FIG_DIR / "importancia_variables.png", dpi=170)
    plt.close(fig)

    # Matriz de confusión
    cm = confusion_matrix(
        y_test,
        forest.predict(X_test)
    )

    fig, ax = plt.subplots(figsize=(5.5, 4.5))

    im = ax.imshow(cm, cmap="Greens")

    ax.set_xticks([0, 1], ["Estándar", "Élite"])
    ax.set_yticks([0, 1], ["Estándar", "Élite"])

    ax.set_xlabel("Predicción")
    ax.set_ylabel("Valor real")
    ax.set_title("Matriz de confusión — Random Forest")

    for (i, j), value in np.ndenumerate(cm):
        ax.text(j, i, str(value), ha="center", va="center")

    fig.colorbar(im, ax=ax)
    fig.tight_layout()

    fig.savefig(FIG_DIR / "matriz_confusion.png", dpi=170)
    plt.close(fig)


def main():

    MODEL_DIR.mkdir(exist_ok=True)
    REPORT_DIR.mkdir(exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    print("[1/6] Extrayendo datos desde MySQL...")

    raw = MySQLConnector().extract_data(QUERY)

    if raw.empty:
        raise RuntimeError(
            "La consulta no devolvió jugadores. Revisa MySQL y la tabla players."
        )

    data, threshold = prepare_source(raw)

    train_df, test_df = train_test_split(
        data,
        test_size=.20,
        random_state=42,
        stratify=data["es_elite"]
    )

    (
        train_df,
        test_df,
        position_medians,
        global_height,
        global_age
    ) = impute_by_position(train_df, test_df)

    columns = make_features(train_df).columns.tolist()

    X_train = make_features(train_df, columns)
    X_test = make_features(test_df, columns)

    y_train = train_df["es_elite"]
    y_test = test_df["es_elite"]

    print("[2/6] Diagnosticando overfitting...")

    free_tree = DecisionTreeClassifier(random_state=42)

    pruned_tree = DecisionTreeClassifier(
        max_depth=4,
        min_samples_leaf=3,
        random_state=42
    )

    free_tree.fit(X_train, y_train)
    pruned_tree.fit(X_train, y_train)

    print("[3/6] Optimizando Random Forest con GridSearchCV...")

    min_class = int(y_train.value_counts().min())
    folds = min(5, min_class)

    if folds < 2:
        raise ValueError(
            "No hay suficientes registros de la clase minoritaria para validación cruzada."
        )

    forest = RandomForestClassifier(
        random_state=42,
        n_jobs=-1,
        class_weight="balanced"
    )

    grid = GridSearchCV(
        forest,
        {
            "n_estimators": [100, 200],
            "max_depth": [None, 4, 8],
            "min_samples_leaf": [1, 3],
            "max_features": ["sqrt", 0.8]
        },
        scoring="f1",
        cv=StratifiedKFold(
            n_splits=folds,
            shuffle=True,
            random_state=42
        ),
        n_jobs=-1,
        refit=True
    )

    grid.fit(X_train, y_train)

    best_forest = grid.best_estimator_

    print("[4/6] Calculando métricas...")

    models = {
        "Árbol libre": free_tree,
        "Árbol podado": pruned_tree,
        "Random Forest": best_forest
    }

    accuracy_train = {}
    accuracy_test = {}

    for name, model in models.items():

        accuracy_train[name] = float(
            accuracy_score(y_train, model.predict(X_train))
        )

        accuracy_test[name] = float(
            accuracy_score(y_test, model.predict(X_test))
        )

    predictions = best_forest.predict(X_test)
    probabilities = best_forest.predict_proba(X_test)[:, 1]

    metrics = {
        "registros": int(len(data)),
        "registros_train": int(len(train_df)),
        "registros_test": int(len(test_df)),
        "umbral_elite_eur": threshold,
        "accuracy_train": accuracy_train,
        "accuracy_test": accuracy_test,
        "accuracy": float(accuracy_score(y_test, predictions)),
        "precision": float(precision_score(y_test, predictions, zero_division=0)),
        "recall": float(recall_score(y_test, predictions, zero_division=0)),
        "f1_score": float(f1_score(y_test, predictions, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, probabilities)),
        "mejores_hiperparametros": grid.best_params_,
        "mejor_f1_validacion_cruzada": float(grid.best_score_),
        "reporte_clasificacion": classification_report(
            y_test,
            predictions,
            target_names=["Estándar", "Élite"],
            output_dict=True,
            zero_division=0
        ),
        "matriz_confusion": confusion_matrix(
            y_test,
            predictions
        ).tolist(),
        "nota": (
            "Resultados calculados con la base disponible al ejecutar el entrenamiento."
        )
    }

    print("[5/6] Generando visualizaciones...")

    save_figures(
        y_test,
        free_tree,
        pruned_tree,
        best_forest,
        X_test,
        metrics
    )

    package = {
        "modelo": best_forest,
        "columnas_X": columns,
        "medianas_estatura": position_medians,
        "mediana_global_estatura": global_height,
        "mediana_global_edad": global_age,
        "umbral_elite_eur": threshold,
        "version_paquete": 1
    }

    joblib.dump(
        package,
        MODEL_DIR / "modelo_scouting_rf.joblib"
    )

    (REPORT_DIR / "metricas_modelo.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2, default=float),
        encoding="utf-8"
    )

    (REPORT_DIR / "resumen_entrenamiento.txt").write_text(
        "SCOUTING ANALYTICS — RESULTADOS DE ENTRENAMIENTO\n\n"
        + json.dumps(metrics, ensure_ascii=False, indent=2, default=float),
        encoding="utf-8"
    )

    print("[6/6] Proceso finalizado.")

    print(
        f"Registros: {len(data)} | "
        f"Umbral Élite: €{threshold:,.0f}"
    )

    print(
        f"Accuracy: {metrics['accuracy']:.3f} | "
        f"F1: {metrics['f1_score']:.3f} | "
        f"AUC: {metrics['roc_auc']:.3f}"
    )

    print(f"Modelo: {MODEL_DIR / 'modelo_scouting_rf.joblib'}")
    print(f"Métricas y gráficas: {REPORT_DIR}")


if __name__ == "__main__":
    main()
