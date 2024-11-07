import graphene
from graphene_django import DjangoObjectType
import pandas as pd
from graphene import ObjectType, Field, List, String, Float, Int
from inmueblesapp.models import Propiedad
from django.db import connection

class PropiedadType(DjangoObjectType):
    class Meta:
        model = Propiedad
        fields = (
            "id",
            "date_published",
            "date_sold",
            "price",
            "bedrooms",
            "bathrooms",
            "sqm_living",
            "sqm_lot",
            "floors",
            "view",
            "condition",
            "grade",
            "sqm_above",
            "sqm_basement",
            "yr_built",
            "yr_renovated",
            "lat",
            "long",
            "city",
            "zone",
        )

class PrecioPromedioPorZonaYCiudadType(ObjectType):
    zona = String()
    ciudad = String()
    precio_promedio_por_m2 = Float()

class PrecioPromedioPorCiudadType(ObjectType):
    ciudad = String()
    precio_promedio_por_m2 = Float()

class GoogleChartsRowType(ObjectType):
    zona = String()
    ciudad = String()
    precio_promedio_por_m2 = Float()

class TasaConversionPorCiudadType(ObjectType):
    ciudad = String()
    tasa_conversion = Float()

class PromedioTiempoMercadoPorZonaYCiudadType(ObjectType):
    ciudad = String()
    zona = String()
    promedio_dias_en_venta = Float()

class PromedioTiempoMercadoPorCiudadType(ObjectType):
    ciudad = String()
    promedio_dias_en_venta = Int()

class CantidadPropiedadesPorCiudadYZonaType(ObjectType):
    ciudad = String()
    zona = String()
    cantidad_propiedades = Int()

class PropiedadesVendidasPorZoneType(ObjectType):
    zona = String()
    vendidos = Int()
    no_vendidos = Int()

class PrecioPromedioPorZonaType(ObjectType):
    zona = String()
    precio_promedio_por_m2 = Float()

class PromedioTiempoMercadoPorZonaType(ObjectType):
    zona = String()
    promedio_dias_en_venta = Float()

class ZoneType(ObjectType):
    zone = String()

