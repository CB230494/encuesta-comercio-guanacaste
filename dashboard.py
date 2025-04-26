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
