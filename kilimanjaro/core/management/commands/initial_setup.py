"""
    While running a project we may be need to initial things to be their. 
    Like the required groups or data in the db. This file contains a custom command 
    that needs to be run beginning of the project setup and those required data/env will be created with this.
"""

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from core.utils.general_data import LIST_OF_COUNTRIES_WITH_CURRENCY, groups
from country.models import Country


class Command(BaseCommand):
    """
    To running this command start env and type
            ```python manage.py initial_setup```
    This will create all the dependencies in the beginning of installing the projects
    """

    help = "Create Groups AND COUNTRY LIST While Installing Project [ Need To Call Once With First Migration ]"

    def handle(self, *args, **kwargs):

        # getting or creating groups
        for group_name in groups:
            group_obj, created = Group.objects.get_or_create(name=group_name)

        # creating country list
        for country_name, currency, currency_code in LIST_OF_COUNTRIES_WITH_CURRENCY:
            country_obj, created = Country.objects.get_or_create(
                name=country_name, currency_name=currency, currency_code=currency_code
            )

        self.stdout.write("Group created")  # for terminal log
        self.stdout.write("Country list created")  # for terminal log
