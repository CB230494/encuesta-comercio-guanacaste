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

client = gspread.authorize(creds)
sheet = client.open("Encuesta_Comercio_2025").worksheet("Respuestas")

# === FORMULARIO ===
st.title("Encuesta Comercio - Guanacaste")

canton = "Santa Cruz"
distrito = st.selectbox("Distrito", ["Tamarindo", "Cartagena", "Cabo Velas"])
edad = st.number_input("Edad", min_value=12, max_value=120)
sexo = st.radio("Sexo", ["Hombre", "Mujer", "LGBTQ+", "Otro / Prefiero no decirlo"])
escolaridad = st.selectbox("Escolaridad", [
    "Ninguna", "Primaria", "Primaria incompleta", "Secundaria incompleta", 
    "Secundaria completa", "Universitaria incompleta", "Universitaria", "Técnico"
])
tipo_local = st.selectbox("Tipo de local", [
    "Supermercado", "Pulpería / Licorera", "Restaurante / Soda", "Bar",
    "Tienda de artículos", "Gasolineras", "Servicios estéticos", "Puesto de lotería", "Otro"
])

# === MAPA ÚNICO CON PIN DINÁMICO ===
st.markdown("### Seleccione su ubicación en el mapa (haga clic):")

# Coordenadas base
center_lat, center_lon = 10.3, -85.8

# Detectar clic anterior guardado en estado
if "ubicacion" not in st.session_state:
    st.session_state.ubicacion = None

# Crear mapa inicial
m = folium.Map(location=[center_lat, center_lon], zoom_start=13)

# Si ya se ha hecho clic, agregar pin
if st.session_state.ubicacion:
    folium.Marker(
        location=st.session_state.ubicacion,
        tooltip="Ubicación seleccionada",
        icon=folium.Icon(color="blue", icon="map-marker")
    ).add_to(m)
else:
    # Mostrar mensaje si aún no hay selección
    st.caption("Haz clic en el mapa para seleccionar la ubicación.")

# Mostrar mapa y capturar clic
map_data = st_folium(m, width=700, height=500)

# Actualizar estado con nuevo clic
if map_data and map_data.get("last_clicked"):
    lat = map_data["last_clicked"]["lat"]
    lon = map_data["last_clicked"]["lng"]
    st.session_state.ubicacion = [lat, lon]
    ubicacion_url = f"https://www.google.com/maps?q={lat},{lon}"
else:
    ubicacion_url = None
    if st.session_state.ubicacion:
        lat, lon = st.session_state.ubicacion
        ubicacion_url = f"https://www.google.com/maps?q={lat},{lon}"

# === BOTÓN DE ENVÍO ===
if st.button("Enviar"):
    if not ubicacion_url:
        st.warning("Debes hacer clic en el mapa para seleccionar tu ubicación.")
    else:
        datos = [datetime.now().isoformat(), canton, distrito, edad, sexo, escolaridad, tipo_local, ubicacion_url]
        sheet.append_row(datos)
        st.success("¡Gracias! Tu respuesta fue registrada.")
        st.session_state.ubicacion = None  # Reiniciar después del envío



