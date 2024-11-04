import graphene
from graphene_django import DjangoObjectType
from inmueblesapp.models import Propiedad

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

class Query(graphene.ObjectType):
    propiedades = graphene.List(PropiedadType)

    def resolve_propiedades(self, info):
        return Propiedad.objects.all()

schema = graphene.Schema(query=Query)


