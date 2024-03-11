from django.db import models

from vehicles.models import Vehicle


class DeliveryJob(models.Model):
    """
    Represents a single delivery job, including vehicle assignment, destination,
    financial details, and time range for the delivery.

    Attributes:
        vehicle (ForeignKey): The vehicle assigned to the delivery job.
        created_at (DateTimeField): Timestamp when the job was created.
        completed_at (DateTimeField): Timestamp when the job was completed (if applicable).
        destination (ForeignKey): The address where the delivery is to be made.
        income (DecimalField): The revenue generated from the delivery.
        cost (DecimalField): The expenses associated with the delivery.
        delivery_slot_starts_at (DateTimeField): The start datetime designated for the delivery slot.
        delivery_slot_ends_at (DateTimeField): The end datetime designated for the delivery slot.
    """

    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="delivery_jobs",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    destination = models.ForeignKey(
        "jobs.Address", on_delete=models.CASCADE, related_name="delivery_jobs"
    )  # Use a fk in case of multiple jobs for the same address
    income = models.DecimalField(max_digits=6, decimal_places=2)  # In USD
    cost = models.DecimalField(max_digits=6, decimal_places=2)  # In USD
    delivery_slot_starts_at = models.DateTimeField()
    delivery_slot_ends_at = models.DateTimeField()

    def __str__(self):
        """Provides a human-readable string representation of a DeliveryJob object."""
        return f"{self.vehicle} delivery for {self.destination}{f'(completed @ {self.completed_at})' if self.completed else ''}"

    @property
    def completed(self):
        """Indicates if a delivery job has been completed."""
        return self.completed_at is not None


class Address(models.Model):
    """
    Represents a US-based address for a delivery destination.

    Attributes:
        recipient (CharField): The name of the recipient of the delivery.
        street_address (CharField): The primary street address line.
        street_address_2 (CharField): Optional secondary address line (e.g., apartment number).
        city (CharField): The city name.
        state (CharField): The two-letter US state abbreviation.
        zip_code (CharField): The ZIP code.
    """

    recipient = models.CharField(max_length=100)
    street_address = models.CharField(max_length=100)
    street_address_2 = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=2)
    zip_code = models.CharField(max_length=10)

    def __str__(self):
        """Provides a human-readable string representation of an Address object."""
        return self.street_address
