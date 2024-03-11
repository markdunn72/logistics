import factory
from factory.django import DjangoModelFactory

from vehicles.models import Vehicle


class VehicleFactory(DjangoModelFactory):
    class Meta:
        model = Vehicle

    registration = factory.Faker("license_plate")
