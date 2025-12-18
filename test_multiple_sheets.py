import pandas as pd
from io import BytesIO
from app import process_excel_data, convert_multiple_sheets_to_excel

def create_test_excel_with_multiple_sheets():
    """Crea un archivo Excel de prueba con múltiples hojas"""
    
    # Hoja 1: Estabilizantes
    hoja1 = pd.DataFrame({
        'Clasificación': ['Estabilizante', 'Estabilizante', 'Estabilizante'],
        'Nº INS': ['331', '331', '338'],
        'Ingrediente': ['Citrato', 'Citrato', 'Fosfato'],
        'Dosis máxima': ['1500 mg/kg', 'BPF', '2000 mg/kg']
    })
    
    # Hoja 2: Conservantes
    hoja2 = pd.DataFrame({
        'Clasificación': ['Conservante', 'Conservante', 'Conservante'],
        'Nº INS': ['200', '200', '211'],
        'Ingrediente': ['Ácido sórbico', 'Ácido sórbico', 'Benzoato de sodio'],
        'Dosis máxima': ['1000 mg/kg', '1500 mg/kg', '300 mg/kg']
    })
    
    # Hoja 3: Colorantes
    hoja3 = pd.DataFrame({
        'Clasificación': ['Colorante', 'Colorante'],
        'Nº INS': ['100', '102'],
        'Ingrediente': ['Curcumina', 'Tartrazina'],
        'Dosis máxima': ['BPF', '100 mg/kg']
    })
    
    # Crear archivo Excel con múltiples hojas
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Añadir una fila vacía al inicio (simulando que los datos empiezan en B2)
        for df, sheet_name in [(hoja1, 'Estabilizantes'), 
                                (hoja2, 'Conservantes'), 
                                (hoja3, 'Colorantes')]:
            # Crear DataFrame con una fila vacía al inicio
            df_with_header = pd.concat([pd.DataFrame([[''] * len(df.columns)], columns=df.columns), df], 
                                       ignore_index=True)
            df_with_header.to_excel(writer, sheet_name=sheet_name, index=False, startcol=1)
    
    output.seek(0)
    return output

def test_multiple_sheets_processing():
    """Prueba el procesamiento de múltiples hojas"""
    print("=" * 70)
    print("TEST: Procesamiento de Múltiples Hojas de Excel")
    print("=" * 70)
    print()
    
    # Crear archivo de prueba
    excel_file = create_test_excel_with_multiple_sheets()
    
    # Leer todas las hojas
    xl_file = pd.ExcelFile(excel_file)
    sheet_names = xl_file.sheet_names
    
    print(f"✓ Archivo creado con {len(sheet_names)} hojas: {', '.join(sheet_names)}")
    print()
    
    # Procesar cada hoja
    processed_data = {}
    all_success = True
    
    for sheet_name in sheet_names:
        print(f"--- Procesando hoja: {sheet_name} ---")
        try:
            # Leer datos (simulando la lectura desde B2)
            df = pd.read_excel(excel_file, sheet_name=sheet_name, header=1, usecols="B:E")
            df = df.dropna(how='all')
            
            print(f"Registros originales: {len(df)}")
            
            # Procesar
            result = process_excel_data(df)
            processed_data[sheet_name] = result
            
            print(f"Registros procesados: {len(result)}")
            print(result.to_string())
            print(f"✓ Hoja '{sheet_name}' procesada exitosamente")
            print()
            
        except Exception as e:
            print(f"✗ Error procesando hoja '{sheet_name}': {e}")
            print()
            all_success = False
    
    # Probar conversión a Excel con múltiples hojas
    print("--- Generando Excel con múltiples hojas ---")
    try:
        excel_output = convert_multiple_sheets_to_excel(processed_data)
        
        # Verificar que se creó correctamente
        verify_file = pd.ExcelFile(excel_output)
        output_sheets = verify_file.sheet_names
        
        print(f"✓ Excel generado con {len(output_sheets)} hojas: {', '.join(output_sheets)}")
        
        # Verificar contenido de cada hoja
        for sheet in output_sheets:
            df_check = pd.read_excel(excel_output, sheet_name=sheet)
            print(f"  - Hoja '{sheet}': {len(df_check)} registros")
        
        print()
        
    except Exception as e:
        print(f"✗ Error generando Excel: {e}")
        print()
        all_success = False
    
    # Resultado final
    print("=" * 70)
    if all_success:
        print("✓ TODAS LAS PRUEBAS DE MÚLTIPLES HOJAS PASARON")
    else:
        print("✗ ALGUNAS PRUEBAS FALLARON")
    print("=" * 70)
    
    return all_success

if __name__ == "__main__":
    test_multiple_sheets_processing()
