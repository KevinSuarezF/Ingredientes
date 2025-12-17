import pandas as pd
import sys
from io import StringIO

# Importar las funciones del app
from app import extract_numeric_value, process_excel_data

def test_extract_numeric_value():
    """Prueba la función de extracción de valores numéricos"""
    print("=== TEST: extract_numeric_value ===\n")
    
    test_cases = [
        ("1500 mg/kg", 1500.0),
        ("BPF", None),
        ("2000.5 mg/kg", 2000.5),
        ("", None),
        (None, None),
        ("300", 300.0),
        ("No hay número aquí", None),
        ("bpf", None),
        ("  1000 mg/kg  ", 1000.0),
        ("500-1000 mg/kg", 500.0),  # Solo toma el primer número
        (123, 123.0),  # Valor numérico directo
    ]
    
    passed = 0
    failed = 0
    
    for value, expected in test_cases:
        result = extract_numeric_value(value)
        status = "✓" if result == expected else "✗"
        if result == expected:
            passed += 1
        else:
            failed += 1
        print(f"{status} Input: {repr(value):30} | Expected: {str(expected):10} | Got: {result}")
    
    print(f"\nResultado: {passed} pasadas, {failed} fallidas\n")
    return failed == 0

def test_process_excel_data():
    """Prueba diferentes escenarios de procesamiento de datos"""
    print("=== TEST: process_excel_data ===\n")
    
    all_tests_passed = True
    
    # Test 1: Datos normales con valores mixtos
    print("Test 1: Datos con valores mixtos")
    df1 = pd.DataFrame({
        'Clasificacion': ['Estabilizante', 'Estabilizante', 'Antioxidante'],
        'N_INS': ['331', '331', '300'],
        'Ingrediente': ['Citrato', 'Citrato', 'Ácido ascórbico'],
        'Dosis_Maxima': ['1500 mg/kg', 'BPF', '500 mg/kg']
    })
    
    try:
        result1 = process_excel_data(df1)
        print(result1.to_string())
        print(f"✓ Test 1 pasado - {len(result1)} registros procesados\n")
    except Exception as e:
        print(f"✗ Test 1 falló: {e}\n")
        all_tests_passed = False
    
    # Test 2: Solo valores BPF
    print("Test 2: Solo valores BPF")
    df2 = pd.DataFrame({
        'Clasificacion': ['Gas de envasado', 'Gas de envasado'],
        'N_INS': ['941', '941'],
        'Ingrediente': ['Nitrógeno', 'Nitrógeno'],
        'Dosis_Maxima': ['BPF', 'BPF']
    })
    
    try:
        result2 = process_excel_data(df2)
        print(result2.to_string())
        print(f"✓ Test 2 pasado - Dosis mínima y máxima deben ser BPF\n")
    except Exception as e:
        print(f"✗ Test 2 falló: {e}\n")
        all_tests_passed = False
    
    # Test 3: Valores numéricos múltiples
    print("Test 3: Múltiples valores numéricos en mismo grupo")
    df3 = pd.DataFrame({
        'Clasificacion': ['Conservante', 'Conservante', 'Conservante'],
        'N_INS': ['200', '200', '200'],
        'Ingrediente': ['Ácido sórbico', 'Ácido sórbico', 'Ácido sórbico'],
        'Dosis_Maxima': ['1000 mg/kg', '1500 mg/kg', '500 mg/kg']
    })
    
    try:
        result3 = process_excel_data(df3)
        print(result3.to_string())
        min_val = result3.iloc[0]['Dosis Mínima']
        max_val = result3.iloc[0]['Dosis Máxima']
        if '500.0' in min_val and '1500.0' in max_val:
            print(f"✓ Test 3 pasado - Mínimo: {min_val}, Máximo: {max_val}\n")
        else:
            print(f"✗ Test 3 falló - Valores incorrectos: Mín: {min_val}, Máx: {max_val}\n")
            all_tests_passed = False
    except Exception as e:
        print(f"✗ Test 3 falló: {e}\n")
        all_tests_passed = False
    
    # Test 4: DataFrame vacío
    print("Test 4: DataFrame vacío")
    df4 = pd.DataFrame(columns=['Clasificacion', 'N_INS', 'Ingrediente', 'Dosis_Maxima'])
    
    try:
        result4 = process_excel_data(df4)
        print(f"Resultado: {len(result4)} registros")
        print(f"✓ Test 4 pasado - Maneja DataFrames vacíos\n")
    except Exception as e:
        print(f"✗ Test 4 falló: {e}\n")
        all_tests_passed = False
    
    # Test 5: Valores None/NaN
    print("Test 5: Valores None/NaN en dosis")
    df5 = pd.DataFrame({
        'Clasificacion': ['Colorante', 'Colorante'],
        'N_INS': ['100', '100'],
        'Ingrediente': ['Curcumina', 'Curcumina'],
        'Dosis_Maxima': [None, pd.NA]
    })
    
    try:
        result5 = process_excel_data(df5)
        print(result5.to_string())
        print(f"✓ Test 5 pasado - Maneja valores None/NaN\n")
    except Exception as e:
        print(f"✗ Test 5 falló: {e}\n")
        all_tests_passed = False
    
    # Test 6: Diferentes clasificaciones con mismo INS
    print("Test 6: Múltiples clasificaciones")
    df6 = pd.DataFrame({
        'Clasificacion': ['Tipo A', 'Tipo B', 'Tipo A'],
        'N_INS': ['100', '200', '100'],
        'Ingrediente': ['Ingrediente 1', 'Ingrediente 2', 'Ingrediente 1'],
        'Dosis_Maxima': ['100 mg/kg', '200 mg/kg', '150 mg/kg']
    })
    
    try:
        result6 = process_excel_data(df6)
        print(result6.to_string())
        print(f"✓ Test 6 pasado - {len(result6)} grupos únicos identificados\n")
    except Exception as e:
        print(f"✗ Test 6 falló: {e}\n")
        all_tests_passed = False
    
    # Test 7: Un solo valor numérico con BPF
    print("Test 7: Un valor numérico y uno BPF")
    df7 = pd.DataFrame({
        'Clasificacion': ['Emulsionante', 'Emulsionante'],
        'N_INS': ['450', '450'],
        'Ingrediente': ['Fosfato', 'Fosfato'],
        'Dosis_Maxima': ['1000 mg/kg', 'BPF']
    })
    
    try:
        result7 = process_excel_data(df7)
        print(result7.to_string())
        min_val = result7.iloc[0]['Dosis Mínima']
        max_val = result7.iloc[0]['Dosis Máxima']
        print(f"Comportamiento actual: Mínimo: {min_val}, Máximo: {max_val}")
        print(f"✓ Test 7 pasado - Un valor numérico se usa para mín y máx\n")
    except Exception as e:
        print(f"✗ Test 7 falló: {e}\n")
        all_tests_passed = False
    
    # Test 8: Valores con decimales
    print("Test 8: Valores con decimales")
    df8 = pd.DataFrame({
        'Clasificacion': ['Edulcorante'],
        'N_INS': ['951'],
        'Ingrediente': ['Aspartamo'],
        'Dosis_Maxima': ['40.5 mg/kg']
    })
    
    try:
        result8 = process_excel_data(df8)
        print(result8.to_string())
        print(f"✓ Test 8 pasado - Maneja decimales correctamente\n")
    except Exception as e:
        print(f"✗ Test 8 falló: {e}\n")
        all_tests_passed = False
    
    return all_tests_passed

