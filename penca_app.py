import streamlit as st

from app import cargar_resultados, hacer_prediccion, ver_mapa, ver_puntajes

st.title("📊 Penca Elecciones Municipales 2025 - Uruguay")

menu = st.sidebar.selectbox(
    "Menú",
    [
        "Hacer Predicción",
        "Cargar Resultados (organizador)",
        "Ver Puntajes",
        "Ver Mapa",
    ],
)

match menu:
    case "Hacer Predicción":
        hacer_prediccion()
    case "Cargar Resultados (organizador)":
        cargar_resultados()
    case "Ver Puntajes":
        ver_puntajes()
    case "Ver Mapa":
        ver_mapa()
