# === PARTE 1: IMPORTACIONES Y CONFIGURACIÓN GOOGLE SHEETS ===

import streamlit as st
import pandas as pd
from datetime import datetime
import folium
from streamlit_folium import st_folium
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time

# === Función para conectar a Google Sheets ===
def conectar_google_sheets():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        credentials_dict = st.secrets["gcp_service_account"]
        credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
        client = gspread.authorize(credentials)
        sheet = client.open("Encuesta_Comercio_2025").sheet1  # ← Asegúrate que el nombre sea correcto
        return sheet
    except Exception:
        return None

# === INICIALIZAR VARIABLES DE SESIÓN ===
if "ubicacion" not in st.session_state:
    st.session_state.ubicacion = None
if "enviado" not in st.session_state:
    st.session_state.enviado = False

# === CSS personalizado ===
st.markdown("""
    <style>
    /* Forzar modo claro y fondo general */
    html, body, .stApp {
        color-scheme: light !important;
        background-color: #2C517A !important;
        color: #ffffff !important;
        font-weight: bold !important;
    }

    /* Títulos principales */
    h1, h2, h3 {
        color: #FAFEF3;
    }

    /* Encabezado del expander */
   .expander-title {
        background-color: #347A59;
        color: #ffffff;
        font-size: 18px;
        font-weight: bold;
        border-radius: 10px;
        padding: 15px 20px;
        margin-bottom: -20px;
        text-align: left;
    }

    /* Elimina el triángulo predeterminado del expander */
    summary::marker {
        display: none;
    }



    /* Fondo interno de expanders */
    div[data-testid="stExpander"] > div {
        background-color: #ffffff;
        border: 2px solid #ff4b4b;
        border-radius: 12px;
        padding: 10px;
    }

    /* Inputs personalizados */
    .stSelectbox > div, .stRadio > div, .stMultiSelect > div, .stTextArea > div {
        background-color: #51924b;
        border: 2px solid #51924b;
        border-radius: 10px;
        color: #2C517A !important;
        padding: 10px;
    }

    /* Botones */
    .stButton > button {
        background-color: #DF912F;
        color: #ffffff;
        border: none;
        border-radius: 10px;
        padding: 10px 24px;
        font-size: 16px;
    }

    .stButton > button:hover {
        background-color: #DF912F;
        color: white;
    }
    
   /* Corregir fondo y texto seleccionado en RADIO y MULTISELECT */
div[role="radiogroup"] > label[data-selected="true"],
div[role="radiogroup"] > div[data-selected="true"],
div[role="listbox"] > div[data-selected="true"] {
    color: #ffffff !important;
    border-radius: 8px !important;
    font-weight: bold !important;
}
div[role="radiogroup"] label[data-selected="true"]::after,
div[role="listbox"] div[data-selected="true"]::after {
    content: " ✅";
    margin-left: 6px;
}
    /* desplegables */
div[role="radiogroup"] label,
div[role="radiogroup"] label span {
    color: #ffffff !important;
    font-weight: 500 !important;
}
    /* Cambia el color del texto de las preguntas */
label, .stMarkdown p {
    color: #ffffff !important;
    font-weight: 600;
}

    /* Limitar altura del contenedor del mapa en pantallas pequeñas */
@media only screen and (max-width: 768px) {
    iframe {
        height: 300px !important;
        max-height: 300px !important;
    }
}
</style>
""", unsafe_allow_html=True)


from PIL import Image
import streamlit as st

