from django.core.management.base import BaseCommand
from ...models import DailyIndicators

import requests
from datetime import date


class Command(BaseCommand):
    help = "Fetch daily UF and Dólar observado from mindicador.cl"

    def handle(self, *args, **kwargs):
        today = date.today()
        if DailyIndicators.objects.filter(date=today).exists():
            self.stdout.write("Indicators for today already exist.")
            return

        response = requests.get("https://mindicador.cl/api")
        if response.status_code != 200:
            self.stderr.write("Failed to fetch indicators.")
            return

        data = response.json()
        uf = data['uf']['valor']
        dolar = data['dolar']['valor']

        DailyIndicators.objects.create(
            date=today,
            uf=uf,
            dolar=dolar
        )

        self.stdout.write(f"Saved indicators: UF={uf}, USD={dolar}")
