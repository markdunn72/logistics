from datetime import timedelta

import factory
from factory.django import DjangoModelFactory

from jobs.models import DeliveryJob, Address
from vehicles.factories import VehicleFactory


class DeliveryJobFactory(DjangoModelFactory):
    class Meta:
        model = DeliveryJob

    destination = factory.SubFactory("jobs.factories.AddressFactory")
    vehicle = factory.SubFactory(VehicleFactory)
    income = factory.Faker("pydecimal", left_digits=4, right_digits=2, positive=True)
    cost = factory.Faker("pydecimal", left_digits=3, right_digits=2, positive=True)
    delivery_slot_starts_at = factory.Faker("date_time_this_year")
    delivery_slot_ends_at = factory.LazyAttribute(
        lambda obj: obj.delivery_slot_starts_at
        + timedelta(
            hours=factory.Faker("pyint", min_value=1, max_value=6).evaluate(
                None, None, extra={"locale": "en_US"}
            )
        )
    )


class AddressFactory(DjangoModelFactory):
    class Meta:
        model = Address

    recipient = factory.Faker("name")
    street_address = factory.Faker("street_address")
    street_address_2 = factory.Faker("secondary_address")
    city = factory.Faker("city")
    state = factory.Faker("state_abbr")
    zip_code = factory.Faker("zipcode")
