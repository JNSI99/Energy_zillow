import streamlit as st
import pandas as pd
import plotly.express as px
import Funciones as F


# --- CONFIGURACIÓN DE LA PÁGINA ---
# Nota: Este debe ser siempre el primer comando de Streamlit
st.set_page_config(page_title="Energy Dashboard", layout="wide")

# --- LÓGICA DE ESTADO ---
if 'pagina_actual' not in st.session_state:
    st.session_state.pagina_actual = 'busqueda'
if 'datos_busqueda' not in st.session_state:
    st.session_state.datos_busqueda = None

# --- FUNCIÓN DE BÚSQUEDA ---

from rapidfuzz import process, fuzz

def buscar_direcciones_similares(direccion, n=5):
    import pandas as pd
    import Funciones as f
    df = pd.read_csv('basic_information.csv')
    columna1 = 'address'
    columna2 = 'Address 1'

    def normalizar(s):
        s = str(s).lower()
        s = s.replace("avenue", "ave")
        s = s.replace("street", "st")
        return s.strip()

    # originales
    direcciones = df[columna1].dropna().astype(str).tolist()
    direcciones2 = df[columna2].dropna().astype(str).tolist()

    # normalizadas
    direcciones_norm = [normalizar(d) for d in direcciones]
    direcciones2_norm = [normalizar(d) for d in direcciones2]
    direccion_norm = normalizar(direccion)

    # 🔥 MUY IMPORTANTE: usar indices
    resultados = process.extract(
        direccion_norm,
        direcciones_norm,
        scorer=fuzz.WRatio,
        limit=n
    )

    resultados2 = process.extract(
        direccion_norm,
        direcciones2_norm,
        scorer=fuzz.WRatio,
        limit=n
    )

    # usar el índice para volver al df original
    idx1 = resultados[0][2]
    idx2 = resultados2[0][2]

    score1 = resultados[0][1]
    score2 = resultados2[0][1]
    
    # data df
    df_final = pd.read_csv('fuels.csv')
    


    # elegir el mejor match
    if score1 >= score2:
        bbl = df["BBL"].iloc[idx1]
        
        return f.display_information(2024, bbl)
    else:
        bbl = df["BBL"].iloc[idx2]
        return f.display_information(2024, bbl)

# --- PÁGINA DE BÚSQUEDA ---
if st.session_state.pagina_actual == 'busqueda':
    st.title("🔍 Energy Search")
    query = st.text_input("Busca una dirección o nombre de edificio:", placeholder="Ej: 123 Empire State St.")
    
    if st.button("Analizar Edificio"):
        if query: # Comprobamos que el usuario escribió algo
            resultado = buscar_direcciones_similares(query)
            
            # 1. Comprobamos que resultado no sea None y que no esté vacío
            if resultado is not None and not resultado.empty:
                
                # 2. IMPORTANTE: Guardamos todo el objeto (la fila) y no solo un campo
                st.session_state.datos_busqueda = resultado 
                st.session_state.pagina_actual = 'dashboard'
                st.rerun()
            else:
                st.error("No se encontró el edificio o hubo un error en la búsqueda.")
        else:
            st.warning("Por favor, ingresa una dirección.")




