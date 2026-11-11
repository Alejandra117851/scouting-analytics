
const $ = (selector) => document.querySelector(selector);

// =====================================
// NAVEGACIÓN ENTRE APARTADOS
// =====================================

const navigationButtons = document.querySelectorAll("[data-view]");
const pages = document.querySelectorAll(".page-view");

function showView(viewName) {
    // Mostrar únicamente la vista seleccionada
    pages.forEach((page) => {
        page.classList.toggle(
            "active",
            page.dataset.page === viewName
        );
    });

    // Actualizar el botón activo
    navigationButtons.forEach((button) => {
        const isActive = button.dataset.view === viewName;

        button.classList.toggle("active", isActive);

        if (isActive) {
            button.setAttribute("aria-current", "page");
        } else {
            button.removeAttribute("aria-current");
        }
    });

    // Actualizar la dirección de la página
    const url = new URL(window.location.href);
    url.searchParams.set("vista", viewName);
    window.history.replaceState({}, "", url);

    // Subir al inicio al cambiar de apartado
    window.scrollTo({
        top: 0,
        behavior: "auto"
    });
}

// Eventos de navegación
navigationButtons.forEach((button) => {
    button.addEventListener("click", () => {
        showView(button.dataset.view);
    });
});

// Cargar la vista inicial
const initialView = new URLSearchParams(window.location.search).get("vista");

const validViews = [
    "overview",
    "predictor",
    "methodology",
    "results"
];

showView(
    validViews.includes(initialView)
        ? initialView
        : "overview"
);

// =====================================
// ESTADO DE LA API
// =====================================

async function loadHealth() {
    const label = $("#apiStatus");

    try {
        const response = await fetch("/health");

        if (!response.ok) {
            throw new Error("No se pudo consultar el estado");
        }

        const data = await response.json();

        if (data.model_ready) {
            label.textContent = "API y modelo activos";
            label.style.color = "#38d996";
        } else {
            label.textContent = "API activa · falta modelo";
            label.style.color = "#f0b45d";
        }

    } catch (error) {
        label.textContent = "API no disponible";
        label.style.color = "#ff8b83";
    }
}

// =====================================
// CARGAR MÉTRICAS DEL MODELO
// =====================================

async function loadMetrics() {
    try {
        const response = await fetch("/metrics");

        if (!response.ok) {
            throw new Error("No hay métricas disponibles");
        }

        const data = await response.json();

        $("#accuracy").textContent =
            `${(data.accuracy * 100).toFixed(1)}%`;

        $("#precision").textContent =
            `${(data.precision * 100).toFixed(1)}%`;

        $("#recall").textContent =
            `${(data.recall * 100).toFixed(1)}%`;

        $("#auc").textContent =
            Number(data.roc_auc).toFixed(3);

        $("#dataStatus").textContent =
            `${data.registros} jugadores analizados · métricas del modelo`;

    } catch (error) {
        $("#dataStatus").textContent =
            "No fue posible cargar las métricas del modelo.";
    }
}

// =====================================
// PREDICCIÓN DE JUGADORES
// =====================================

const playerForm = $("#playerForm");

playerForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const form = event.currentTarget;

    const button = form.querySelector("button[type='submit']");
    const buttonText = button.querySelector("span");

    const error = $("#errorBox");
    const result = $("#resultBox");

    error.hidden = true;
    result.hidden = true;

    button.disabled = true;
    buttonText.textContent = "Analizando perfil...";

    // Obtener los datos del formulario
    const values = Object.fromEntries(
        new FormData(form).entries()
    );

    const payload = {
        edad: Number(values.edad),
        estatura_cm: Number(values.estatura_cm),
        posicion: values.posicion
    };

    try {
        // Enviar datos al backend
        const response = await fetch("/predict", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (!response.ok) {
            const detail = typeof data.detail === "string"
                ? data.detail
                : "Verifica los datos ingresados.";

            throw new Error(detail);
        }

        // Mostrar resultado de la predicción
        $("#resultClass").textContent =
            data.jugador_clasificacion.toUpperCase();

        $("#probability").textContent =
            `${data.probabilidad_elite.toFixed(1)}%`;

        $("#progressBar").style.width =
            `${Math.max(
                0,
                Math.min(100, data.probabilidad_elite)
            )}%`;

        $("#resultMessage").textContent =
            data.mensaje;

        $("#resultWarning").textContent =
            data.advertencia;

        result.hidden = false;

    } catch (errorResponse) {
        error.textContent =
            errorResponse.message ||
            "No fue posible conectar con el servicio.";

        error.hidden = false;

    } finally {
        button.disabled = false;
        buttonText.textContent = "Analizar jugador";
    }
});

// =====================================
// INICIAR SERVICIOS
// =====================================

loadHealth();
loadMetrics();
