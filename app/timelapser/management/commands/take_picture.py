from os import system, makedirs
from os.path import join

from django.core.management import BaseCommand
from django.utils.datetime_safe import datetime

from timelapser.models import Photo
from app.settings import MEDIA_ROOT


class Command(BaseCommand):

    help = 'Take photo with Pi camera'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Taking photo with Pi Camera'))

        trigger_time = datetime.now()  # Most important time is what time it was triggered
        day = trigger_time.strftime("%Y-%m-%d")
        full_image_dir = join(MEDIA_ROOT, day)  # YYYY-MM-DD
        makedirs(full_image_dir, exist_ok=True)  # Ensure daily folder exists
        image_filename = f'image-{trigger_time.strftime("%Y-%m-%d-%H-%M-%S")}.jpg'  # YYYY-MM-DD-HH-MM-SS
        output_filename = join(
            full_image_dir,
            image_filename,
        )

        # Take the photo
        code = system(f'raspistill -o "{output_filename}" --annotate 12 --quality 100')
        if code != 0:
            self.stdout.write(self.style.ERROR(f'Error taking picture with raspistill.'))
            raise Exception('Failure during `raspistill`. Does it exist?')

        # Store the photo reference in database
        Photo.objects.create(time_taken=trigger_time, image_file=join(day, image_filename)).save()
        self.stdout.write(self.style.SUCCESS(f'Took photo {output_filename}'))