banner = Image.open("baner.png")
st.markdown(
    """
    <style>
    .banner-container img {
        width: 100%;
        max-height: 300px;
        object-fit: contain;
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="banner-container">', unsafe_allow_html=True)
st.image(banner, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)


# === TÍTULO PRINCIPAL ===

st.markdown("""
**Con el objetivo de fortalecer la seguridad en nuestro entorno comercial, nos enfocamos en abordar las principales preocupaciones de seguridad.**
La información que nos suministras es completamente confidencial y se emplea exclusivamente con el propósito de mejorar la seguridad en nuestra área comercial.
""")

# === PARTE 2: DATOS DEMOGRÁFICOS Y MAPA ===
st.markdown("<div class='expander-title'>Datos Demográficos</div>", unsafe_allow_html=True)

with st.expander("", expanded=False):
    distrito = st.selectbox(
        "Distrito:",
        ["", "Tamarindo", "Cabo Velas (Flamingo)", "Tempate"]
    )

    if distrito == "Tamarindo":
        barrio = st.selectbox("Barrio", ["Tamarindo Centro", "Villareal"])
    elif distrito == "Cabo Velas (Flamingo)":
        barrio = st.selectbox("Barrio", ["Flamingo", "Brasilito"])
    elif distrito == "Tempate":
        barrio = st.selectbox("Barrio", ["Surf Side", "Potrero"])
    else:
        barrio = ""

    edad = st.number_input("Edad:", min_value=12, max_value=120, format="%d")
    sexo = st.selectbox("Sexo:", ["","Hombre", "Mujer", "LGBTQ+", "Otro / Prefiero No decirlo"])
    escolaridad = st.selectbox("Escolaridad:", [
        "","Ninguna", "Primaria", "Primaria incompleta", "Secundaria incompleta",
        "Secundaria completa", "Universitaria incompleta", "Universitaria", "Técnico"
    ])
    tipo_local = st.selectbox("Tipo de local comercial:", [
        "Supermercado", "Pulpería / Licorera", "Restaurante / Soda", "Bar",
        "Tienda de artículos", "Gasolineras", "Servicios estéticos",
        "Puesto de lotería", "Otro"
    ])
    st.caption("Nota: Todas las anteriores son selección única.")

    # === MAPA ===
st.markdown("### Seleccione su ubicación en el mapa:")

if "ubicacion" not in st.session_state:
    st.session_state.ubicacion = None

mapa = folium.Map(location=[10.3, -85.8], zoom_start=13)

# Agregar marcador si ya hay una ubicación seleccionada
if st.session_state.ubicacion:
    folium.Marker(
        location=st.session_state.ubicacion,
        tooltip="Ubicación seleccionada",
        icon=folium.Icon(color="blue", icon="map-marker")
    ).add_to(mapa)

# Mostrar el mapa
map_click = st_folium(mapa, width=700, height=500)

# Capturar clic y actualizar ubicación (sin recargar)
if map_click and map_click.get("last_clicked"):
    lat = map_click["last_clicked"]["lat"]
    lon = map_click["last_clicked"]["lng"]
    st.session_state.ubicacion = [lat, lon]


# === PARTE 3: PERCEPCIÓN DE SEGURIDAD ===
st.markdown("<div class='expander-title'>Percepción de Seguridad</div>", unsafe_allow_html=True)
with st.expander("", expanded=False):
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
st.markdown("<div class='expander-title'>Factores de Riesgo Social</div>", unsafe_allow_html=True)
with st.expander("", expanded=False):
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

    falta_de_inversion = st.multiselect(
        "Falta de Inversión Social",
        [
            "Falta de oferta educativa",
            "Falta de oferta deportiva",
            "Falta de oferta recreativa",
            "Falta de actividades culturales"
        ]
    )
    st.caption("Nota: selección múltiple.")

    consumo_drogas = st.multiselect(
        "Consumo de Drogas",
        [
            "Área Privada",
            "Área Pública"
        ]
    )
    st.caption("Nota: selección múltiple.")

    bunker = st.multiselect(
        "Búnker(Sitio de oportunidad)",
        [
            "Casa de habitación",
            "Edificación Abandonada","Lote Baldío","Otro"
        ]
    )
    st.caption("Nota: selección múltiple.")
    
# === PARTE 5: SITUACIONES RELACIONADAS A DELITOS ===
st.markdown("<div class='expander-title'>Situaciones Relacionadas a Delitos</div>", unsafe_allow_html=True)
with st.expander("", expanded=False):
    delitos_zona = st.multiselect(
        "¿Seleccine los delitos que considere que ocurren alrededor de su comercio?",
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
            "Recinto privado"
        ]
    )

    delitos_vida = st.multiselect(
        "Que delitos contra la vida considera que hay en la zona",
        [
            "Homicidios",
            "Heridos"
        ]
    )

    delitos_sexuales = st.multiselect(
        "¿Qué delitos sexuales ha percibido que existen en la zona?",
        [
            "Abuso sexual",
            "Acoso sexual",
            "Violación"
        ]
    )

    asaltos = st.multiselect(
        "¿Qué tipos de asaltos hay en la zona?",
        [
            "Asalto a personas",
            "Asalto a comercio",
            "Asalto a vivienda",
            "Asalto a transporte público"
        ]
    )

    estafas = st.multiselect(
        "¿Qué tipos de estafas ha observado que hay en la zona?",
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
        "¿Qué tipos de robos ha identificado en la zona?",
        [
            "Tacha a comercio",
            "Tacha a edificaciones",
            "Tacha a vivienda",
            "Tacha de vehículos",
            "Robo de vehículos"
        ]
    )
    st.caption("Nota: selección múltiple.")

st.markdown("<div class='expander-title'>Información Adicional</div>", unsafe_allow_html=True)
with st.expander("", expanded=False):
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

        # Validaciones obligatorias
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

            datos = [
                datetime.now().isoformat(),
                distrito,
                barrio,
                edad,
                sexo,
                escolaridad,
                tipo_local,
                ubicacion_url,
                percepcion_seguridad,
                ", ".join(factores_inseguridad) if factores_inseguridad else "",
                ", ".join(factores_sociales) if factores_sociales else "",
                ", ".join(falta_de_inversion) if falta_de_inversion else "",
                ", ".join(consumo_drogas) if consumo_drogas else "",
                ", ".join(bunker) if bunker else "",
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

            sheet = conectar_google_sheets()

            if sheet:
                try:
                    sheet.append_row(datos)
                    st.session_state.enviado = True

                    # ✅ Mensaje de éxito normal
                    st.success("✅ ¡Formulario enviado correctamente!")

                    # ✅ Bloque visual adicional
                    st.markdown("""
                    <div style='background-color:#9DC453; padding: 20px; border-radius: 10px; border: 2px solid #51924B; text-align: center;'>
                        <h2 style='color: #2C517A;'>¡Gracias por completar la encuesta!</h2>
                        <p style='color: #2C517A;'>Tus respuestas han sido registradas exitosamente.</p>
                    </div>
                    """, unsafe_allow_html=True)

                    # ✅ Botón para reiniciar
                    if st.button("📝 Enviar otra respuesta"):
                        st.session_state.enviado = False
                        st.experimental_rerun()

                except Exception:
                    st.error("❌ Hubo un error al guardar los datos. Intente nuevamente.")


st.markdown("<p style='text-align: center; color:#88E145; font-size:10px'>Sembremos Seguridad-2025</p>", unsafe_allow_html=True)


