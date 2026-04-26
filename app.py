import streamlit as st
import pandas as pd
import plotly.express as px
from rapidfuzz import process, fuzz
import Funciones as f
from openai import OpenAI



# =========================================================
# CONFIGURACIÓN
# =========================================================
st.set_page_config(page_title="Energy Dashboard", layout="wide")


# =========================================================
# CARGA DE DATOS
# =========================================================
@st.cache_data
def load_basic_info():
    df = pd.read_csv("basic_information.csv")
    df.columns = df.columns.str.strip()
    return df


df_basic = load_basic_info()


# =========================================================
# ESTADO
# =========================================================
if "pagina_actual" not in st.session_state:
    st.session_state.pagina_actual = "busqueda"

if "datos_busqueda" not in st.session_state:
    st.session_state.datos_busqueda = None


# =========================================================
# HELPERS
# =========================================================
def obtener_consejos_chatgpt(data, data_predictions, data_fuels):
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

    prompt = f"""
    You are an expert building energy efficiency consultant.

    Based ONLY on the following building data, generate exactly 5 concrete improvement recommendations.
    The recommendations must be practical, specific, and related to emissions, penalties,
    fuels, ENERGY STAR, and regulatory compliance.

    Building data:
    - Name: {data.get("Property Name", "N/A")}
    - Address: {data.get("address", data.get("Address 1", "N/A"))}
    - Status: {data.get("status", "N/A")}
    - Ranking: {data.get("ranking", "N/A")}
    - Year: {data.get("Calendar Year", "N/A")}
    - Calculated emissions: {data.get("Emisiones Calculadas", "N/A")}
    - Emissions limit: {data.get("Limite", "N/A")}
    - Excess emissions: {data.get("Exceso", "N/A")}
    - Difference: {data.get("Diferencia", "N/A")}
    - Relative to limit: {data.get("Relativo", "N/A")}
    - Current penalty: {data.get("multa", "N/A")}
    - Estimated penalty 2030: {data_predictions.get("multa 2030", "N/A")}
    - Estimated penalty 2035: {data_predictions.get("multa 2035", "N/A")}
    - Estimated penalty 2040: {data_predictions.get("multa 2040", "N/A")}
    - ENERGY STAR Score: {data.get("ENERGY STAR Score", "N/A")}
    - Electricity: {data_fuels.get("Electricity", "N/A")}
    - Natural Gas: {data_fuels.get("Natural Gas", "N/A")}
    - Other fuels: {data_fuels.get("Others", "N/A")}
    - Fuel Oil: {data_fuels.get("Fuel Oil", "N/A")}

    The recommendations must include:
    - expected impact on emissions (% or qualitative)
    - relation to penalties reduction
    - level of investment (low, medium, high)
    - implementation difficulty

    Return the answer in English, as a numbered list from 1 to 5.
    Do not invent data. If any data is missing, use what is available.
    """

    respuesta = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert in building energy efficiency and decarbonization."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4
    )

    return respuesta.choices[0].message.content


def normalizar_texto(s):
    s = str(s).lower().strip()
    s = s.replace("avenue", "ave")
    s = s.replace("street", "st")
    s = s.replace("road", "rd")
    s = s.replace("boulevard", "blvd")
    return s


def to_float(value, default=0.0):
    try:
        if pd.isna(value):
            return default
        return float(value)
    except Exception:
        return default


def to_int(value, default=0):
    try:
        if pd.isna(value):
            return default
        return int(float(value))
    except Exception:
        return default


def format_money(value):
    return f"${to_int(value):,}"


def format_percent(value):
    return f"{round(to_float(value) * 100, 2)}%"


def status_a_texto(status_raw):
    valor = str(status_raw).strip().lower()
    if valor == "true":
        return "Compliant", "green"
    elif valor == "false":
        return "Non-Compliant", "red"
    return "N/A", "gray"


def asegurar_serie(resultado):
    """
    Convierte el resultado a una sola fila (pd.Series).
    Soporta:
    - pd.Series
    - pd.DataFrame de 1+ filas
    - dict
    """
    if resultado is None:
        return None

    if isinstance(resultado, pd.Series):
        return resultado

    if isinstance(resultado, pd.DataFrame):
        if resultado.empty:
            return None
        return resultado.iloc[0]

    if isinstance(resultado, dict):
        return pd.Series(resultado)

    return None


