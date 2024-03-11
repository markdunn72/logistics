import graphene

import vehicles.schema
import jobs.schema


class Query(vehicles.schema.Query, jobs.schema.Query,graphene.ObjectType):
    pass


class Mutation(vehicles.schema.Mutation, jobs.schema.Mutation, graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
