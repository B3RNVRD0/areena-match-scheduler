import graphene
from .query import Query
# from .mutation import Mutation 

# Defina sua classe Schema que agrupa Query e Mutation
class Schema(graphene.ObjectType):
    query = Query
    # mutation = Mutation 

schema = graphene.Schema(query=Query) 