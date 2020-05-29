#  Copyright (c) 2020 openKirkes, developed by Developer From Jokela

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Pushes refresh request to devices'

    def handle(self, *args, **options):
        ...
