import streamlit as st
import pandas as pd
import re
from io import BytesIO

def extract_numeric_value(value):
    """Extrae el valor numérico de una cadena como '1500 mg/kg'"""
    if pd.isna(value) or value == 'BPF':
        return None
    
    # Convertir a string si no lo es
    value_str = str(value).strip()
    
    # Si es una cadena vacía después del strip, retornar None
    if not value_str:
        return None
    
    # Si ya es 'BPF', retornar None
    if value_str.upper() == 'BPF':
        return None
    
    # Buscar números (incluyendo decimales)
    match = re.search(r'(\d+(?:\.\d+)?)', value_str)
    if match:
        return float(match.group(1))
    
    return None

def process_excel_data(df):
    """Procesa los datos del Excel según los requisitos"""
    
    # Validar que el DataFrame no esté vacío
    if df.empty:
        return pd.DataFrame(columns=['Clasificación', 'Nº INS', 'Ingrediente', 'Dosis Mínima', 'Dosis Máxima'])
    
    # Renombrar columnas para trabajar más fácil
    df.columns = ['Clasificacion', 'N_INS', 'Ingrediente', 'Dosis_Maxima']
    
    # Limpiar espacios en blanco de las columnas de texto
    df['Clasificacion'] = df['Clasificacion'].astype(str).str.strip()
    df['N_INS'] = df['N_INS'].astype(str).str.strip()
    df['Ingrediente'] = df['Ingrediente'].astype(str).str.strip()
    
    # Filtrar filas con valores inválidos en columnas clave
    df = df[df['Clasificacion'] != 'None']
    df = df[df['N_INS'] != 'None']
    df = df[df['Clasificacion'] != '']
    df = df[df['N_INS'] != '']
    
    # Si después del filtrado el DataFrame queda vacío, retornar vacío
    if df.empty:
        return pd.DataFrame(columns=['Clasificación', 'Nº INS', 'Ingrediente', 'Dosis Mínima', 'Dosis Máxima'])
    
    # Crear una lista para almacenar los resultados
    results = []
    
    # Agrupar por Clasificación y N INS
    grouped = df.groupby(['Clasificacion', 'N_INS'])
    
    for (clasificacion, n_ins), group in grouped:
        # Obtener el ingrediente (tomar el primero no nulo si hay varios)
        ingrediente_vals = group['Ingrediente'].dropna()
        if len(ingrediente_vals) > 0 and str(ingrediente_vals.iloc[0]) != 'None':
            ingrediente = ingrediente_vals.iloc[0]
        else:
            ingrediente = ''
        
        # Extraer valores numéricos de dosis máxima
        dosis_values = []
        for dosis in group['Dosis_Maxima']:
            valor = extract_numeric_value(dosis)
            if valor is not None:
                dosis_values.append(valor)
        
        # Determinar dosis mínima y máxima
        if len(dosis_values) > 0:
            dosis_minima = f"{min(dosis_values)} mg/kg"
            dosis_maxima = f"{max(dosis_values)} mg/kg"
        else:
            dosis_minima = "BPF"
            dosis_maxima = "BPF"
        
        results.append({
            'Clasificación': clasificacion,
            'Nº INS': n_ins,
            'Ingrediente': ingrediente,
            'Dosis Mínima': dosis_minima,
            'Dosis Máxima': dosis_maxima
        })
    
    # Crear DataFrame con los resultados
    result_df = pd.DataFrame(results)
    
    # Ordenar por Clasificación
    result_df = result_df.sort_values('Clasificación').reset_index(drop=True)
    
    return result_df

def convert_df_to_excel(df):
    """Convierte DataFrame a Excel en memoria"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Datos Procesados')
    output.seek(0)
    return output

# Configuración de la página
st.set_page_config(
    page_title="Procesador de Ingredientes",
    page_icon="�",
    layout="wide"
)

# Título de la aplicación
st.title("Procesador de Datos de Ingredientes")
st.markdown("---")

# Instrucciones
with st.expander("Instrucciones de uso"):
    st.markdown("""
    ### Formato del archivo Excel:
    - Los datos deben comenzar desde la celda **B2** (incluyendo el título)
    - Las columnas deben ser:
        1. **Clasificación**
        2. **Nº INS**
        3. **Ingrediente**
        4. **Dosis máxima**
    
    ### Procesamiento:
    - Agrupa los ingredientes por **Clasificación** y **Nº INS**
    - Calcula la dosis mínima y máxima para cada grupo
    - Si no hay valores numéricos, muestra "BPF"
    - Organiza los resultados por clasificación
    """)

st.markdown("---")

# Carga de archivo
uploaded_file = st.file_uploader(
    "Carga tu archivo Excel",
    type=['xlsx', 'xls'],
    help="Selecciona un archivo Excel con el formato especificado"
)

if uploaded_file is not None:
    try:
        # Leer el archivo Excel
        # Leer desde la columna B (índice 1) y desde la fila 2 (índice 1, ya que Python es 0-indexed)
        df = pd.read_excel(uploaded_file, header=1, usecols="B:E")
        
        # Eliminar filas vacías
        df = df.dropna(how='all')
        
        # Mostrar vista previa de datos originales
        st.subheader("Vista previa de datos originales")
        st.dataframe(df, use_container_width=True)
        
        # Procesar los datos
        with st.spinner("Procesando datos..."):
            result_df = process_excel_data(df)
        
        # Mostrar resultados procesados
        st.success("Datos procesados exitosamente")
        st.subheader("Datos Procesados")
        st.dataframe(result_df, use_container_width=True)
        
        # Mostrar estadísticas
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de registros originales", len(df))
        with col2:
            st.metric("Total de registros procesados", len(result_df))
        with col3:
            st.metric("Clasificaciones únicas", result_df['Clasificación'].nunique())
        
        # Botón de descarga
        st.markdown("---")
        excel_data = convert_df_to_excel(result_df)
        
        st.download_button(
            label="Descargar Excel Procesado",
            data=excel_data,
            file_name="datos_procesados.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
        
    except Exception as e:
        st.error(f"Error al procesar el archivo: {str(e)}")
        st.info("Por favor, verifica que el archivo tenga el formato correcto.")

else:
    # Mostrar ejemplo cuando no hay archivo cargado
    st.info("Por favor, carga un archivo Excel para comenzar")
    
    # Mostrar ejemplo de datos
    st.subheader("Ejemplo de formato de datos")
    ejemplo_df = pd.DataFrame({
        'Clasificación': [
            'Estabilizante / regulador acidez',
            'Estabilizante / emulsionante',
            'Gas de envasado / atmósfera inerte',
            'Enriquecimiento (vitamina C)'
        ],
        'Nº INS': ['331(iii)', '338; 339(i)–(iii); 340(i)–(iii); 341(i)–(iii); 342(i)–(ii); 343(i)–(ii); 450(i)–(iii),(v)–(vii),(ix); 451(i),(ii); 452(i)–(v); 542', '941', '300'],
        'Ingrediente': ['Citrato trisódico', 'Fosfatos (diversas sales fosfatadas)', 'Nitrógeno', 'Ácido ascórbico, L-'],
        'Dosis máxima': ['BPF', '1500 mg/kg', 'BPF', 'BPF']
    })
    st.dataframe(ejemplo_df, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        Desarrollado usando Streamlit
    </div>
    """,
    unsafe_allow_html=True
)
