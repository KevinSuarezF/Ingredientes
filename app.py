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

def convert_multiple_sheets_to_excel(sheets_dict):
    """Convierte múltiples DataFrames a Excel con múltiples hojas"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for sheet_name, df in sheets_dict.items():
            # Limitar el nombre de la hoja a 31 caracteres (límite de Excel)
            safe_sheet_name = sheet_name[:31]
            df.to_excel(writer, index=False, sheet_name=safe_sheet_name)
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
with st.expander("📖 Instrucciones de uso"):
    st.markdown("""
    ### Formato del archivo Excel:
    - Los datos deben comenzar desde la celda **B2** (incluyendo el título)
    - Las columnas deben ser:
        1. **Clasificación**
        2. **Nº INS**
        3. **Ingrediente**
        4. **Dosis máxima**
    - **Soporta múltiples hojas**: La aplicación procesará automáticamente todas las hojas del archivo
    
    ### Procesamiento:
    - Agrupa los ingredientes por **Clasificación** y **Nº INS**
    - Calcula la dosis mínima y máxima para cada grupo
    - Si no hay valores numéricos, muestra "BPF"
    - Organiza los resultados por clasificación
    - **Cada hoja se procesa independientemente** y se muestra en pestañas separadas
    
    ### Descarga:
    - El archivo Excel generado contendrá **todas las hojas procesadas**
    - Cada hoja del archivo original se conserva como hoja separada en el resultado
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
        # Leer todas las hojas del archivo Excel
        excel_file = pd.ExcelFile(uploaded_file)
        sheet_names = excel_file.sheet_names
        
        st.info(f"Se encontraron {len(sheet_names)} hoja(s): {', '.join(sheet_names)}")
        
        # Diccionario para almacenar datos originales y procesados por hoja
        original_data = {}
        processed_data = {}
        skipped_sheets = []
        
        # Procesar cada hoja
        for sheet_name in sheet_names:
            try:
                with st.spinner(f"Procesando hoja '{sheet_name}'..."):
                    # Leer desde la columna B (índice 1) y desde la fila 2
                    df = pd.read_excel(uploaded_file, sheet_name=sheet_name, header=1, usecols="B:E")
                    
                    # Eliminar filas vacías
                    df = df.dropna(how='all')
                    
                    # Validar que la hoja tenga las columnas esperadas
                    expected_columns = 4  # Clasificación, Nº INS, Ingrediente, Dosis máxima
                    if df.empty or len(df.columns) != expected_columns:
                        skipped_sheets.append(sheet_name)
                        continue
                    
                    # Guardar datos originales
                    original_data[sheet_name] = df
                    
                    # Procesar los datos
                    result_df = process_excel_data(df)
                    
                    # Solo guardar si hay resultados procesados
                    if not result_df.empty:
                        processed_data[sheet_name] = result_df
                    else:
                        skipped_sheets.append(sheet_name)
                        
            except Exception as e:
                skipped_sheets.append(sheet_name)
                continue
        
        # Mostrar resultado del procesamiento
        if processed_data:
            st.success(f"✓ {len(processed_data)} hoja(s) procesada(s) exitosamente")
            if skipped_sheets:
                st.warning(f"⚠️ {len(skipped_sheets)} hoja(s) omitida(s) (sin datos válidos): {', '.join(skipped_sheets)}")
        else:
            st.error("❌ No se encontraron hojas con datos válidos para procesar")
            st.stop()
        
        # Crear tabs para cada hoja procesada
        st.markdown("---")
        st.subheader("Resultados por Hoja")
        
        tabs = st.tabs(list(processed_data.keys()))
        
        for idx, sheet_name in enumerate(processed_data.keys()):
            with tabs[idx]:
                st.markdown(f"### Hoja: {sheet_name}")
                
                # Mostrar datos originales
                with st.expander("📄 Ver datos originales", expanded=False):
                    st.dataframe(original_data[sheet_name], use_container_width=True)
                
                # Mostrar datos procesados
                st.markdown("**Datos Procesados:**")
                st.dataframe(processed_data[sheet_name], use_container_width=True)
                
                # Estadísticas
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Registros originales", len(original_data[sheet_name]))
                with col2:
                    st.metric("Registros procesados", len(processed_data[sheet_name]))
                with col3:
                    st.metric("Clasificaciones únicas", processed_data[sheet_name]['Clasificación'].nunique())
        
        # Botón de descarga con todas las hojas procesadas
        st.markdown("---")
        st.subheader("Descargar Resultados")
        
        col1, col2 = st.columns(2)
        
        with col1:
            excel_data = convert_multiple_sheets_to_excel(processed_data)
            st.download_button(
                label="📥 Descargar Excel Procesado (Todas las hojas)",
                data=excel_data,
                file_name="datos_procesados.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        with col2:
            # Mostrar resumen general
            total_original = sum(len(df) for df in original_data.values())
            total_procesado = sum(len(df) for df in processed_data.values())
            st.metric("Total registros procesados", f"{total_procesado} de {total_original}")
        
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
