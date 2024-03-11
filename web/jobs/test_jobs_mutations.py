import pytest
from django.utils import timezone
from graphql_relay.node.node import to_global_id
from graphene.test import Client

from jobs.factories import DeliveryJobFactory
from jobs.schema import schema
from vehicles.factories import VehicleFactory


@pytest.fixture
def client():
    return Client(schema)


@pytest.fixture
def job_without_vehicle(db):
    return DeliveryJobFactory(vehicle=None)


@pytest.fixture
def job_with_vehicle(db):
    return DeliveryJobFactory()


@pytest.fixture
def completed_job(db):
    return DeliveryJobFactory(completed_at=timezone.now())


def test_mark_job_completed_no_vehicle(client, job_without_vehicle):
    assert job_without_vehicle.completed_at is None
    assert job_without_vehicle.vehicle is None

    mutation = """
        mutation MarkJobCompleted($input: MarkJobCompletedInput!) {
            markJobCompleted(input: $input) {
                job { 
                  id
                }
            }
        }
    """

    response = client.execute(
        mutation,
        variables={
            "input": {
                "id": to_global_id("DeliveryJobType", job_without_vehicle.id),
                "completedAt": "2024-12-25T10:00:00Z",
            }
        },
    )

    assert "errors" in response  # Should have errors
    assert "Job must have an assigned vehicle" in response["errors"][0]["message"]


def test_mark_job_completed_already_completed(client, completed_job):
    assert completed_job.completed_at is not None
    assert completed_job.vehicle is not None

    mutation = """
        mutation MarkJobCompleted($input: MarkJobCompletedInput!) {
            markJobCompleted(input: $input) {
                job { 
                  id
                }
            }
        }
    """

    response = client.execute(
        mutation,
        variables={
            "input": {
                "id": to_global_id("DeliveryJobType", completed_job.id),
                "completedAt": "2024-12-25T10:00:00Z",
            }
        },
    )

    assert "errors" in response
    assert (
        "Job has already been marked as completed" in response["errors"][0]["message"]
    )
