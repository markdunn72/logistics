import graphene
from django.db import IntegrityError
from django.db.models import Sum
from django_filters import FilterSet, OrderingFilter
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from jobs.models import DeliveryJob
from vehicles.models import Vehicle


class VehicleFilter(FilterSet):
    """Provides filtering options for DeliveryJob queries"""

    delivery_jobs = graphene.List("jobs.schema.DeliveryJobType")

    order_by = OrderingFilter(fields=("total_income", "total_cost"))

    class Meta:
        model = Vehicle
        fields = {
            "registration": ("exact", "contains", "isnull"),
            "delivery_jobs__created_at": ("exact", "lt", "lte", "gt", "gte"),
            "delivery_jobs__completed_at": (
                "exact",
                "lt",
                "lte",
                "gt",
                "gte",
                "isnull",
            ),
            "delivery_jobs__income": ("exact", "lt", "lte", "gt", "gte"),
            "delivery_jobs__cost": ("exact", "lt", "lte", "gt", "gte"),
            "delivery_jobs__delivery_slot_starts_at": (
                "exact",
                "lt",
                "lte",
                "gt",
                "gte",
            ),
            "delivery_jobs__delivery_slot_ends_at": ("exact", "lt", "lte", "gt", "gte"),
        }


class VehicleType(DjangoObjectType):
    """Represents a Vehicle with its fields and relationships."""
    total_income = graphene.Decimal()
    total_cost = graphene.Decimal()

    class Meta:
        model = Vehicle
        interfaces = (graphene.relay.Node,)
        fields = "__all__"
        filterset_class = VehicleFilter


class Query(graphene.ObjectType):
    """Root-level query fields for retrieving Vehicle data."""

    vehicle_by_registration = graphene.Field(
        VehicleType,
        registration=graphene.String(required=True),
        description="Fetches a Vehicle object based on its registration number.",
    )
    vehicles = DjangoFilterConnectionField(VehicleType, filterset_class=VehicleFilter)

    def resolve_vehicle_by_registration(self, info, registration):
        """Resolver for the 'vehicle_by_registration' query field. Retrieves a single Vehicle."""
        return Vehicle.objects.filter(registration=registration).first()

    def resolve_vehicles(self, info, **kwargs):
        queryset = VehicleFilter(kwargs).qs.annotate(
            total_income=Sum("delivery_jobs__income"),
            total_cost=Sum("delivery_jobs__cost"),
        )

        return queryset.distinct()


class CreateVehicleInput(graphene.InputObjectType):
    """Input type for creating new Vehicle objects."""

    registration = graphene.String(
        required=True, description="The vehicle's registration number."
    )


class CreateVehicle(graphene.Mutation):
    """Mutation for creating a new Vehicle."""

    class Arguments:
        input = CreateVehicleInput(required=True)

    success = graphene.Boolean(
        description="Indicates whether the vehicle creation was successful."
    )
    vehicle = graphene.Field(
        VehicleType, description="The newly created Vehicle object."
    )

    @staticmethod
    def mutate(root, info, input):
        """
        Performs the vehicle creation logic, handles potential IntegrityErrors,
        and returns the result.
        """
        try:
            vehicle = Vehicle.objects.create(registration=input.registration)
            return CreateVehicle(success=True, vehicle=vehicle)
        except IntegrityError:
            return CreateVehicle(success=False, vehicle=None)


class AssignVehicleToJobsInput(graphene.InputObjectType):
    """Input type for assigning a vehicle to multiple jobs."""

    vehicle_registration = graphene.String(
        required=True, description="The registration number of the vehicle."
    )
    job_ids = graphene.List(
        graphene.NonNull(graphene.ID),
        required=True,
        description="List of global IDs for the target jobs.",
    )


class AssignVehicleToJobs(graphene.Mutation):
    """Mutation for assigning a vehicle to a set of DeliveryJob instances."""

    class Arguments:
        input = AssignVehicleToJobsInput(required=True)

    success = graphene.Boolean(
        description="Indicates if the vehicle assignment was successful."
    )
    jobs = graphene.List(
        "jobs.schema.DeliveryJobType", description="The updated DeliveryJob instances."
    )

    @staticmethod
    def mutate(root, info, input):
        """
        Performs the vehicle assignment logic, handles potential errors,
        and returns the result.
        """
        try:
            vehicle = Vehicle.objects.get(registration=input.vehicle_registration)
            jobs = DeliveryJob.objects.filter(id__in=input.job_ids)

            jobs.update(vehicle=vehicle)
            return AssignVehicleToJobs(success=True, jobs=jobs)
        except (Vehicle.DoesNotExist, IntegrityError) as e:
            return AssignVehicleToJobs(success=False, jobs=[])


class Mutation(graphene.ObjectType):
    """Root-level mutation fields for modifying Vehicle data."""

    create_vehicle = CreateVehicle.Field()
    assign_vehicle_to_jobs = AssignVehicleToJobs.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