class Query(graphene.ObjectType):
    propiedades = graphene.List(PropiedadType)
    calcular_precio_promedio_por_zona_ciudad = List(PrecioPromedioPorZonaYCiudadType)
    calcular_precio_promedio_por_ciudad = List(PrecioPromedioPorCiudadType)
    obtener_datos_para_google_charts = List(GoogleChartsRowType)
    calcular_tasa_conversion_por_ciudad = List(TasaConversionPorCiudadType)
    calcular_promedio_tiempo_mercado_por_zona_y_ciudad = List(PromedioTiempoMercadoPorZonaYCiudadType)
    calcular_promedio_tiempo_mercado_por_ciudad = List(PromedioTiempoMercadoPorCiudadType)
    calcular_cantidad_propiedades_por_ciudad_y_zona = List(CantidadPropiedadesPorCiudadYZonaType)

    propiedades_vendidas_por_zona = graphene.List(PropiedadesVendidasPorZoneType, zone=graphene.String(required=True))
    precio_m2_por_zona = graphene.List(PrecioPromedioPorZonaType, zone=graphene.String(required=True))
    calcular_promedio_tiempo_mercado_por_zona = graphene.List(PromedioTiempoMercadoPorZonaType, zone=graphene.String(required=True))
    obtener_zonas_unicas = graphene.List(ZoneType)

    def resolve_propiedades(self, info):
        return Propiedad.objects.all()

    def resolve_calcular_precio_promedio_por_zona_ciudad(self, info):
        # Consulta SQL para cargar los datos desde PostgreSQL
        query = "SELECT price, sqm_living, zone, city FROM inmueblesapp_propiedad"
        data_frame = pd.read_sql_query(query, connection)

        # Evitar divisiones por cero
        data_frame = data_frame[data_frame['sqm_living'] > 0]

        # Calcular el precio por metro cuadrado para cada propiedad
        data_frame['precio_por_m2'] = data_frame['price'] / data_frame['sqm_living']

        # Agrupar por zona y ciudad y calcular el precio por m2 promedio
        grouped_data = data_frame.groupby(['zone', 'city'])['precio_por_m2'].mean().reset_index()

        # Convertir los resultados en una lista de objetos que GraphQL pueda devolver
        result = [
            {
                'zona': row['zone'],
                'ciudad': row['city'],
                'precio_promedio_por_m2': row['precio_por_m2']
            }
            for _, row in grouped_data.iterrows()
        ]

        return result

    def resolve_calcular_precio_promedio_por_ciudad(self, info):
        # Consulta SQL para cargar los datos desde PostgreSQL
        query = "SELECT price, sqm_living, city FROM inmueblesapp_propiedad"
        data_frame = pd.read_sql_query(query, connection)

        # Evitar divisiones por cero
        data_frame = data_frame[data_frame['sqm_living'] > 0]

        # Calcular el precio por metro cuadrado para cada propiedad
        data_frame['precio_por_m2'] = data_frame['price'] / data_frame['sqm_living']

        # Agrupar por zona y ciudad y calcular el precio por m2 promedio
        grouped_data = data_frame.groupby(['city'])['precio_por_m2'].mean().reset_index()

        # Convertir los resultados en una lista de objetos que GraphQL pueda devolver
        result = [
            {
                'ciudad': row['city'],
                'precio_promedio_por_m2': row['precio_por_m2']
            }
            for _, row in grouped_data.iterrows()
        ]

        return result


    def resolve_obtener_datos_para_google_charts(self, info):
        # Consulta SQL para cargar los datos desde PostgreSQL
        query = "SELECT price, sqm_living, zone, city FROM inmueblesapp_propiedad"
        data_frame = pd.read_sql_query(query, connection)

        # Evitar divisiones por cero
        data_frame = data_frame[data_frame['sqm_living'] > 0]

        # Calcular el precio por metro cuadrado
        data_frame['precio_por_m2'] = data_frame['price'] / data_frame['sqm_living']

        # Agrupar por zona y ciudad y calcular el precio promedio por m2
        grouped_data = data_frame.groupby(['zone', 'city'])['precio_por_m2'].mean().reset_index()

        # Convertir el DataFrame en una lista de objetos que GraphQL pueda devolver
        result = [
            GoogleChartsRowType(
                zona=row['zone'],
                ciudad=row['city'],
                precio_promedio_por_m2=row['precio_por_m2']
            )
            for _, row in grouped_data.iterrows()
        ]

        return result

    def resolve_calcular_tasa_conversion_por_ciudad(self, info):
        # Consulta SQL para cargar los datos desde PostgreSQL
        query = "SELECT view, date_sold, city FROM inmueblesapp_propiedad"
        data_frame = pd.read_sql_query(query, connection)

        # Filtrar propiedades que han sido visitadas al menos una vez
        data_frame = data_frame[data_frame['view'] > 0]

        # Crear una columna que indique si la propiedad fue vendida (date_sold no es nulo)
        data_frame['vendido'] = data_frame['date_sold'].notnull()

        # Agrupar por ciudad y calcular la tasa de conversión (porcentaje de vendidos respecto a visitados)
        grouped_data = data_frame.groupby('city').agg(
            total_visitados=('view', 'count'),
            total_vendidos=('vendido', 'sum')
        ).reset_index()

        # Calcular la tasa de conversión como porcentaje
        grouped_data['tasa_conversion'] = (grouped_data['total_vendidos'] / grouped_data['total_visitados']) * 100

        # Convertir los resultados en una lista de objetos que GraphQL pueda devolver
        result = [
            TasaConversionPorCiudadType(
                ciudad=row['city'],
                tasa_conversion=row['tasa_conversion']
            )
            for _, row in grouped_data.iterrows()
        ]

        return result

    def resolve_calcular_promedio_tiempo_mercado_por_zona_y_ciudad(self, info):
        # Consulta SQL para cargar los datos desde PostgreSQL
        query = "SELECT date_published, date_sold, city, zone FROM inmueblesapp_propiedad WHERE date_sold IS NOT NULL"
        data_frame = pd.read_sql_query(query, connection)

        # Convertir las columnas de fecha a tipo datetime
        data_frame['date_published'] = pd.to_datetime(data_frame['date_published'])
        data_frame['date_sold'] = pd.to_datetime(data_frame['date_sold'])

        # Calcular la diferencia en días entre la fecha de venta y la fecha de publicación
        data_frame['dias_en_venta'] = (data_frame['date_sold'] - data_frame['date_published']).dt.days

        # Agrupar por ciudad y zona y calcular el promedio de días en venta
        grouped_data = data_frame.groupby(['city', 'zone'])['dias_en_venta'].mean().reset_index()

        # Convertir los resultados en una lista de objetos que GraphQL pueda devolver
        result = [
            PromedioTiempoMercadoPorZonaYCiudadType(
                ciudad=row['city'],
                zona=row['zone'],
                promedio_dias_en_venta=row['dias_en_venta']
            )
            for _, row in grouped_data.iterrows()
        ]

        return result

    def resolve_calcular_promedio_tiempo_mercado_por_ciudad(self, info):
        # Consulta SQL para cargar los datos desde PostgreSQL
        query = "SELECT date_published, date_sold, city FROM inmueblesapp_propiedad WHERE date_sold IS NOT NULL"
        data_frame = pd.read_sql_query(query, connection)

        # Convertir las columnas de fecha a tipo datetime
        data_frame['date_published'] = pd.to_datetime(data_frame['date_published'])
        data_frame['date_sold'] = pd.to_datetime(data_frame['date_sold'])

        # Calcular la diferencia en días entre la fecha de venta y la fecha de publicación
        data_frame['dias_en_venta'] = (data_frame['date_sold'] - data_frame['date_published']).dt.days

        # Agrupar por ciudad y zona y calcular el promedio de días en venta
        grouped_data = data_frame.groupby(['city'])['dias_en_venta'].mean().reset_index()

        # Entero del promedio de días en venta
        grouped_data['dias_en_venta'] = grouped_data['dias_en_venta'].astype(int)

        # Convertir los resultados en una lista de objetos que GraphQL pueda devolver
        result = [
            PromedioTiempoMercadoPorCiudadType(
                ciudad=row['city'],
                promedio_dias_en_venta=row['dias_en_venta']
            )
            for _, row in grouped_data.iterrows()
        ]

        return result

    def resolve_calcular_cantidad_propiedades_por_ciudad_y_zona(self, info):
        # Consulta SQL para cargar los datos desde PostgreSQL
        query = "SELECT city, zone FROM inmueblesapp_propiedad"
        data_frame = pd.read_sql_query(query, connection)

        # Agrupar por ciudad y zona y contar el número de propiedades
        grouped_data = data_frame.groupby(['city', 'zone']).size().reset_index(name='cantidad_propiedades')

        # Convertir los resultados en una lista de objetos que GraphQL pueda devolver
        result = [
            CantidadPropiedadesPorCiudadYZonaType(
                ciudad=row['city'],
                zona=row['zone'],
                cantidad_propiedades=row['cantidad_propiedades']
            )
            for _, row in grouped_data.iterrows()
        ]

        return result

    def resolve_propiedades_vendidas_por_zona(self, info, zone):
        # Obtén la cantidad de propiedades vendidas y no vendidas para la zona solicitada
        total_vendidos = Propiedad.objects.filter(zone=zone, date_sold__isnull=False).count()
        total_no_vendidos = Propiedad.objects.filter(zone=zone, date_sold__isnull=True).count()

        # Estructura los datos en el formato solicitado
        result = [PropiedadesVendidasPorZoneType(
                zona = zone,
                vendidos = total_vendidos,
                no_vendidos= total_no_vendidos,
            )]

        return result

    def resolve_precio_m2_por_zona(self, info, zone):
        # Extrae las propiedades en la zona específica
        propiedades = Propiedad.objects.filter(zone=zone).values('zone', 'price', 'sqm_living')

        # Convierte los resultados a un DataFrame de Pandas
        df = pd.DataFrame(list(propiedades))

        # Verifica que el DataFrame no esté vacío
        if df.empty:
            return PrecioPromedioPorZonaType(zona=zone, precio_promedio_por_m2=None)

        # Filtra filas sin valores de `sqm_living` o `price`
        df = df[(df['sqm_living'] > 0) & (df['price'] > 0)]

        # Calcula el precio promedio por metro cuadrado
        df['precio_por_m2'] = df['price'] / df['sqm_living']
        precio_promedio_por_m2 = round(df['precio_por_m2'].mean(), 2)

        # Estructura los datos en el formato solicitado
        result = [PrecioPromedioPorZonaType(
            zona=zone,
            precio_promedio_por_m2=precio_promedio_por_m2
        )]
        return result

    def resolve_calcular_promedio_tiempo_mercado_por_zona(self, info, zone):
        # Consulta SQL para cargar los datos de propiedades vendidas de la zona especificada
        query = f"""
        SELECT date_published, date_sold, zone 
        FROM inmueblesapp_propiedad 
        WHERE date_sold IS NOT NULL AND zone = %s
        """
        data_frame = pd.read_sql_query(query, connection, params=[zone])

        # Verifica que haya datos en la zona especificada
        if data_frame.empty:
            return []

        # Convertir las columnas de fecha a tipo datetime
        data_frame['date_published'] = pd.to_datetime(data_frame['date_published'])
        data_frame['date_sold'] = pd.to_datetime(data_frame['date_sold'])

        # Calcular la diferencia en días entre la fecha de venta y la fecha de publicación
        data_frame['dias_en_venta'] = (data_frame['date_sold'] - data_frame['date_published']).dt.days

        # Calcular el promedio de días en venta para la zona
        promedio_dias_en_venta = round(data_frame['dias_en_venta'].mean(), 2)

        # Convertir los resultados en una lista de objetos que GraphQL pueda devolver
        result = [
            PromedioTiempoMercadoPorZonaType(
                zona=zone,
                promedio_dias_en_venta=promedio_dias_en_venta  # Redondear a dos decimales
            )
        ]

        return result

    def resolve_obtener_zonas_unicas(self, info):
        # Realiza la consulta para obtener zonas únicas desde la base de datos
        zonas_unicas = Propiedad.objects.values('zone').distinct()

        # Convertir el resultado a una lista de objetos de tipo ZoneType
        result = [ZoneType(zone=z['zone']) for z in zonas_unicas]

        return result

schema = graphene.Schema(query=Query)


