# Procesador de Datos de Ingredientes

Aplicación web desarrollada con Streamlit para procesar archivos Excel con información de ingredientes, clasificaciones y dosis.

## Características

- **Carga de archivos Excel**: Sube archivos .xlsx o .xls
- **📊 Soporte para múltiples hojas**: Procesa automáticamente todas las hojas del Excel
- **Procesamiento automático**: Agrupa datos por Clasificación y Nº INS
- **Cálculo de dosis**: Determina dosis mínima y máxima automáticamente
- **Visualización por pestañas**: Cada hoja se muestra en su propia pestaña
- **Descarga de resultados**: Exporta los datos procesados a Excel con todas las hojas
- **Interfaz intuitiva**: Diseño limpio y fácil de usar

## Formato de Datos

El archivo Excel debe contener datos desde la celda **B2** (incluyendo títulos) con las siguientes columnas:

1. **Clasificación**: Tipo de ingrediente (ej. "Estabilizante / regulador acidez")
2. **Nº INS**: Número de Sistema Internacional de Numeración (ej. "331(iii)")
3. **Ingrediente**: Nombre del ingrediente (ej. "Citrato trisódico")
4. **Dosis máxima**: Dosis máxima permitida (ej. "1500 mg/kg" o "BPF")

### ✨ Múltiples Hojas

La aplicación procesa automáticamente **todas las hojas** del archivo Excel:
- Cada hoja se procesa de manera independiente
- Los resultados se visualizan en pestañas separadas
- El archivo descargado incluye todas las hojas procesadas
- No se requiere configuración adicional

### Ejemplo de Datos

| Clasificación | Nº INS | Ingrediente | Dosis máxima |
|--------------|--------|-------------|--------------|
| Estabilizante / regulador acidez | 331(iii) | Citrato trisódico | BPF |
| Estabilizante / emulsionante | 338; 339(i)–(iii); 340(i)–(iii); 341(i)–(iii); 342(i)–(ii); 343(i)–(ii); 450(i)–(iii),(v)–(vii),(ix); 451(i),(ii); 452(i)–(v); 542 | Fosfatos (diversas sales fosfatadas) | 1500 mg/kg |
| Gas de envasado / atmósfera inerte | 941 | Nitrógeno | BPF |
| Enriquecimiento (vitamina C) | 300 | Ácido ascórbico, L- | BPF |

## Instalación Local

### Prerrequisitos

- Python 3.8 o superior
- pip

### Pasos de instalación

1. Clona este repositorio:
```bash
git clone <tu-repositorio-url>
cd streamlit-excel-processor
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

3. Ejecuta la aplicación:
```bash
streamlit run app.py
```

4. Abre tu navegador en `http://localhost:8501`

## Funcionalidad

La aplicación realiza las siguientes operaciones:

1. **Lectura de hojas**: Lee automáticamente todas las hojas del archivo Excel
2. **Agrupación**: Agrupa los datos por Clasificación y Nº INS en cada hoja
3. **Cálculo de dosis**:
   - Si hay valores numéricos, calcula el mínimo y máximo
   - Si no hay valores numéricos o solo hay "BPF", muestra "BPF"
4. **Visualización**: Muestra cada hoja en su propia pestaña con:
   - Datos originales (colapsables)
   - Datos procesados
   - Estadísticas (registros originales, procesados y clasificaciones únicas)
5. **Organización**: Ordena los resultados por clasificación
6. **Exportación**: Genera un archivo Excel con múltiples hojas, cada una con las columnas:
   - Clasificación
   - Nº INS
   - Ingrediente
   - Dosis Mínima
   - Dosis Máxima

## Tecnologías Utilizadas

- **Streamlit**: Framework para crear aplicaciones web
- **Pandas**: Procesamiento y análisis de datos
- **OpenPyXL**: Lectura y escritura de archivos Excel
- **Python**: Lenguaje de programación

## Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Haz fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Contacto

Para preguntas o sugerencias, por favor abre un issue en GitHub.
