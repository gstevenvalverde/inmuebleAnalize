import csv
import psycopg2

# Conexión a la base de datos PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    port="5432",
    database="inmueblesbi",
    user="postgres",
    password="password"
)
cur = conn.cursor()

# Ruta del archivo CSV
ruta_csv = './inmuebles_sin_nan.csv'

# Lee el archivo CSV y carga cada fila en la base de datos
with open(ruta_csv, 'r') as archivo_csv:
    lector_csv = csv.reader(archivo_csv)

    # Lee la primera fila (encabezado) para los nombres de columna
    columnas = next(lector_csv)

    # Inserta cada fila en la tabla de la base de datos
    for fila in lector_csv:
        valores = tuple(fila)

        # Construye el comando SQL para la inserción
        consulta_sql = f"INSERT INTO inmueblesapp_propiedad ({', '.join(columnas)}) VALUES ({', '.join(['%s'] * len(valores))})"

        # Ejecuta la consulta SQL con los valores de la fila
        cur.execute(consulta_sql, valores)

    # Confirma los cambios
    conn.commit()

# Cierra el cursor y la conexión
cur.close()
conn.close()
