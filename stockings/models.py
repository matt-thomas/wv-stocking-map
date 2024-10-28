# stockings/models.py

from django.db import models

class BodyOfWater(models.Model):
    name = models.CharField(max_length=255, unique=True)  # Name of the water body
    latitude = models.FloatField()                        # GPS latitude
    longitude = models.FloatField()                       # GPS longitude
    info_url = models.URLField(blank=True, null=True)     # Optional link for more info about the location

    def __str__(self):
        return self.name


class FishStocking(models.Model):
    body_of_water = models.ForeignKey(BodyOfWater, on_delete=models.CASCADE, related_name='stockings')
    stocking_date = models.DateField()                # Date of stocking
    species = models.CharField(max_length=255)        # Species of fish stocked
    quantity = models.IntegerField()                  # Quantity of fish stocked
    source_url = models.URLField()                    # Link to the original data source

    def __str__(self):
        return f"{self.species} stocked in {self.body_of_water} on {self.stocking_date}"
