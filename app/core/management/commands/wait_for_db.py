import time

from psycopg2 import OperationalError as Psycopg20Error

from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Django command to pause execution until database is available"""

    def handle(self, *args, **options):
        """Handle the command"""
        self.stdout.write('Waiting for database...')
        db_up = False
        db_conn = None
        while not db_conn or db_up is False:
            try:
                # self.check(databases=['default'])
                db_conn = connections['default']
                db_up = True
            except(Psycopg20Error, OperationalError):
                self.stdout.write('Database unavailable, waiting 1 second...')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Database available!'))
