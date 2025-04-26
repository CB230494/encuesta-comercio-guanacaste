import streamlit as st
import pandas as pd
from datetime import datetime
import folium
from streamlit_folium import st_folium
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# === CONFIGURACIÓN GOOGLE SHEETS ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_dict(
    st.secrets["gcp_service_account"], scope
)

try:
    client = gspread.authorize(creds)
    sheet = client.open("Encuesta_Comercio_2025").worksheet("Respuestas")
except Exception:
    st.error("❌ No se pudo acceder a la hoja de cálculo. Verifica nombre, hoja y permisos.")
    st.stop()

# === ESTADO PARA UBICACIÓN ===
if "ubicacion" not in st.session_state:
    st.session_state.ubicacion = None

# === FORMULARIO ===
st.title("Encuesta Comercio - Guanacaste")

canton = "Santa Cruz"
distrito = st.selectbox("Distrito", ["Tamarindo", "Cartagena", "Cabo Velas"])
edad = st.number_input("Edad", min_value=12, max_value=120, format="%d")
sexo = st.radio("Sexo", ["Hombre", "Mujer", "LGBTQ+", "Otro / Prefiero no decirlo"])
escolaridad = st.selectbox("Escolaridad", [
    "Ninguna", "Primaria", "Primaria incompleta", "Secundaria incompleta", 
    "Secundaria completa", "Universitaria incompleta", "Universitaria", "Técnico"
])
tipo_local = st.selectbox("Tipo de local", [
    "Supermercado", "Pulpería / Licorera", "Restaurante / Soda", "Bar",
    "Tienda de artículos", "Gasolineras", "Servicios estéticos", "Puesto de lotería", "Otro"
])

# === MAPA DINÁMICO ===
st.markdown("### Haga clic en el mapa para seleccionar o cambiar su ubicación:")

mapa = folium.Map(location=[10.3, -85.8], zoom_start=13)

# Mostrar pin si ya se ha hecho clic
if st.session_state.ubicacion:
    folium.Marker(
        location=st.session_state.ubicacion,
        tooltip="Ubicación seleccionada",
        icon=folium.Icon(color="blue", icon="map-marker")
    ).add_to(mapa)

# Mostrar el mapa e interpretar clic
map_click = st_folium(mapa, width=700, height=500)

# Si hay nuevo clic, actualizar la ubicación
if map_click and map_click.get("last_clicked"):
    lat = map_click["last_clicked"]["lat"]
    lon = map_click["last_clicked"]["lng"]
    st.session_state.ubicacion = [lat, lon]

# === BOTÓN DE ENVÍO ===
if st.button("Enviar"):
    errores = []

    # Verificar cada campo
    if not edad:
        errores.append("Edad")
    if not distrito:
        errores.append("Distrito")
    if not sexo:
        errores.append("Sexo")
    if not escolaridad:
        errores.append("Escolaridad")
    if not tipo_local:
        errores.append("Tipo de local")
    if not st.session_state.ubicacion:
        errores.append("Ubicación en el mapa")

    if errores:
        st.error("⚠️ Faltan los siguientes campos obligatorios: " + ", ".join(errores))
    else:
        lat, lon = st.session_state.ubicacion
        ubicacion_url = f"https://www.google.com/maps?q={lat},{lon}"

        datos = [
            datetime.now().isoformat(),
            canton,
            distrito,
            edad,
            sexo,
            escolaridad,
            tipo_local,
            ubicacion_url
        ]

        try:
            sheet.append_row(datos)
            st.success("✅ Respuesta enviada correctamente.")
            # Reiniciar formulario
            st.session_state.ubicacion = None
        except Exception as e:
            st.error("❌ Error al guardar la respuesta. Intente de nuevo.")

