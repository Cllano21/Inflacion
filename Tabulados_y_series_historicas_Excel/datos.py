import pandas as pd
import datetime
import numpy as np

# Leer el archivo Excel (solo columnas A a M)
df = pd.read_excel('SERIE HISTORICA IPC_07_2025.xls', sheet_name='1. ÍNDICE', header=4, usecols="A:M")

# Renombrar la primera columna a 'año'
df = df.rename(columns={df.columns[0]: 'año'})

# Verificar los valores únicos en la columna 'año' para depuración
print("Valores únicos en la columna 'año' antes de limpiar:")
print(df['año'].unique())

# Filtrar y limpiar la columna 'año'
# Primero, convertir a string y luego eliminar filas no numéricas
df = df[df['año'].apply(lambda x: str(x).strip().isdigit())]

# Convertir la columna año a entero
df['año'] = df['año'].astype(int)

# Verificar los valores únicos después de limpiar
print("Valores únicos en la columna 'año' después de limpiar:")
print(df['año'].unique())

# Crear lista para almacenar los resultados
resultados = []

# Iterar sobre cada fila
for _, row in df.iterrows():
    año = int(row['año'])  # Asegurar que año sea entero
    
    # Iterar sobre cada mes (columnas B a M)
    for i in range(1, 13):  # 12 meses (columnas 1 a 12)
        col_name = df.columns[i]  # Obtener el nombre real de la columna
        valor = row[col_name]  # Usar el nombre de la columna para acceder al valor
        
        if not pd.isna(valor):
            # Crear fecha (primer día del mes)
            fecha = datetime.datetime(año, i, 1)
            
            # Formatear el valor con coma como separador decimal
            valor_str = str(valor).replace('.', ',')
            
            # Agregar a resultados
            resultados.append((fecha, valor_str))

# Ordenar por fecha (año y mes)
resultados.sort(key=lambda x: x[0])

# Crear el contenido del archivo de texto
contenido = ""
for fecha, valor in resultados:
    contenido += f'("{fecha.strftime("%Y-%m-%d %H:%M:%S")}", "{valor}"),\n'

# Quitar la última coma y nueva línea
contenido = contenido.rstrip(',\n')

# Guardar en archivo de texto
with open('resultados.txt', 'w', encoding='utf-8') as f:
    f.write(contenido)

print("Archivo 'resultados.txt' generado exitosamente")
print(f"Se procesaron {len(resultados)} registros")