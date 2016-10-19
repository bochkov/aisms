import os
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = "Creates a test db"

    def handle(self, *args, **options):
        # delete existing sqlite db
        db = settings.DATABASES['default']
        if db['ENGINE'] == 'django.db.backends.sqlite3':
            if os.path.exists(db['NAME']):
                os.remove(settings.DATABASES['default']['NAME'])

        # create new db and fill data
        os.system("python manage.py syncdb --noinput")
        fixtures = ('organization.json', 'department.json', 'measure.json', 'document.json',
                    'image.json', 'passport.json', 'user.json')
        for i in fixtures:
            os.system('python manage.py loaddata %s' % i)

        # collect static
        os.system('python manage.py collectstatic --noinput')

        # run dev server
        os.system('python manage.py runserver')