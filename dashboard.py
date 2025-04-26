import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import folium
from streamlit_folium import st_folium

# === CONFIGURACIÓN GOOGLE SHEETS ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_dict(
    st.secrets["gcp_service_account"], scope
)

# === CARGAR DATOS CON CACHE PARA EVITAR RECARGAS POR INTERACCIÓN ===
@st.cache_data(ttl=300)
def cargar_datos():
    client = gspread.authorize(creds)
    sheet = client.open("Encuesta_Comercio_2025").worksheet("Respuestas")
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    return df

# === INICIO DEL DASHBOARD ===
st.set_page_config(page_title="Dashboard Comercio Guanacaste", layout="wide")
st.title("📊 Dashboard Encuesta Comercio - Guanacaste")

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

    # === PERCEPCIÓN DE SEGURIDAD ===
    if "Percepción de seguridad" in df.columns:
        st.subheader("Percepción de Seguridad")
        fig1 = px.pie(
            df,
            names="Percepción de seguridad",
            title="Percepción de Seguridad",
            hole=0.4
        )
        st.plotly_chart(fig1, use_container_width=True)

    # === FACTORES DE INSEGURIDAD ===
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

    # === TIPOS DE DELITOS REPORTADOS ===
    if "Tipo de delito" in df.columns:
        st.subheader("Tipos de Delitos Reportados")
        delitos = df["Tipo de delito"].dropna().str.split(", ")
        delitos_flat = [item for sublist in delitos for item in sublist]
        delitos_df = pd.DataFrame(delitos_flat, columns=["Delito"])
        if not delitos_df.empty:
            fig3 = px.histogram(
                delitos_df,
                x="Delito",
                title="Frecuencia de Tipos de Delito",
                color_discrete_sequence=["darkblue"]
            )
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("No hay datos suficientes de delitos aún.")

    # === VICTIMIZACIÓN ===
    if "Victimización" in df.columns:
        st.subheader("Victimización Comercial")
        fig4 = px.pie(
            df,
            names="Victimización",
            title="¿Han sido víctimas de delitos?",
            hole=0.5
        )
        st.plotly_chart(fig4, use_container_width=True)

    # === MODO DE OPERAR DELICTIVO ===
    if "Modo de operar delictivo" in df.columns:
        st.subheader("Modos de Operar Delictivo Observados")
        modos = df["Modo de operar delictivo"].dropna().str.split(", ")
        modos_flat = [item for sublist in modos for item in sublist]
        modos_df = pd.DataFrame(modos_flat, columns=["Modo"])
        if not modos_df.empty:
            fig5 = px.bar(
                modos_df.value_counts().reset_index(),
                x="Modo",
                y="count",
                labels={"count": "Cantidad"},
                title="Modos de Operar Delictivo"
            )
            st.plotly_chart(fig5, use_container_width=True)
        else:
            st.info("No hay datos suficientes sobre modos de operar.")

    # === HORARIOS DE DELITOS ===
    if "Horario del hecho" in df.columns:
        st.subheader("Horarios en los que ocurren más delitos")
        horario_df = df["Horario del hecho"].dropna()
        if not horario_df.empty:
            horario_df = horario_df.value_counts().reset_index()
            horario_df.columns = ["Horario", "Cantidad"]
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

    # === MAPA DE UBICACIONES CON COLORES POR DISTRITO ===
    st.subheader("Ubicaciones de Formularios Registrados")

    def extraer_lat_lon(url):
        try:
            if pd.notna(url) and "maps?q=" in url:
                coords = url.split("maps?q=")[-1].split(",")
                lat = float(coords[0])
                lon = float(coords[1])
                return lat, lon
        except:
            return None, None

    if "Ubicación (enlace)" in df.columns and not df["Ubicación (enlace)"].dropna().empty:
        ubicaciones = df["Ubicación (enlace)"].apply(lambda x: extraer_lat_lon(x))
        distritos_mapa = df["Distrito"]

        m = folium.Map(location=[10.3, -85.8], zoom_start=11)

        colores_distrito = {
            "Tamarindo": "blue",
            "Cartagena": "green",
            "Cabo Velas": "red"
        }

        for (ubicacion, distrito) in zip(ubicaciones, distritos_mapa):
            if ubicacion and ubicacion[0] is not None:
                color_pin = colores_distrito.get(distrito, "gray")
                folium.Marker(
                    location=[ubicacion[0], ubicacion[1]],
                    tooltip=distrito,
                    icon=folium.Icon(color=color_pin)
                ).add_to(m)

        st_folium(m, width=800, height=500)
    else:
        st.info("No hay ubicaciones registradas aún en los formularios.")
