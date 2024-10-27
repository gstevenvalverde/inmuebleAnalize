import graphene
from graphene_django import DjangoObjectType
from inmueblesapp.models import Propiedad

class PropiedadType(DjangoObjectType):
    class Meta:
        model = Propiedad
        fields = ("id", 'titulo', 'tipodepropiedad', 'direccion')

class Query(graphene.ObjectType):
    propiedades = graphene.List(PropiedadType)

    def resolve_propiedades(self, info, **kwargs):
        return Propiedad.objects.all()

schema = graphene.Schema(query=Query)