# =========================================================
# BÚSQUEDA
# =========================================================
def buscar_direcciones_similares(direccion, n=5):
    columna1 = "address"
    columna2 = "Address 1"

    if not direccion or not str(direccion).strip():
        return None

    if columna1 not in df_basic.columns or columna2 not in df_basic.columns:
        st.error(f"No encuentro las columnas '{columna1}' y/o '{columna2}' en basic_information.csv")
        return None

    direcciones1 = df_basic[columna1].fillna("").astype(str).tolist()
    direcciones2 = df_basic[columna2].fillna("").astype(str).tolist()

    direcciones1_norm = [normalizar_texto(d) for d in direcciones1]
    direcciones2_norm = [normalizar_texto(d) for d in direcciones2]
    direccion_norm = normalizar_texto(direccion)

    resultados1 = process.extract(
        direccion_norm,
        direcciones1_norm,
        scorer=fuzz.WRatio,
        limit=n
    )

    resultados2 = process.extract(
        direccion_norm,
        direcciones2_norm,
        scorer=fuzz.WRatio,
        limit=n
    )

    if not resultados1 and not resultados2:
        return None

    mejor1 = resultados1[0] if resultados1 else ("", -1, None)
    mejor2 = resultados2[0] if resultados2 else ("", -1, None)

    score1 = mejor1[1]
    idx1 = mejor1[2]

    score2 = mejor2[1]
    idx2 = mejor2[2]

    if score1 >= score2 and idx1 is not None:
        idx_final = idx1
    elif idx2 is not None:
        idx_final = idx2
    else:
        return None

    bbl = df_basic["BBL"].iloc[idx_final]

    # Usa tu función actual para traer la información final
    resultado = f.display_information(2024, bbl)

    # Normalizamos el resultado a una sola fila
    data = asegurar_serie(resultado)

    # Fallback por si display_information devuelve algo incompleto
    if data is None:
        data = df_basic.iloc[idx_final]

    return data



# =========================================================
# PÁGINA DE BÚSQUEDA
# =========================================================
if st.session_state.pagina_actual == "busqueda":

    st.title("🔍 Energy Search")

    query = st.text_input(
        "Busca una dirección o edificio:",
        placeholder="Ej: 123 Main St"
    )

    if st.button("Analizar Edificio"):

        resultado = buscar_direcciones_similares(query)
        resultado_bbl = resultado["BBL"] 
        predicciones = f.display_predictions(2024, resultado_bbl)
        fuels_info = f.display_fuels(2024, resultado_bbl)


        if resultado is not None:
            st.session_state.datos_busqueda = resultado
            st.session_state.predicciones = predicciones
            st.session_state.fuels_info = fuels_info
            st.session_state.pagina_actual = "dashboard"
            st.rerun()
        else:
            st.error("No se encontró el edificio.")


# =========================================================
# DASHBOARD
# =========================================================
elif st.session_state.pagina_actual == "dashboard":

    data = asegurar_serie(st.session_state.datos_busqueda)
    data_predictions = asegurar_serie(st.session_state.predicciones)
    data_fuels = asegurar_serie(st.session_state.fuels_info)

    if data is None:
        st.error("No hay datos para mostrar.")
        if st.button("⬅️ Volver a búsqueda"):
            st.session_state.pagina_actual = "busqueda"
            st.rerun()
        st.stop()

    if st.button("⬅️ Nueva Búsqueda"):
        st.session_state.pagina_actual = "busqueda"
        st.session_state.datos_busqueda = None
        st.rerun()

    # -------- Header --------
    property_name = data.get("Property Name", "N/A")
    address = data.get("address", data.get("Address 1", "N/A"))
    ranking = data.get("ranking", "N/A")
    year = data.get("Calendar Year", "N/A")

    status_text, status_color = status_a_texto(data.get("status", None))

    st.title(str(property_name))
    st.caption(str(address))

    st.markdown(
        f"""
        **Ranking:** {ranking}  
        **Status:** :{status_color}[{status_text}]  
        **Año:** {year}
        """
    )

    st.divider()

    # -------- Datos numéricos --------
    
    #multa info
    multa = to_float(data.get("multa", 0))
    multa_2030 = to_float(data_predictions.get("multa 2030", 0))
    multa_2035 = to_float(data_predictions.get("multa 2035", 0))
    multa_2040 = to_float(data_predictions.get("multa 2040", 0))
    #Resumen Info
    relativo = to_float(data.get("Relativo", 0))
    emisiones = to_float(data.get("Emisiones Calculadas", 0))
    limite = to_float(data.get("Limite", 0))
    exceso = to_float(data.get("Exceso", 0))
    diferencia = to_float(data.get("Diferencia", 0))
    energy_star = data.get("ENERGY STAR Score", "N/A")
    emisiones_dob = data.get("Emisiones DOB_y", data.get("Emisiones DOB_x", "N/A"))
    #Fuels info
    electricity = to_float(data_fuels.get("Electricity", 0))
    natural_gas = to_float(data_fuels.get("Natural Gas", 0))
    others = to_float(data_fuels.get("Others", 0))
    oil = to_float(data_fuels.get("Fuel Oil", 0))

    col1, col2 = st.columns([1, 1.5], gap="large")

    with col1:
        st.metric(
            label="Emissions over limit",
            value=format_percent(relativo),
            delta="Exceeded" if relativo > 0 else "Below limit",
            delta_color="inverse"
        )

        st.metric(
            label="Annual Penalty ($)",
            value=format_money(multa)
        )

        st.metric(
            label="ENERGY STAR Score",
            value=energy_star if pd.notna(energy_star) else "N/A"
        )
        
        
        st.write("### Forecast penalty")

       # Data NUMÉRICA (importante: sin format_money aquí)
        df_forecast = pd.DataFrame({
              "Year": [2024, 2030, 2035, 2040],
              "Penalty": [
                        multa,
                        multa_2030,
                        multa_2035,
                        multa_2040
                                  ]
                })

       # Gráfico de línea
        fig = px.line(
             df_forecast,
             x="Year",
             y="Penalty",
            markers=True
                        )

