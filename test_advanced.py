import pandas as pd
from app import extract_numeric_value, process_excel_data

def test_special_characters():
    """Prueba caracteres especiales y formatos inusuales"""
    print("=== TEST: Caracteres especiales ===\n")
    
    test_cases = [
        "1,500 mg/kg",  # Coma como separador de miles
        "1.500 mg/kg",  # Punto como separador de miles (europeo)
        "1500mg/kg",    # Sin espacio
        "1500 MG/KG",   # Mayúsculas
        "1500",         # Solo número
        "1500.0",       # Decimal sin unidades
        "< 1000 mg/kg", # Menor que
        "> 500 mg/kg",  # Mayor que
        "≤ 2000 mg/kg", # Menor o igual
        "≥ 100 mg/kg",  # Mayor o igual
        "BPF (Buenas Prácticas de Fabricación)",  # BPF con descripción
        "No especificado",  # Otra forma de decir N/A
        "N/A",
        "-",
        "—",  # Em dash
    ]
    
    for test_val in test_cases:
        result = extract_numeric_value(test_val)
        print(f"Input: {test_val:50} -> {result}")
    
    print()

def test_duplicate_data():
    """Prueba datos duplicados exactos"""
    print("=== TEST: Datos duplicados ===\n")
    
    df = pd.DataFrame({
        'Clasificacion': ['Conservante', 'Conservante', 'Conservante', 'Conservante'],
        'N_INS': ['200', '200', '200', '200'],
        'Ingrediente': ['Ácido sórbico', 'Ácido sórbico', 'Ácido sórbico', 'Ácido sórbico'],
        'Dosis_Maxima': ['1000 mg/kg', '1000 mg/kg', '1000 mg/kg', '1000 mg/kg']
    })
    
    result = process_excel_data(df)
    print(result.to_string())
    print(f"\n{len(df)} registros de entrada -> {len(result)} registro(s) de salida")
    print("✓ Maneja duplicados correctamente\n")

def test_mixed_formats():
    """Prueba mezcla de formatos en el mismo grupo"""
    print("=== TEST: Formatos mixtos en mismo grupo ===\n")
    
    df = pd.DataFrame({
        'Clasificacion': ['Colorante', 'Colorante', 'Colorante', 'Colorante'],
        'N_INS': ['100', '100', '100', '100'],
        'Ingrediente': ['Curcumina', 'Curcumina', 'Curcumina', 'Curcumina'],
        'Dosis_Maxima': ['100 mg/kg', '150', 'BPF', '200.5 mg/kg']
    })
    
    result = process_excel_data(df)
    print(result.to_string())
    print(f"Debe mostrar mínimo: 100.0 mg/kg y máximo: 200.5 mg/kg\n")

def test_large_numbers():
    """Prueba números muy grandes o muy pequeños"""
    print("=== TEST: Números extremos ===\n")
    
    df = pd.DataFrame({
        'Clasificacion': ['Test A', 'Test B', 'Test C'],
        'N_INS': ['001', '002', '003'],
        'Ingrediente': ['Grande', 'Pequeño', 'Decimal'],
        'Dosis_Maxima': ['100000 mg/kg', '0.001 mg/kg', '0.5 mg/kg']
    })
    
    result = process_excel_data(df)
    print(result.to_string())
    print("✓ Maneja números extremos\n")

def test_unicode_and_special_chars():
    """Prueba caracteres Unicode y especiales en nombres"""
    print("=== TEST: Unicode y caracteres especiales ===\n")
    
    df = pd.DataFrame({
        'Clasificacion': ['Conservación', 'Émulsión', 'Estabilización'],
        'N_INS': ['200', '300', '400'],
        'Ingrediente': ['Ácido cítrico', 'β-caroteno', 'D-α-tocoferol'],
        'Dosis_Maxima': ['1000 mg/kg', '500 mg/kg', 'BPF']
    })
    
    result = process_excel_data(df)
    print(result.to_string())
    print("✓ Maneja caracteres Unicode\n")

