import csv

from django.core.management.base import BaseCommand, CommandError
from recipe.models import Ingredients


class Command(BaseCommand):
    help = 'Add csv files to Django Models.'

    def handle(self, *args, **kwargs):
        try:
            with open(
                'ingredients.csv',
                newline='',
                encoding='utf-8'
            ) as csvfile:
                spamreader = csv.reader(csvfile, delimiter=',')
                next(spamreader)
                for row in spamreader:
                    if not Ingredients.objects.filter(name=row[0]):
                        Ingredients.objects.update_or_create(
                            name=row[0],
                            measurement_unit=row[1]
                        )
                self.stdout.write(self.style.SUCCESS('Ingredients записан.'))
        except FileNotFoundError as error:
            raise CommandError(
                f"Неудалось открыть файл Ingredients.csv. {error}"
            )
        except Exception as error:
            raise CommandError(
                f"Неудалось записать модель Ingredients. {error}"
            )
