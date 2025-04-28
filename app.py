# === PARTE 1: IMPORTACIONES Y CONFIGURACIÓN GOOGLE SHEETS ===

import streamlit as st
import pandas as pd
from datetime import datetime
import folium
from streamlit_folium import st_folium
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time

# CSS personalizado
st.markdown(
    """
    <style>
    /* Fondo general */
    .stApp {
        background-color: #0e1117;
    }

    /* Títulos principales */
    h1, h2, h3 {
        color: #3399ff;
    }

    /* Estilo de Expander Headers */
    .streamlit-expanderHeader {
        font-weight: bold;
        background-color: #003366;
        color: white;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 5px;
        font-size: 20px;
    }

    /* Fondo interno de expanders */
    div[data-testid="stExpander"] > div {
        background-color: #1f2228;
        border: 2px solid #ff4b4b;
        border-radius: 12px;
        padding: 10px;
    }

    /* Inputs personalizados (radios, selects, multiselects) */
    .stSelectbox > div, .stRadio > div, .stMultiSelect > div, .stTextArea > div {
        background-color: #1f2228;
        border-radius: 10px;
        color: white;
        padding: 10px;
    }

    /* Botones */
    .stButton > button {
        background-color: #ff4b4b;
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 24px;
        font-size: 16px;
    }
    .stButton > button:hover {
        background-color: #e60000;
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Mostrar logo local


st.markdown(
    """
    <div style="text-align: center; margin-bottom: 10px;">
        <!-- Aquí después pones tu st.image('ruta_logo.png') -->
        <h1 style="color: #3399ff;">Encuesta Comercio 2025 🦜🌴</h1>
    </div>
    """,
    unsafe_allow_html=True
) 



# === TEXTO INICIAL ===
st.title("Encuesta Comercio - Santa Cruz")

st.markdown("""
**Con el objetivo de fortalecer la seguridad en nuestro entorno comercial, nos enfocamos en abordar las principales preocupaciones de seguridad.**
La información que nos suministras es completamente confidencial y se emplea exclusivamente con el propósito de mejorar la seguridad en nuestra área comercial.
""")

# === PARTE 2: DATOS DEMOGRÁFICOS Y MAPA ===

if st.session_state.enviado:
    st.success("✅ ¡Formulario enviado exitosamente!")
    if st.button("Enviar otro formulario"):
        st.session_state.enviado = False
        st.experimental_rerun()
else:
    with st.expander("1️⃣🦜 Datos Demográficos", expanded=True):
        canton = "Santa Cruz"
        distrito = st.selectbox("Distrito:", ["", "Tamarindo", "Cartagena", "Cabo Velas (Flamingo)"])
        edad = st.number_input("Edad:", min_value=12, max_value=120, format="%d")
        sexo = st.radio("Sexo:", ["Hombre", "Mujer", "LGBTQ+", "Otro / Prefiero No decirlo"])
        escolaridad = st.radio("Escolaridad:", [
            "Ninguna", "Primaria", "Primaria incompleta", "Secundaria incompleta",
            "Secundaria completa", "Universitaria incompleta", "Universitaria", "Técnico"
        ])
        tipo_local = st.radio("Tipo de local comercial:", [
            "Supermercado", "Pulpería / Licorera", "Restaurante / Soda", "Bar", 
            "Tienda de artículos", "Gasolineras", "Servicios estéticos", "Puesto de lotería", "Otro"
        ])
        st.caption("Nota: Todas las anteriores son selección única.")

       # === PARTE DEL MAPA EN "DATOS DEMOGRÁFICOS" ===

st.markdown("### Seleccione su ubicación en el mapa:")

# Crear el mapa base solo una vez al cargar
if "mapa" not in st.session_state:
    st.session_state.mapa = folium.Map(location=[10.3, -85.8], zoom_start=13)

# Si ya hay ubicación seleccionada, agregar el marcador
if st.session_state.ubicacion:
    # Limpiar y recrear el mapa para evitar múltiples marcadores
    st.session_state.mapa = folium.Map(location=[10.3, -85.8], zoom_start=13)
    folium.Marker(
        location=st.session_state.ubicacion,
        tooltip="Ubicación seleccionada",
        icon=folium.Icon(color="blue", icon="map-marker")
    ).add_to(st.session_state.mapa)

# Mostrar el mapa (sin recargar toda la página)
map_click = st_folium(st.session_state.mapa, width=700, height=500)

# Si el usuario hace clic en el mapa, capturar nueva ubicación
if map_click and map_click.get("last_clicked"):
    lat = map_click["last_clicked"]["lat"]
    lon = map_click["last_clicked"]["lng"]
    st.session_state.ubicacion = [lat, lon]

# === PARTE 3: PERCEPCIÓN DE SEGURIDAD ===
with st.expander("2️⃣🐒 Percepción de Seguridad"):
    percepcion_seguridad = st.radio(
        "¿Qué tan seguro(a) se siente en esta zona comercial?",
        ["Muy seguro(a)", "Seguro(a)", "Ni seguro(a) Ni inseguro(a)", "Inseguro(a)", "Muy inseguro(a)"]
    )
    st.caption("Nota: respuesta de selección única.")

    factores_inseguridad = []
    if percepcion_seguridad in ["Inseguro(a)", "Muy inseguro(a)"]:
        factores_inseguridad = st.multiselect(
            "¿Por qué se siente inseguro(a)?",
            [
                "Presencia de personas desconocidas o comportamientos inusuales",
                "Poca iluminación en la zona",
                "Escasa presencia policial",
                "Robos frecuentes",
                "Consumo de sustancias en la vía pública",
                "Horarios considerados peligrosos (Entre las 6:00pm y las 5:00am)",
                "Disturbios o riñas cercanas",
                "Otro"
            ]
        )
        st.caption("Nota: selección múltiple.")


# === PARTE 4: FACTORES DE RIESGO SOCIAL ===
with st.expander("3️⃣🐢 Factores de Riesgo Social"):
    factores_sociales = st.multiselect(
        "¿Cuáles de los siguientes factores afectan la seguridad en su zona comercial?",
        [
            "Falta de oportunidades laborales", 
            "Problemas vecinales", 
            "Asentamientos ilegales",
            "Personas en situación de calle", 
            "Zona de prostitución", 
            "Consumo de alcohol en vía pública",
            "Personas con exceso de tiempo de ocio", 
            "Cuarterías", 
            "Lotes baldíos",
            "Ventas informales", 
            "Pérdida de espacios públicos", 
            "Otro"
        ]
    )
    st.caption("Nota: selección múltiple.")
# === PARTE 5: SITUACIONES RELACIONADAS A DELITOS ===
with st.expander("4️⃣🦥 Situaciones Relacionadas a Delitos"):
    delitos_zona = st.multiselect(
        "¿Qué delitos considera que ocurren alrededor de su comercio?",
        [
            "Disturbios en vía pública",
            "Daños a la propiedad",
            "Intimidación o amenazas con fines de lucro",
            "Hurto",
            "Receptación",
            "Contrabando",
            "Otro"
        ]
    )
    st.caption("Nota: selección múltiple.")

    venta_drogas = st.multiselect(
        "¿Dónde ocurre la venta de drogas?",
        [
            "Búnker (espacio cerrado)",
            "Vía pública",
            "Exprés"
        ]
    )

    delitos_vida = st.multiselect(
        "¿Qué delitos contra la vida ha observado?",
        [
            "Homicidios",
            "Heridos"
        ]
    )

    delitos_sexuales = st.multiselect(
        "¿Qué delitos sexuales ha percibido?",
        [
            "Abuso sexual",
            "Acoso sexual",
            "Violación"
        ]
    )

    asaltos = st.multiselect(
        "¿Qué tipos de asaltos considera que ocurren?",
        [
            "Asalto a personas",
            "Asalto a comercio",
            "Asalto a vivienda",
            "Asalto a transporte público"
        ]
    )

    estafas = st.multiselect(
        "¿Qué tipos de estafas ha observado?",
        [
            "Billetes falsos",
            "Documentos falsos",
            "Estafa (Oro)",
            "Lotería falsos",
            "Estafas informáticas",
            "Estafa telefónica",
            "Estafa con tarjetas"
        ]
    )

    robos = st.multiselect(
        "¿Qué tipos de robos ha identificado?",
        [
            "Tacha a comercio",
            "Tacha a edificaciones",
            "Tacha a vivienda",
            "Tacha de vehículos",
            "Robo de vehículos"
        ]
    )
    st.caption("Nota: selección múltiple.")
# === PARTE 6: INFORMACIÓN ADICIONAL ===
# === PARTE 6: INFORMACIÓN ADICIONAL ===
# === PARTE 6: INFORMACIÓN ADICIONAL ===
with st.expander("5️⃣🦎 Información Adicional"):
    st.markdown("""
    **Información adicional**

    Este apartado busca conocer con mayor profundidad la percepción de seguridad en el entorno comercial, identificar situaciones particulares que generan preocupación entre los comerciantes y entender mejor los factores que afectan el desarrollo de su actividad. La información recolectada permitirá orientar acciones preventivas, fortalecer la presencia institucional y fomentar entornos comerciales más seguros y colaborativos.
    """)

    observacion_control = st.radio(
        "¿Ha notado la presencia de personas o grupos que aparentan ejercer control sobre la actividad comercial?",
        [
            "Sí, he observado comportamientos similares",
            "He escuchado comentarios de otros comercios",
            "No",
            "Prefiero no responder"
        ]
    )

    descripcion_control = []
    if observacion_control == "Sí, he observado comportamientos similares":
        descripcion_control = st.multiselect(
            "Describa qué tipo de comportamientos ha observado:",
            [
                "Cobros o 'cuotas' por dejar operar",
                "Personas que vigilan entradas/salidas",
                "Amenazas veladas o directas",
                "Restricciones sobre horarios o actividades",
                "Intermediarios de 'seguridad' no oficiales",
                "Personas ajenas con control territorial",
                "Interferencia constante en operación",
                "Presencia de grupos como 'autorizadores'",
                "Otros"
            ]
        )
        st.caption("Nota: selección múltiple.")

    victima = st.radio(
        "¿Usted o su local comercial han sido víctimas de algún delito en los últimos 12 meses?",
        [
            "Sí, y presenté la denuncia",
            "Sí, pero no presenté la denuncia",
            "No",
            "Prefiero no responder"
        ]
    )

    motivo_no_denuncia = []
    tipo_delito = []
    horario_delito = ""
    modo_operar = []

    if victima == "Sí, pero no presenté la denuncia":
        motivo_no_denuncia = st.multiselect(
            "¿Por qué no presentó la denuncia?",
            [
                "Distancia (falta de oficinas para recepción de denuncias)",
                "Miedo a represalias",
                "Falta de respuesta oportuna",
                "He realizado denuncias y no ha pasado nada",
                "Complejidad al colocar la denuncia",
                "Desconocimiento de dónde colocar la denuncia",
                "El Policía me dijo que era mejor no denunciar",
                "Falta de tiempo para colocar la denuncia"
            ]
        )
        st.caption("Nota: selección múltiple.")
    elif victima == "Sí, y presenté la denuncia":
        tipo_delito = st.multiselect(
            "¿Cuál fue el delito del que fue víctima?",
            [
                "Hurto", "Asalto", "Cobro por protección", "Estafa",
                "Daños a la propiedad", "Venta o consumo de drogas",
                "Amenazas", "Cobros periódicos o 'cuotas'", "Otro"
            ]
        )
        st.caption("Nota: puede marcar más de una opción.")

    # SOLO si fue víctima mostrar horario y modo de operar
    if victima in ["Sí, y presenté la denuncia", "Sí, pero no presenté la denuncia"]:
        horario_delito = st.selectbox(
            "¿Conoce el horario en el que ocurrió el hecho delictivo?",
            [
                "", 
                "00:00 - 02:59 a.m.", "03:00 - 05:59 a.m.", "06:00 - 08:59 a.m.",
                "09:00 - 11:59 a.m.", "12:00 - 14:59 p.m.", "15:00 - 17:59 p.m.",
                "18:00 - 20:59 p.m.", "21:00 - 23:59 p.m.", "Desconocido"
            ]
        )

        modo_operar = st.multiselect(
            "¿Cómo operaban los responsables?",
            [
                "Arma blanca", "Arma de fuego", "Amenazas",
                "Cobros o 'cuotas' por dejar operar", "Arrebato",
                "Boquete", "Ganzúa", "Engaño", "No sé", "Otro"
            ]
        )
        st.caption("Nota: selección múltiple.")

    # Continua normal para todos
    exigencia_cuota = st.radio(
        "¿Ha recibido su local comercial algún tipo de exigencia económica o cuota obligatoria?",
        ["Sí", "No", "Prefiero no responder"]
    )

    descripcion_cuota = ""
    if exigencia_cuota == "Sí":
        descripcion_cuota = st.text_area(
            "Detalle cómo ocurrió (frecuencia, forma de contacto, tipo de exigencia):"
        )

    opinion_fp = st.radio(
        "¿Cómo califica el servicio policial de la Fuerza Pública cerca de su local?",
        ["Excelente", "Bueno", "Regular", "Mala", "Muy mala"]
    )

    cambio_servicio = st.radio(
        "¿Cómo ha cambiado el servicio en los últimos 12 meses?",
        ["Ha mejorado mucho", "Ha mejorado", "Igual", "Ha empeorado", "Ha empeorado mucho"]
    )

    conocimiento_policias = st.radio(
        "¿Conoce a los policías de Fuerza Pública o Policía Turística que patrullan su zona comercial?",
        ["Sí", "No"]
    )

    participacion_programa = st.radio(
        "¿Conoce o participa en el Programa de Seguridad Comercial impulsado por Fuerza Pública?",
        [
            "No lo conozco",
            "Lo conozco, pero no participo",
            "Lo conozco y participo activamente",
            "No lo conozco, pero me gustaría participar",
            "Prefiero no responder"
        ]
    )

    deseo_participar = ""
    if participacion_programa in [
        "No lo conozco", "Lo conozco, pero no participo", "No lo conozco, pero me gustaría participar"
    ]:
        deseo_participar = st.text_area(
            "Si desea ser contactado para formar parte del programa, indique nombre del comercio, correo electrónico y número de teléfono:"
        )

    medidas_fp = st.text_area(
        "¿Qué medidas considera importantes que implemente la Fuerza Pública para mejorar la seguridad en su zona comercial?"
    )

    medidas_muni = st.text_area(
        "¿Qué medidas considera necesarias por parte de la Municipalidad para mejorar la seguridad en su zona comercial?"
    )

    info_adicional = st.text_area(
        "¿Desea agregar alguna otra información que considere pertinente?"
    )


# === PARTE 7: ENVÍO Y GUARDADO DE RESPUESTAS ===
if not st.session_state.enviado:
    if st.button("Enviar formulario"):
        errores = []

        # Validaciones básicas
        if not st.session_state.ubicacion:
            errores.append("Ubicación en el mapa")
        if not distrito:
            errores.append("Distrito")
        if not sexo:
            errores.append("Sexo")
        if not escolaridad:
            errores.append("Escolaridad")
        if not tipo_local:
            errores.append("Tipo de local comercial")
        if not percepcion_seguridad:
            errores.append("Percepción de seguridad")
        if not victima:
            errores.append("Victimización")
        if not horario_delito:
            errores.append("Horario del hecho")
        if not exigencia_cuota:
            errores.append("Exigencia de cuota")
        if not opinion_fp:
            errores.append("Opinión sobre Fuerza Pública")
        if not cambio_servicio:
            errores.append("Cambio de servicio policial")
        if not conocimiento_policias:
            errores.append("Conocimiento de policías")
        if not participacion_programa:
            errores.append("Participación en programa")

        if errores:
            st.error("⚠️ Faltan los siguientes campos obligatorios: " + ", ".join(errores))
        else:
            lat, lon = st.session_state.ubicacion
            ubicacion_url = f"https://www.google.com/maps?q={lat},{lon}"

            # Preparar fila de datos
            datos = [
                datetime.now().isoformat(),
                canton,
                distrito,
                edad,
                sexo,
                escolaridad,
                tipo_local,
                ubicacion_url,
                percepcion_seguridad,
                ", ".join(factores_inseguridad) if factores_inseguridad else "",
                ", ".join(factores_sociales) if factores_sociales else "",
                "",  # Inversión social (lo puedes agregar si quieres aquí en estructura)
                "",  # Consumo de drogas
                "",  # Búnkers
                ", ".join(delitos_zona) if delitos_zona else "",
                ", ".join(venta_drogas) if venta_drogas else "",
                ", ".join(delitos_vida) if delitos_vida else "",
                ", ".join(delitos_sexuales) if delitos_sexuales else "",
                ", ".join(asaltos) if asaltos else "",
                ", ".join(estafas) if estafas else "",
                ", ".join(robos) if robos else "",
                observacion_control,
                ", ".join(descripcion_control) if descripcion_control else "",
                victima,
                ", ".join(motivo_no_denuncia) if motivo_no_denuncia else "",
                ", ".join(tipo_delito) if tipo_delito else "",
                horario_delito,
                ", ".join(modo_operar) if modo_operar else "",
                exigencia_cuota,
                descripcion_cuota,
                opinion_fp,
                cambio_servicio,
                conocimiento_policias,
                participacion_programa,
                deseo_participar,
                medidas_fp,
                medidas_muni,
                info_adicional
            ]

            # Guardar en Google Sheets
            sheet = conectar_google_sheets()
            if sheet:
                try:
                    sheet.append_row(datos)
                    st.session_state.enviado = True
                    st.success("✅ ¡Formulario enviado correctamente!")
                    st.experimental_rerun()
                except Exception:
                    st.error("❌ Error al guardar la respuesta. Intente de nuevo.")
else:
    st.success("✅ ¡Formulario enviado correctamente!")
    if st.button("Enviar otro formulario"):
        st.session_state.enviado = False
        st.experimental_rerun()


