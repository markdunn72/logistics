from django.db import models


class Vehicle(models.Model):
    """
    Represents a vehicle with its primary identifier, the registration number.

    Attributes:
        registration (CharField): The vehicle's registration number, acting as its unique identifier.
    """

    registration = models.CharField(max_length=10, primary_key=True)
