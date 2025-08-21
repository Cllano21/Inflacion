import pandas as pd
import datetime

# Leer el archivo Excel (solo columnas A a M)
df = pd.read_excel('SERIE HISTORICA IPC_07_2025.xls', sheet_name='1. ÍNDICE', header=5, usecols="A:M")

# Renombrar la primera columna a 'año'
df = df.rename(columns={df.columns[0]: 'año'})

# Eliminar filas con valores NaN en la columna año y convertir a entero
df = df.dropna(subset=['año'])
df['año'] = df['año'].astype(int)

# Crear lista para almacenar los resultados
resultados = []

# Iterar sobre cada fila
for _, row in df.iterrows():
    año = row['año']
    
    # Iterar sobre cada mes (columnas B a M)
    for i in range(1, 13):  # 12 meses (columnas 1 a 12)
        valor = row[i]  # Columna i corresponde al mes i
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