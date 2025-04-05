import graphene
from graphene_django.types import DjangoObjectType
from .models import Job

class JobType(DjangoObjectType):
    class Meta:
        model = Job

class Query(graphene.ObjectType):
    all_jobs = graphene.List(JobType)

    def resolve_all_jobs(self, info):
        return Job.objects.all()

schema = graphene.Schema(query=Query)

