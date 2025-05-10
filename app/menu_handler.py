import json
import os

import streamlit as st

from app import DEPARTAMENTOS, PREDICCIONES_FILE, RESULTADOS_FILE
from app.candidatos import CANDIDATOS_INTENDENCIA
from app.candidatos_alcalde import CANDIDATOS_ALCALDE_MVD
from app.visualizador_mapa import (mostrar_mapa_predicciones,
                                   mostrar_mapa_resultados)


def cargar_json(path):
    """Carga datos desde un archivo JSON con manejo de errores"""
    # Asegurarse de que el directorio existe
    os.makedirs(os.path.dirname(path), exist_ok=True)

    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except UnicodeDecodeError:
            st.error(
                f"Error: No se pudo decodificar {path}. Asegúrate de que está guardado con codificación UTF-8."
            )
            return {}
        except json.JSONDecodeError:
            st.error(f"Error: Formato JSON inválido en {path}.")
            return {}
    else:
        # Si el archivo no existe, crear uno vacío
        with open(path, "w", encoding="utf-8") as f:
            json.dump({}, f)
        return {}


def guardar_json(path, data):
    """Guarda datos en un archivo JSON con manejo de errores"""
    # Asegurarse de que el directorio existe
    os.makedirs(os.path.dirname(path), exist_ok=True)

    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        st.error(f"Error al guardar en {path}: {e}")
        return False


# Cargar datos al inicio
predicciones = cargar_json(PREDICCIONES_FILE)
resultados_reales = cargar_json(RESULTADOS_FILE)


def hacer_prediccion():
    """Interfaz para que los usuarios hagan sus predicciones"""
    nombre = st.text_input("Tu nombre:", key="nombre_pred")

    if nombre:
        st.subheader("Predicciones de intendencias")
        nueva_prediccion = {}

        for dep in DEPARTAMENTOS:
            if dep in CANDIDATOS_INTENDENCIA:
                st.markdown(f"#### {dep}")
                partidos_disponibles = list(CANDIDATOS_INTENDENCIA[dep].keys())
                partido = st.selectbox(
                    f"Partido ganador en {dep}",
                    partidos_disponibles,
                    key=f"{nombre}_{dep}_partido",
                )
                candidato = st.selectbox(
                    f"Candidato del {partido}",
                    CANDIDATOS_INTENDENCIA[dep][partido],
                    key=f"{nombre}_{dep}_candidato",
                )
                nueva_prediccion[dep] = {
                    "partido": partido,
                    "intendente": candidato,
                }

        # Asegurarnos de que Montevideo existe en nueva_prediccion antes de agregar datos de alcalde
        if "Montevideo" not in nueva_prediccion:
            nueva_prediccion["Montevideo"] = {}

        st.subheader("Predicción de alcalde en Montevideo")
        municipio = st.selectbox(
            "Municipio",
            list(CANDIDATOS_ALCALDE_MVD.keys()),
            key="municipio_mvd",
        )
        agrupacion = st.selectbox(
            "Agrupación política",
            list(CANDIDATOS_ALCALDE_MVD[municipio].keys()),
            key="agrupacion_mvd",
        )
        candidato_alcalde = st.selectbox(
            "Candidato a alcalde",
            CANDIDATOS_ALCALDE_MVD[municipio][agrupacion],
            key="alcalde_mvd",
        )

        nueva_prediccion["Montevideo"]["municipio"] = municipio
        nueva_prediccion["Montevideo"]["agrupacion_alcalde"] = agrupacion
        nueva_prediccion["Montevideo"]["alcalde"] = candidato_alcalde

        if st.button("Guardar Predicción"):
            # Mostrar ruta actual para depuración
            st.info(f"Guardando en: {os.path.abspath(PREDICCIONES_FILE)}")

            # Recargar predicciones antes de actualizar (por si alguien más modificó el archivo)
            predicciones_actualizadas = cargar_json(PREDICCIONES_FILE)
            predicciones_actualizadas[nombre] = nueva_prediccion

            if guardar_json(PREDICCIONES_FILE, predicciones_actualizadas):
                st.success("✅ Predicción guardada correctamente.")
                # Actualizar variable global
                global predicciones
                predicciones = predicciones_actualizadas
            else:
                st.error("❌ Error al guardar la predicción.")


def cargar_resultados():
    st.warning("Solo para organizador/a de la penca")
    st.subheader("Resultados de intendencias")
    for dep in DEPARTAMENTOS:
        if dep in CANDIDATOS_INTENDENCIA:
            ganador = st.selectbox(
                f"Ganador en {dep}",
                CANDIDATOS_INTENDENCIA[dep],
                key=f"res_{dep}",
            )
            if dep not in resultados_reales:
                resultados_reales[dep] = {}
            resultados_reales[dep]["intendente"] = ganador

    st.markdown("### Ganador de Alcaldía (Montevideo)")
    municipio = st.selectbox(
        "Municipio", list(CANDIDATOS_ALCALDE_MVD.keys()), key="res_mvd_muni"
    )
    alcalde_ganador = st.selectbox(
        "Ganador del municipio",
        CANDIDATOS_ALCALDE_MVD[municipio],
        key="res_mvd_alcalde",
    )
    resultados_reales["Montevideo"]["municipio"] = municipio
    resultados_reales["Montevideo"]["alcalde"] = alcalde_ganador

    if st.button("Guardar Resultados"):
        guardar_json(RESULTADOS_FILE, resultados_reales)
        st.success("✅ Resultados guardados.")


def ver_puntajes():
    st.subheader("🏆 Ranking de Participantes")
    if not resultados_reales:
        st.info("Primero se deben cargar los resultados reales.")
    else:
        ranking = []
        for usuario, pred in predicciones.items():
            puntos = 0
            for dep, datos in pred.items():
                real = resultados_reales.get(dep, {})
                if datos.get("partido") == real.get("partido") and datos.get(
                    "intendente"
                ) == real.get("intendente"):
                    puntos += 1

            # Evaluar predicción de alcalde solo si corresponde
            if "Montevideo" in pred and "municipio" in pred["Montevideo"]:
                pred_muni = pred["Montevideo"]["municipio"]
                pred_agrup = pred["Montevideo"].get("agrupacion_alcalde")
                pred_alcalde = pred["Montevideo"].get("alcalde")

                real_muni = resultados_reales.get("Montevideo", {}).get(
                    "municipio"
                )
                real_agrup = resultados_reales.get("Montevideo", {}).get(
                    "agrupacion_alcalde"
                )
                real_alcalde = resultados_reales.get("Montevideo", {}).get(
                    "alcalde"
                )

                if (
                    pred_muni == real_muni
                    and pred_agrup == real_agrup
                    and pred_alcalde == real_alcalde
                ):
                    puntos += 1  # punto adicional por acierto en municipio

            ranking.append((usuario, puntos))

        ranking.sort(key=lambda x: (-x[1], x[0]))
        for i, (usuario, puntos) in enumerate(ranking, 1):
            st.write(f"{i}. {usuario}: {puntos} puntos")


def ver_mapa():
    mapa_opcion = st.radio(
        "¿Qué querés visualizar?",
        ["Resultados reales", "Predicción de un usuario"],
    )

    if mapa_opcion == "Resultados reales":
        mostrar_mapa_resultados()
    else:
        nombre = st.text_input("Nombre del usuario:")
        if nombre:
            mostrar_mapa_predicciones(nombre)
