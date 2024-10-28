# stockings/management/commands/scrape_stockings.py

import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from stockings.models import BodyOfWater, FishStocking
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import datetime

class Command(BaseCommand):
    help = 'Scrape fish stocking data from WVDNR and save to the database'

    def handle(self, *args, **kwargs):
        url = "https://wvdnr.gov/fishing/fish-stocking/fish-stockings/"
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        soup = BeautifulSoup(response.content, 'html.parser')

        # Example parsing logic (modify according to actual HTML structure)
        stocking_entries = soup.find_all('div', class_='stocking-entry')  # Adjust this selector

        for entry in stocking_entries:
            # Extract information from the HTML
            body_of_water_name = entry.find('span', class_='body-of-water').get_text(strip=True)
            stocking_date_text = entry.find('span', class_='date').get_text(strip=True)
            species = entry.find('span', class_='species').get_text(strip=True)
            quantity_text = entry.find('span', class_='quantity').get_text(strip=True)

            # Parse date and quantity
            stocking_date = datetime.datetime.strptime(stocking_date_text, "%Y-%m-%d").date()
            quantity = int(quantity_text)

            # Get or geocode coordinates for the body of water
            latitude, longitude = self.get_coordinates(body_of_water_name)

            # Skip if coordinates are not found
            if latitude is None or longitude is None:
                self.stdout.write(self.style.WARNING(f"Skipping {body_of_water_name} due to missing coordinates"))
                continue

            # Create or get the BodyOfWater entry
            body_of_water, created = BodyOfWater.objects.get_or_create(
                name=body_of_water_name,
                defaults={'latitude': latitude, 'longitude': longitude}
            )

            # Create or update the FishStocking entry
            FishStocking.objects.update_or_create(
                body_of_water=body_of_water,
                stocking_date=stocking_date,
                species=species,
                defaults={'quantity': quantity, 'source_url': url}
            )

    def get_coordinates(self, body_of_water_name):
        geolocator = Nominatim(user_agent="wv_stocking_map_geocoder")

        try:
            # Geocode the body of water with context (West Virginia)
            location = geolocator.geocode(f"{body_of_water_name}, West Virginia, USA")
            if location:
                return location.latitude, location.longitude
            else:
                self.stdout.write(self.style.WARNING(f"Coordinates not found for {body_of_water_name}"))
                return None, None
        except GeocoderTimedOut:
            self.stdout.write(self.style.ERROR(f"Geocoding request timed out for {body_of_water_name}"))
            return None, None
