# alx_backend_graphql_crm/schema.py
import graphene
import crm.schema as crm_schema


class Query(crm_schema.CustomerType, graphene.ObjectType):
    # declare the field
    hello = graphene.String(description="A simple hello field")

    # resolver for the field
    def resolve_hello(self, info):
        return "Hello, GraphQL!"
    
class Mutation(crm_schema.Mutation, graphene.ObjectType):
    pass
# public schema object (Graphene expects this)
schema = graphene.Schema(query=Query, mutation=Mutation)