# Añadir etiquetas bonitas
        fig.update_traces(
           mode = "lines+markers+text",
           line=dict(width=2),
           marker=dict(size=7),
           text=df_forecast["Penalty"],  # valores
           texttemplate="$%{text:,.0f}",  # formato $
           textposition="bottom center",
           textfont=dict(size=14)
           )

# Estilo
        fig.update_layout(
            height=280,
            margin=dict(l=10, r=10, t=10, b=10),
            yaxis_title="Penalty ($)",
            xaxis_title="Year",
            xaxis=dict(showgrid=True, gridcolor = "rgba(255, 255, 255, 0.1)",
                       range=[2023, 2041]),
            yaxis=dict(tickprefix="$",
              showgrid=True,
              gridcolor="rgba(255,255,255,0.15)")
            )

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.write("### Emissions vs Limit")

        df_bar = pd.DataFrame({
            "Type": ["Actual Emissions", "Limit"],
            "Value": [emisiones, limite]
        })

        fig_bar = px.bar(
            df_bar,
            x="Value",
            y="Type",
            orientation="h",
            color="Type",
            text="Value"
        )
        fig_bar.update_layout(height=260, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_bar, use_container_width=True)

        c1, c2 = st.columns([1, 1])

        with c1:
            st.write("### Summary")

            resumen_df = pd.DataFrame({
                "Metric": [
                    "DOB Emissions (tCO₂e)",
                    "Calculated Emissions (tCO₂e)",
                    "Limit (tCO₂e)",
                    "Excess (tCO₂e)",
                    "Penalty"
                ],
                "Value": [
                    emisiones_dob,
                    emisiones,
                    limite,
                    exceso,
                    format_money(multa)
                ]
            })

            st.dataframe(resumen_df, use_container_width=True, hide_index=True)

        with c2:
            pie_values = {
                "Within Limit": max(limite - emisiones, 0),
                "Excess": max(exceso, 0),
                "Electricity": max(electricity, 0),
                "Natural Gas": max(natural_gas, 0),
                "Others": max(others, 0),
                "Fuel Oil": max(oil, 0)
            }

            

            df_pie = pd.DataFrame({
                "Source": list(pie_values.keys()),
                "Value": list(pie_values.values())
            })

            df_pie = df_pie.iloc[2:,:] 

            st.write("### Emissions Breakdown")
            fig_pie = px.pie(
                df_pie,
                values="Value",
                names="Source",
                hole=0.4
            )
            fig_pie.update_layout(height=260, margin=dict(l=10, r=10, t=10, b=10))
            fig_pie.update_traces(textfont_size=20, textposition='inside')
            
            st.plotly_chart(fig_pie, use_container_width=True)
            
    st.divider()

    with st.expander("🔎 Ver datos crudos"):
        st.dataframe(pd.DataFrame([data]), use_container_width=True)
        st.divider()

    st.write("## 🤖 Improve building efficiency advices")

    if st.button("Generate 5 efficiency improvement tips"):
        with st.spinner("Generating recommendations..."):
            try:
                consejos = obtener_consejos_chatgpt(
                    data,
                    data_predictions,
                    data_fuels
                )
                st.markdown(consejos)
            except Exception as e:
                st.error(f"Failed to generate recommendations: {e}")