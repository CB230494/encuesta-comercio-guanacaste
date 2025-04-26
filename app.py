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

# === MAPA INTERACTIVO CON PIN VISIBLE ===
st.markdown("### Seleccione su ubicación en el mapa (haga clic):")

# Coordenadas por defecto (centro en Guanacaste)
lat_default = 10.3
lon_default = -85.8

# Capturar clic
map_click = st_folium(
    folium.Map(location=[lat_default, lon_default], zoom_start=13),
    width=700, height=500
)

ubicacion_url = None

# Si el usuario hace clic, se genera nuevo mapa con pin
if map_click and map_click.get("last_clicked"):
    lat = map_click["last_clicked"]["lat"]
    lon = map_click["last_clicked"]["lng"]
    ubicacion_url = f"https://www.google.com/maps?q={lat},{lon}"

    # Redibujar mapa con el pin visible
    mapa = folium.Map(location=[lat, lon], zoom_start=16)
    folium.Marker(
        location=[lat, lon],
        tooltip="Ubicación seleccionada",
        icon=folium.Icon(color="blue", icon="map-marker")
    ).add_to(mapa)

    st.markdown("### Pin seleccionado:")
    st_folium(mapa, width=700, height=500)

# === BOTÓN DE ENVÍO ===
if st.button("Enviar"):
    if not ubicacion_url:
        st.warning("Debes hacer clic en el mapa para seleccionar tu ubicación.")
    else:
        datos = [datetime.now().isoformat(), canton, distrito, edad, sexo, escolaridad, tipo_local, ubicacion_url]
        sheet.append_row(datos)
        st.success("¡Gracias! Tu respuesta fue registrada.")


