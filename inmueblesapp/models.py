from django.db import models

# Create your models here.
class Propiedad(models.Model):
    id = models.AutoField(primary_key=True)  # AutoField para el ID
    date_published = models.DateTimeField()  # Para fechas, es mejor usar DateTimeField
    date_sold = models.DateTimeField(null=True, blank=True)  # Permitir que sea nulo
    price = models.IntegerField()
    bedrooms = models.IntegerField()
    bathrooms = models.FloatField()
    sqm_living = models.FloatField()
    sqm_lot = models.FloatField()
    floors = models.FloatField()
    view = models.IntegerField(null=True, blank=True) # Permitir que sea nulo
    condition = models.IntegerField()
    grade = models.IntegerField()
    sqm_above = models.FloatField()
    sqm_basement = models.FloatField()
    yr_built = models.IntegerField()
    yr_renovated = models.IntegerField(null=True, blank=True)  # Permitir que sea nulo
    lat = models.FloatField()
    long = models.FloatField()
    city = models.CharField(max_length=100)  # Ajusta el tamaño según tus necesidades
    zone = models.CharField(max_length=100)  # Ajusta el tamaño según tus necesidades