# --- PÁGINA DE DASHBOARD ---
elif st.session_state.pagina_actual == 'dashboard':
    # Extraemos la información del estado
    # Asumimos que guardaste la fila del DF en st.session_state.datos_busqueda
    data = st.session_state.datos_busqueda
    
    if st.button("⬅️ Nueva Búsqueda"):
        st.session_state.pagina_actual = 'busqueda'
        st.rerun()

    # --- HEADER DINÁMICO CON TUS COLUMNAS ---
    # Usamos 'address' o 'Address 1', 'Property Name', 'ranking' y 'status'
    st.success(f"### 📍 {data['address']} | 🏢 {data['Property Name']} | 🏆 Ranking: {data['ranking']} | ⚖️ Status: {data['status']}")
    st.divider()

    # --- LAYOUT DE COLUMNAS ---
    col_izquierda, col_derecha = st.columns([1, 1.5], gap="large")

    with col_izquierda:
        # Fila 1 Izq: % de Exceso (Relativo)
        # Usamos 'Relativo' que suele ser el porcentaje y 'Exceso'
        st.metric(
            label="Total Emissions % over the limit", 
            value=f"{data['Relativo']:.2f}%", 
            delta=f"{data['Exceso']:.2f} tCO2e", 
            delta_color="inverse"
        )
        
        # Fila 2 Izq: Multa
        st.metric(label="Annual Penalty ($)", value=f"${data['multa']:,.2f}")
        
        # Fila 3 Izq: Forecasting (Aquí podrías proyectar la multa basado en 'multa')
        st.write("**Forecasting annual penalty**")
        # Simulación simple basada en tu columna 'multa' actual
        df_forecast = pd.DataFrame({
            "Year": ["2024", "2030", "2035", "2040"],
            "Penalty ($)": [data['multa'], data['multa']*1.2, data['multa']*1.5, data['multa']*2.1]
        })
        st.dataframe(df_forecast, hide_index=True, use_container_width=True)

    with col_derecha:
        # Fila 1 Der: Emissions vs Limit
        # Usamos 'Emisiones Calculadas' y 'Limite'
        st.write("**Emissions vs Limit (tCO2e)**")
        df_bar = pd.DataFrame({
            "Type": ["Actual Emissions", "Limit"],
            "Value": [data['Emisiones Calculadas'], data['Limite']]
        })
        fig_bar = px.bar(df_bar, x="Value", y="Type", orientation='h', 
                         color="Type", color_discrete_map={"Limit": "#A9A9A9", "Actual Emissions": "#FF4B4B"})
        fig_bar.update_layout(height=200, margin=dict(l=0, r=0, t=0, b=0), showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)

        # Fila 2 Der: ENERGY STAR Score y BBL
        c1, c2 = st.columns([1, 1])
        with c1:
            # Mostramos el ENERGY STAR Score como un gráfico circular simple
            score = data['ENERGY STAR Score']
            fig_pie = px.pie(values=[score, 100-score], names=["Score", "Remaining"], hole=0.6,
                             color_discrete_sequence=["#00FF00", "#333333"])
            fig_pie.update_layout(height=200, showlegend=False, margin=dict(l=0, r=0, t=0, b=0))
            fig_pie.add_annotation(text=f"{score}", x=0.5, y=0.5, showarrow=False, font_size=25)
            st.plotly_chart(fig_pie, use_container_width=True)
            
        with c2:
            st.write("### Property Details")
            st.write(f"**BBL:** {data['BBL']}")
            st.write(f"**Calendar Year:** {data['Calendar Year']}")
            st.caption(f"Emisiones DOB (x): {data['Emisiones DOB_x']}")

        # Fila 3 Der: Simulations
        st.divider()
        st.write("#### Energy consumption Simulations")
        st.info(f"Diferencia actual: {data['Diferencia']:.2f} tCO2e")
        st.button("Run Simulation Model ⚙️")
"""
elif st.session_state.pagina_actual == 'dashboard':
    data = st.session_state.datos_busqueda
    
    if st.button("⬅️ Nueva Búsqueda"):
        st.session_state.pagina_actual = 'busqueda'
        st.rerun()

    st.success(f"### {data['direccion']} | Name: Example Bldg | Ranking: {data['ranking']} | Status: {data['status']}")
    st.divider()

    col_izquierda, col_derecha = st.columns([1, 1.5], gap="large")

    with col_izquierda:
        st.metric(label="Total Emissions % over the limit", value="12.5%", delta="Exceeded", delta_color="inverse")
        st.metric(label="Annual Penalty ($)", value="$45,200")
        
        st.write("**Forecasting annual penalty**")
        df_forecast = pd.DataFrame({
            "Year": ["2024", "2030", "2035", "2040"],
            "Penalty ($)": [45200, 58000, 82000, 110000]
        })
        st.dataframe(df_forecast, hide_index=True, use_container_width=True)

    with col_derecha:
        st.write("**Emissions vs Limit**")
        df_bar = pd.DataFrame({
            "Type": ["Actual Emissions", "Limit"],
            "Value": [120, 100]
        })
        fig_bar = px.bar(df_bar, x="Value", y="Type", orientation='h', 
                         color="Type", color_discrete_map={"Limit": "grey", "Actual Emissions": "red"})
        fig_bar.update_layout(height=200, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig_bar, use_container_width=True)

        c1, c2 = st.columns([1, 1])
        with c1:
            df_pie = pd.DataFrame({"Source": ["Gas", "Elec", "Steam"], "Val": [40, 50, 10]})
            fig_pie = px.pie(df_pie, values='Val', names='Source', hole=0.4)
            fig_pie.update_layout(height=200, showlegend=False, margin=dict(l=0, r=0, t=0, b=0))
            st.plotly_chart(fig_pie, use_container_width=True)
        with c2:
            st.write("### Emissions By Source")
            st.caption("Detailed breakdown of carbon footprint by utility type.")

        st.divider()
        st.write("#### Energy consumption Simulations")
        st.button("Run Simulation Model ⚙️")
        """