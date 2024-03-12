from decimal import Decimal

import graphene
from django_filters import FilterSet
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from graphene_django.types import Connection
from graphql_relay import from_global_id

from jobs.models import Address, DeliveryJob
from vehicles.models import Vehicle


class AddressType(DjangoObjectType):
    """
    Represents an Address with its fields.
    """

    class Meta:
        model = Address
        interfaces = (graphene.relay.Node,)
        fields = "__all__"


class DeliveryJobFilter(FilterSet):
    """Provides filtering options for DeliveryJob queries"""

    vehicle = graphene.Field("vehicles.schema.VehicleType")
    destination = graphene.Field(AddressType)

    class Meta:
        model = DeliveryJob
        fields = {
            "vehicle__registration": ("exact", "contains", "isnull"),
            "destination__recipient": ("exact", "contains", "startswith", "endswith"),
            "destination__street_address": (
                "exact",
                "contains",
                "startswith",
                "endswith",
            ),
            "destination__street_address_2": (
                "exact",
                "contains",
                "startswith",
                "endswith",
            ),
            "destination__city": ("exact", "contains", "startswith", "endswith"),
            "destination__state": ("exact", "contains", "startswith", "endswith"),
            "destination__zip_code": ("exact", "contains", "startswith", "endswith"),
            "created_at": ("exact", "lt", "lte", "gt", "gte"),
            "completed_at": ("exact", "lt", "lte", "gt", "gte", "isnull"),
            "income": ("exact", "lt", "lte", "gt", "gte"),
            "cost": ("exact", "lt", "lte", "gt", "gte"),
            "delivery_slot_starts_at": ("exact", "lt", "lte", "gt", "gte"),
            "delivery_slot_ends_at": ("exact", "lt", "lte", "gt", "gte"),
        }


class DeliveryJobConnection(Connection):
    """
    A paginated connection that includes a count of items on the current page.
    """

    class Meta:
        abstract = True

    currentPageCount = graphene.Int()
    totalIncome = graphene.Decimal()
    totalCost = graphene.Decimal()

    def resolve_currentPageCount(self, info, **kwargs):
        """
        Returns the number of items (edges) within the current page.
        """
        return len(self.edges)

    def resolve_totalIncome(self, info, **kwargs):
        """Calculates the total income for the current page."""
        return Decimal(sum(edge.node.income for edge in self.edges))

    def resolve_totalCost(self, info, **kwargs):
        """Calculates the total cost for the current page."""
        return Decimal(sum(edge.node.cost for edge in self.edges))


class DeliveryJobType(DjangoObjectType):
    """
    Represents a DeliveryJob, along with its relationships and fields.
    """

    vehicle = graphene.Field("vehicles.schema.VehicleType")

    class Meta:
        model = DeliveryJob
        interfaces = (graphene.relay.Node,)
        fields = "__all__"
        filterset_class = DeliveryJobFilter
        connection_class = DeliveryJobConnection


class Query(graphene.ObjectType):
    """
    Root-level query fields for accessing and filtering DeliveryJob data.
    """

    delivery_jobs = DjangoFilterConnectionField(DeliveryJobType)


class AddressInput(graphene.InputObjectType):
    """
    Input type representing address data for creating new addresses.
    """

    recipient = graphene.String(required=True)
    street_address = graphene.String(required=True)
    street_address_2 = graphene.String()
    city = graphene.String(required=True)
    state = graphene.String(required=True)
    zip_code = graphene.String(required=True)


class CreateJobInput(graphene.InputObjectType):
    """
    Input type containing data required for creating a new DeliveryJob.
    """

    destination = graphene.Field(AddressInput, required=True)
    income = graphene.Decimal(required=True)
    cost = graphene.Decimal(required=True)
    delivery_slot_starts_at = graphene.DateTime(required=True)
    delivery_slot_ends_at = graphene.DateTime(required=True)
    vehicle_registration = graphene.String()


class CreateJob(graphene.Mutation):
    """
    Mutation for creating new DeliveryJob instances.
    """

    class Arguments:
        input = CreateJobInput(required=True)

    job = graphene.Field(DeliveryJobType)

    @staticmethod
    def mutate(root, info, input):
        """
        Performs the mutation logic, creates a DeliveryJob, and returns the created instance.
        """
        address = Address.objects.create(**input.destination)
        job_kwargs = {
            "destination": address,
            "income": input.income,
            "cost": input.cost,
            "delivery_slot_starts_at": input.delivery_slot_starts_at,
            "delivery_slot_ends_at": input.delivery_slot_ends_at,
        }
        if input.get("vehicle_registration"):
            try:
                vehicle = Vehicle.objects.get(registration=input.vehicle_registration)
                job_kwargs["vehicle"] = vehicle
            except Vehicle.DoesNotExist:
                raise Exception("Vehicle with specified registration not found.")

        job = DeliveryJob.objects.create(**job_kwargs)
        return CreateJob(job=job)


class MarkJobCompletedInput(graphene.InputObjectType):
    """Input type for marking a job as completed."""

    id = graphene.ID(required=True)
    completed_at = graphene.DateTime(
        required=True
    )  # Client expected to send time in UTC


class MarkJobCompleted(graphene.Mutation):
    """Mutation for marking a job as completed."""

    class Arguments:
        input = MarkJobCompletedInput(required=True)

    job = graphene.Field(DeliveryJobType)

    @staticmethod
    def mutate(root, info, input):
        """Performs logic to mark a job as completed."""
        internal_id = from_global_id(
            input.id
        ).id  # Convert global ID to internal database ID
        job = DeliveryJob.objects.get(id=internal_id)

        # Check vehicle has been assigned before completing job
        if not job.vehicle:
            raise Exception(
                "Job must have an assigned vehicle to mark it as completed."
            )

        # Check job is not already marked as completed
        if job.completed_at is not None:
            raise Exception(
                f"Job has already been marked as completed at {job.completed_at}."
            )

        # Do not check completion date falls within delivery slot - too restrictive

        job.completed_at = input.completed_at
        job.save()
        return MarkJobCompleted(job=job)


class Mutation(graphene.ObjectType):
    """Root-level mutation fields."""

    create_job = CreateJob.Field()
    mark_job_completed = MarkJobCompleted.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
