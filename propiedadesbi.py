import requests
import pandas as pd

# URL del endpoint GraphQL
url = 'http://localhost:8000/graphql/'

# Consulta GraphQL para obtener las propiedades
query = """
{
  propiedades {
    city
    zone
    price
    sqmLiving
    price
  }
}
"""

response = requests.post(url, json={'query': query})

# Si la respuesta es exitosa
if response.status_code == 200:
    data = response.json()['data']['propiedades']

    # Crear un DataFrame de Pandas
    df = pd.DataFrame(data)
    print(df.head())
    print(df.columns)

    # Convertir la columna 'price' a tipo numérico si es necesario
    df['price'] = pd.to_numeric(df['price'])

    # Desactivar la notación científica en pandas para mostrar números más legibles
    pd.set_option('display.float_format', '{:.2f}'.format)

    # Calcular el promedio de precio por ciudad y zona
    avg_price = df.groupby(['city', 'zone'])['price'].mean().reset_index()

    # Mostrar el DataFrame con los promedios
    print(avg_price)

    # Preparar los datos para Google Charts
    chart_data = avg_price[['city', 'zone', 'price']].values.tolist()

    # Ver el formato de los datos
    print(chart_data)

    # Calcular el precio por metro cuadrado
    df['price_per_sqm'] = df['price'] / df['sqmLiving']

    # Calcular el promedio del precio por metro cuadrado por ciudad y zona
    avg_price_per_sqm = df.groupby(['city', 'zone'])['price_per_sqm'].mean().reset_index()

    # Desactivar la notación científica en pandas
    pd.set_option('display.float_format', '{:.2f}'.format)

    # Mostrar el DataFrame resultante
    print(avg_price_per_sqm)

else:
    print(f"Error: {response.status_code}")
    print(response.text)
