import streamlit as st
import pandas as pd
from datetime import datetime
import folium
from streamlit_folium import st_folium
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# === CONFIGURACIÓN DE GOOGLE SHEETS ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Leer credenciales desde st.secrets (Streamlit Cloud)
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

# === MAPA INTERACTIVO ===
st.markdown("### Seleccione su ubicación en el mapa (haga clic):")

m = folium.Map(location=[10.3, -85.8], zoom_start=11)
map_data = st_folium(m, width=700, height=500)

if map_data and map_data.get("last_clicked"):
    lat = map_data["last_clicked"]["lat"]
    lon = map_data["last_clicked"]["lng"]
    ubicacion_url = f"https://www.google.com/maps?q={lat},{lon}"
else:
    ubicacion_url = None

# === BOTÓN DE ENVÍO ===
if st.button("Enviar"):
    if not ubicacion_url:
        st.warning("Debes hacer clic en el mapa para seleccionar tu ubicación.")
    else:
        datos = [datetime.now().isoformat(), canton, distrito, edad, sexo, escolaridad, tipo_local, ubicacion_url]
        sheet.append_row(datos)
        st.success("¡Gracias! Tu respuesta fue registrada con éxito.")
