import json
import os

import geopandas as gpd
import pandas as pd
import plotly.express as px
import streamlit as st

from app import GEOJSON_FILE, PREDICCIONES_FILE, RESULTADOS_FILE


def mostrar_mapa_resultados(resultados_path=None, geojson_path=None):
    """Muestra un mapa con los resultados reales de las elecciones por departamento"""
    st.subheader("🗺️ Mapa de resultados reales por departamento")

    # Usar rutas del módulo app si no se especifican
    if resultados_path is None:
        resultados_path = RESULTADOS_FILE
    if geojson_path is None:
        geojson_path = GEOJSON_FILE

    try:
        # Intenta abrir el archivo directamente primero
        if os.path.exists(resultados_path):
            with open(resultados_path, "r", encoding="utf-8") as f:
                resultados_reales = json.load(f)
        else:
            # Fallback a pandas si es necesario
            resultados_reales = pd.read_json(resultados_path).to_dict()

        st.success(
            f"Archivo de resultados cargado correctamente desde: {resultados_path}"
        )
    except Exception as e:
        st.error(f"No se pudo cargar resultados: {e}")
        st.info(f"Ruta intentada: {os.path.abspath(resultados_path)}")
        return

    data = []
    for departamento, datos in resultados_reales.items():
        partido = datos.get("partido", "Sin dato")
        data.append({"departamento": departamento.upper(), "partido": partido})
    _mostrar_mapa(data, geojson_path)


def mostrar_mapa_predicciones(
    nombre_usuario, predicciones_path=None, geojson_path=None
):
    """Muestra un mapa con las predicciones de un usuario específico"""
    st.subheader(f"🗺️ Predicción de {nombre_usuario}")

    # Usar rutas del módulo app si no se especifican
    if predicciones_path is None:
        predicciones_path = PREDICCIONES_FILE
    if geojson_path is None:
        geojson_path = GEOJSON_FILE

    try:
        if os.path.exists(predicciones_path):
            with open(predicciones_path, "r", encoding="utf-8") as f:
                predicciones = json.load(f)
            st.success(
                f"Archivo de predicciones cargado correctamente desde: {predicciones_path}"
            )
        else:
            st.error(f"No se encontró el archivo: {predicciones_path}")
            st.info(
                f"Ruta completa intentada: {os.path.abspath(predicciones_path)}"
            )
            return
    except Exception as e:
        st.error(f"No se pudo cargar predicciones: {e}")
        return

    if nombre_usuario not in predicciones:
        st.warning("Ese usuario no existe o no ha hecho predicciones.")
        return

    data = []
    for departamento, datos in predicciones[nombre_usuario].items():
        partido = datos.get("partido", "Sin dato")
        data.append({"departamento": departamento.upper(), "partido": partido})
    _mostrar_mapa(data, geojson_path)


def _mostrar_mapa(data, geojson_path):
    df_resultados = pd.DataFrame(data)

    try:
        gdf = gpd.read_file(geojson_path)
    except Exception as e:
        st.error(f"No se pudo cargar el geojson: {e}")
        return

    # Usar la columna correcta para los nombres de departamento
    gdf["name"] = gdf["NAME_1"].str.upper()
    df_resultados["departamento"] = df_resultados["departamento"].str.upper()

    gdf = gdf.merge(
        df_resultados, left_on="name", right_on="departamento", how="left"
    )

    color_map = {
        "Frente Amplio": "navy",
        "Coalición Republicana": "blue",
        "Partido Nacional": "skyblue",
        "Partido Colorado": "red",
        "Cabildo Abierto": "yellow",
        "Asamblea Popular": "purple",
        "Sin dato": "lightgray",
    }

    gdf["color"] = gdf["partido"].map(color_map).fillna("gray")

    fig = px.choropleth(
        gdf,
        geojson=gdf.geometry,
        locations=gdf.index,
        color="partido",
        color_discrete_map=color_map,
        projection="mercator",
        hover_name="name",
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(height=600, margin={"r": 0, "t": 0, "l": 0, "b": 0})
    st.plotly_chart(fig)
