from django.db import models

# Create your models here.
class Activos(models.Model):
    id = models.CharField(max_length=100, auto_created=False, primary_key=True, verbose_name="ID")
    nombre = models.CharField(max_length=100, null=False, verbose_name="Nombre")