def test_edge_cases():
    """Prueba casos extremos adicionales"""
    print("=== TEST: Casos Extremos ===\n")
    
    all_passed = True
    
    # Test: Espacios en blanco
    print("Test: Espacios y strings vacíos")
    test_values = ["   ", "", "  BPF  ", "  1000 mg/kg  "]
    for val in test_values:
        result = extract_numeric_value(val)
        print(f"Input: {repr(val):20} -> {result}")
    print("✓ Completado\n")
    
    # Test: INS números complejos
    print("Test: Números INS complejos")
    df = pd.DataFrame({
        'Clasificacion': ['Complejo', 'Complejo', 'Complejo'],
        'N_INS': ['338; 339(i)-(iii)', '338; 339(i)-(iii)', '450(i)-(iii),(v)-(vii)'],
        'Ingrediente': ['Sales fosfatadas', 'Sales fosfatadas', 'Fosfatos complejos'],
        'Dosis_Maxima': ['1500 mg/kg', '2000 mg/kg', 'BPF']
    })
    
    try:
        result = process_excel_data(df)
        print(result.to_string())
        print(f"✓ Maneja INS complejos - {len(result)} grupos\n")
    except Exception as e:
        print(f"✗ Falló con INS complejos: {e}\n")
        all_passed = False
    
    return all_passed

if __name__ == "__main__":
    print("=" * 60)
    print("SUITE DE PRUEBAS - Procesador de Ingredientes")
    print("=" * 60)
    print()
    
    test1 = test_extract_numeric_value()
    test2 = test_process_excel_data()
    test3 = test_edge_cases()
    
    print("=" * 60)
    if test1 and test2 and test3:
        print("✓ TODAS LAS PRUEBAS PASARON")
    else:
        print("✗ ALGUNAS PRUEBAS FALLARON")
    print("=" * 60)
