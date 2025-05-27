from django.core.management.base import BaseCommand
from App.models import Product
import pandas as pd
import random
import os

class Command(BaseCommand):
    help = "Import products from Excel and create Product entries"

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='Path to Excel file (e.g., src/list.xlsx)',
            required=True
        )

    def handle(self, *args, **kwargs):
        file_path = kwargs['file']
        
        if not os.path.exists(file_path):
            self.stderr.write(self.style.ERROR(f"File not found: {file_path}"))
            return

        df = pd.read_excel(file_path)

        created = 0
        for row in df.itertuples(index=False):
            Product.objects.get_or_create(
                code=list(row)[0],
                defaults={
                    'code': list(row)[0],
                    'material_number': list(row)[1],
                    'description': list(row)[2],
                    'price': random.randrange(5000, 50000)
                }
            )
            created += 1

        self.stdout.write(self.style.SUCCESS(f"Successfully imported {created} products."))
