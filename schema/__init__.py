import graphene
from .query import Query
from .mutation import Mutation 

class Schema(graphene.ObjectType):
    query = Query
    mutation = Mutation 

schema = graphene.Schema(query=Query, mutation=Mutation) 