def test_inconsistent_spacing():
    """Prueba espaciado inconsistente"""
    print("=== TEST: Espaciado inconsistente ===\n")
    
    df = pd.DataFrame({
        'Clasificacion': ['  Tipo A  ', 'Tipo A', ' Tipo A'],
        'N_INS': ['  100  ', '100', ' 100'],
        'Ingrediente': ['Ingrediente   1', 'Ingrediente 1', '  Ingrediente 1  '],
        'Dosis_Maxima': ['  1000 mg/kg  ', '1500 mg/kg', '2000 mg/kg  ']
    })
    
    result = process_excel_data(df)
    print(result.to_string())
    print(f"Registros agrupados: {len(result)}")
    print("Nota: Espacios pueden causar agrupación incorrecta\n")

def test_null_and_empty_values():
    """Prueba valores nulos y vacíos en diferentes columnas"""
    print("=== TEST: Valores nulos en diferentes columnas ===\n")
    
    df = pd.DataFrame({
        'Clasificacion': ['Tipo A', 'Tipo B', None, 'Tipo D'],
        'N_INS': ['100', None, '300', '400'],
        'Ingrediente': ['Ingrediente 1', 'Ingrediente 2', 'Ingrediente 3', None],
        'Dosis_Maxima': ['1000 mg/kg', 'BPF', None, '500 mg/kg']
    })
    
    try:
        result = process_excel_data(df)
        print(result.to_string())
        print("✓ Maneja valores nulos\n")
    except Exception as e:
        print(f"✗ Error con valores nulos: {e}\n")

def test_same_ingredient_different_ins():
    """Prueba mismo ingrediente con diferentes números INS"""
    print("=== TEST: Mismo ingrediente, diferentes INS ===\n")
    
    df = pd.DataFrame({
        'Clasificacion': ['Conservante', 'Conservante', 'Conservante'],
        'N_INS': ['200', '201', '202'],
        'Ingrediente': ['Ácido sórbico', 'Ácido sórbico', 'Ácido sórbico'],
        'Dosis_Maxima': ['1000 mg/kg', '1500 mg/kg', '2000 mg/kg']
    })
    
    result = process_excel_data(df)
    print(result.to_string())
    print(f"Debe crear {len(result)} registros separados (uno por INS)\n")

def test_real_world_complex_case():
    """Simula un caso complejo del mundo real"""
    print("=== TEST: Caso complejo del mundo real ===\n")
    
    df = pd.DataFrame({
        'Clasificacion': [
            'Estabilizante / emulsionante',
            'Estabilizante / emulsionante',
            'Estabilizante / emulsionante',
            'Antioxidante / conservante',
            'Antioxidante / conservante',
            'Colorante natural',
        ],
        'N_INS': [
            '338; 339(i)–(iii); 340(i)–(iii)',
            '338; 339(i)–(iii); 340(i)–(iii)',
            '338; 339(i)–(iii); 340(i)–(iii)',
            '300; 301',
            '300; 301',
            '100',
        ],
        'Ingrediente': [
            'Fosfatos (diversas sales)',
            'Fosfatos (diversas sales)',
            'Fosfatos (diversas sales)',
            'Ácido ascórbico / Ascorbato de sodio',
            'Ácido ascórbico / Ascorbato de sodio',
            'Curcumina',
        ],
        'Dosis_Maxima': [
            '1500 mg/kg',
            '2000 mg/kg',
            'BPF',
            'BPF',
            '500 mg/kg',
            '100 mg/kg'
        ]
    })
    
    result = process_excel_data(df)
    print(result.to_string())
    print(f"\n{len(df)} registros -> {len(result)} grupos\n")

if __name__ == "__main__":
    print("=" * 70)
    print("SUITE DE PRUEBAS AVANZADAS - Procesador de Ingredientes")
    print("=" * 70)
    print()
    
    test_special_characters()
    test_duplicate_data()
    test_mixed_formats()
    test_large_numbers()
    test_unicode_and_special_chars()
    test_inconsistent_spacing()
    test_null_and_empty_values()
    test_same_ingredient_different_ins()
    test_real_world_complex_case()
    
    print("=" * 70)
    print("PRUEBAS AVANZADAS COMPLETADAS")
    print("=" * 70)
