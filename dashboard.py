# === DASHBOARD STREAMLIT: Análisis de Formularios ===

import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# === CONFIGURACIÓN GOOGLE SHEETS ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_dict(
    st.secrets["gcp_service_account"], scope
)

# === FUNCIÓN PARA CARGAR DATOS DE GOOGLE SHEETS ===
def cargar_datos():
    client = gspread.authorize(creds)
    sheet = client.open("Encuesta_Comercio_2025").worksheet("Respuestas")
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    return df

# === INICIO DEL DASHBOARD ===
st.set_page_config(page_title="Dashboard Comercio Guanacaste", layout="wide")
st.title("📊 Dashboard Encuesta Comercio - Guanacaste")

# Cargar datos
df = cargar_datos()

if df.empty:
    st.warning("Aún no hay datos registrados.")
else:
    # === FILTRO POR DISTRITO ===
    st.sidebar.header("Filtros")
    distritos = df["Distrito"].unique().tolist()
    distrito_seleccionado = st.sidebar.selectbox("Seleccione un distrito:", ["Todos"] + distritos)

    if distrito_seleccionado != "Todos":
        df = df[df["Distrito"] == distrito_seleccionado]

    # === MÉTRICAS ===
    st.metric("📋 Total de Formularios Recibidos", len(df))

    # === GRÁFICA DE PERCEPCIÓN DE SEGURIDAD ===
    if "Percepción de seguridad" in df.columns:
        st.subheader("Percepción de Seguridad")
        fig1 = px.pie(
            df,
            names="Percepción de seguridad",
            title="Percepción de Seguridad",
            hole=0.4
        )
        st.plotly_chart(fig1, use_container_width=True)

    # === GRÁFICA DE FACTORES DE INSEGURIDAD ===
    if "Factores de inseguridad (selección múltiple)" in df.columns:
        st.subheader("Factores de Inseguridad Reportados")
        factores = df["Factores de inseguridad (selección múltiple)"].dropna().str.split(", ")
        factores_flat = [item for sublist in factores for item in sublist]
        factores_df = pd.DataFrame(factores_flat, columns=["Factor"])
        fig2 = px.histogram(
            factores_df,
            x="Factor",
            title="Factores de Inseguridad",
            color_discrete_sequence=["indianred"]
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("No se encuentra la columna de 'Factores de inseguridad' en los datos.")
# === HORARIO DE HECHOS DELICTIVOS ===
if "¿Conoce el horario en el que ocurrió el hecho delictivo?" in df.columns:
    st.subheader("Horarios en los que ocurren más delitos")

    horario_df = df["¿Conoce el horario en el que ocurrió el hecho delictivo>"].dropna()

    if not horario_df.empty:
        horario_df = horario_df.value_counts().reset_index()
        horario_df.columns = ["Horario", "Cantidad"]

        # Orden manual para que los horarios estén en secuencia lógica
        orden_horarios = [
            "00:00 - 02:59 a.m.", "03:00 - 05:59 a.m.", "06:00 - 08:59 a.m.",
            "09:00 - 11:59 a.m.", "12:00 - 14:59 p.m.", "15:00 - 17:59 p.m.",
            "18:00 - 20:59 p.m.", "21:00 - 23:59 p.m.", "Desconocido"
        ]
        horario_df["Horario"] = pd.Categorical(horario_df["Horario"], categories=orden_horarios, ordered=True)
        horario_df = horario_df.sort_values("Horario")

        fig6 = px.line(
            horario_df,
            x="Horario",
            y="Cantidad",
            markers=True,
            title="Frecuencia de delitos por horario",
            labels={"Cantidad": "Cantidad de delitos", "Horario": "Rango horario"}
        )
        st.plotly_chart(fig6, use_container_width=True)
    else:
        st.info("No hay datos suficientes sobre horarios.")
# === MAPA DE UBICACIONES DE RESPUESTAS ===
import folium
from streamlit_folium import st_folium

st.subheader("Ubicaciones de Formularios Registrados")

# Extraer latitud y longitud desde el enlace
def extraer_lat_lon(url):
    try:
        if pd.notna(url) and "maps?q=" in url:
            coords = url.split("maps?q=")[-1].split(",")
            lat = float(coords[0])
            lon = float(coords[1])
            return lat, lon
    except:
        return None, None

# Aplicar extracción
ubicaciones = df["Link ubicación"].apply(lambda x: extraer_lat_lon(x))

# Crear mapa base
m = folium.Map(location=[10.3, -85.8], zoom_start=11)

# Agregar marcadores
for ubicacion in ubicaciones:
    if ubicacion and ubicacion[0] is not None:
        folium.Marker(location=[ubicacion[0], ubicacion[1]], icon=folium.Icon(color="blue")).add_to(m)

# Mostrar mapa
st_folium(m, width=800, height=500)
