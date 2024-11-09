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

class PromedioTiempoMercadoPorCiudadType(ObjectType):
    ciudad = String()
    promedio_dias_en_venta = Int()

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

class TimeSeriesDataType(graphene.ObjectType):
    fecha = graphene.Date()
    valor = graphene.Float()

class SalesSummaryType(graphene.ObjectType):
    monthly_data = List(TimeSeriesDataType)
    yearly_data = List(TimeSeriesDataType)

class Query(graphene.ObjectType):
    propiedades = graphene.List(PropiedadType)
    calcular_precio_promedio_por_ciudad = List(PrecioPromedioPorCiudadType)
    obtener_datos_para_google_charts = List(GoogleChartsRowType)
    calcular_tasa_conversion_por_ciudad = List(TasaConversionPorCiudadType)
    calcular_promedio_tiempo_mercado_por_ciudad = List(PromedioTiempoMercadoPorCiudadType)

    propiedades_vendidas_por_zona = graphene.List(PropiedadesVendidasPorZoneType, zone=graphene.String(required=True))
    precio_m2_por_zona = graphene.List(PrecioPromedioPorZonaType, zone=graphene.String(required=True))
    calcular_promedio_tiempo_mercado_por_zona = graphene.List(PromedioTiempoMercadoPorZonaType, zone=graphene.String(required=True))
    obtener_zonas_unicas = graphene.List(ZoneType)

    sales_summary = graphene.Field(SalesSummaryType)

    def resolve_propiedades(self, info):
        return Propiedad.objects.all()

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

    def resolve_sales_summary(self, info):
        # Extraer los datos de la base de datos
        ventas = Propiedad.objects.filter(date_sold__isnull=False).values('date_sold', 'price')

        # Crear un DataFrame a partir de los datos de la base de datos
        df = pd.DataFrame(list(ventas))
        df['date_sold'] = pd.to_datetime(df['date_sold'])

        # Agrupación por mes (Año y Mes) y sumatoria de ventas
        df['month'] = df['date_sold'].dt.to_period('M')  # Agrupar por Año-Mes
        monthly_summary = (
            df.groupby('month')['price'].sum()
            .reset_index()
            .sort_values('month')
        )

        # Convertir los datos de mes a un formato compatible con GraphQL
        monthly_data = [
            TimeSeriesDataType(
                fecha=period.to_timestamp().date(),
                valor=precio
            )
            for period, precio in zip(monthly_summary['month'], monthly_summary['price'])
        ]

        # Agrupación por año y sumatoria de ventas
        df['year'] = df['date_sold'].dt.to_period('Y')  # Agrupar solo por Año
        yearly_summary = (
            df.groupby('year')['price'].sum()
            .reset_index()
            .sort_values('year')
        )

        # Convertir los datos de año a un formato compatible con GraphQL
        yearly_data = [
            TimeSeriesDataType(
                fecha=period.to_timestamp().date(),
                valor=precio
            )
            for period, precio in zip(yearly_summary['year'], yearly_summary['price'])
        ]

        # Retornar los datos como objeto SalesSummaryType
        return SalesSummaryType(monthly_data=monthly_data, yearly_data=yearly_data)

class CreatePropiedad(graphene.Mutation):
    class Arguments:
        date_published = graphene.Date(required=True)
        date_sold = graphene.Date()
        price = graphene.Decimal(required=True)
        bedrooms = graphene.Int(required=True)
        bathrooms = graphene.Int(required=True)
        sqm_living = graphene.Decimal(required=True)
        sqm_lot = graphene.Decimal(required=True)
        floors = graphene.Decimal(required=True)
        view = graphene.String(required=True)
        condition = graphene.String(required=True)
        grade = graphene.Int(required=True)
        sqm_above = graphene.Decimal(required=True)
        sqm_basement = graphene.Decimal(required=True)
        yr_built = graphene.Int(required=True)
        yr_renovated = graphene.Int()
        lat = graphene.Float(required=True)
        long = graphene.Float(required=True)
        city = graphene.String(required=True)
        zone = graphene.String(required=True)

    propiedad = graphene.Field(PropiedadType)

    def mutate(self, info, **kwargs):
        propiedad = Propiedad.objects.create(**kwargs)
        return CreatePropiedad(propiedad=propiedad)

# Mutación para actualizar solo el campo date_sold
class UpdateDateSold(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        date_sold = graphene.Date(required=True)

    propiedad = graphene.Field(PropiedadType)

    def mutate(self, info, id, date_sold):
        propiedad = Propiedad.objects.get(id=id)
        propiedad.date_sold = date_sold
        propiedad.save()
        return UpdateDateSold(propiedad=propiedad)

# Mutación para incrementar el campo view en 1
class IncrementView(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)

    propiedad = graphene.Field(PropiedadType)

    def mutate(self, info, id):
        propiedad = Propiedad.objects.get(id=id)
        propiedad.view += 1
        propiedad.save()
        return IncrementView(propiedad=propiedad)

# Clase Mutation que agrupa todas las mutaciones
class Mutation(graphene.ObjectType):
    create_propiedad = CreatePropiedad.Field()
    update_date_sold = UpdateDateSold.Field()
    increment_view = IncrementView.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)


