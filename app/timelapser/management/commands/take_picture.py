import logging
from os import system, makedirs
from os.path import join
from django.core.management import BaseCommand
from django.utils.datetime_safe import datetime

from timelapser.models import Photo
from app.settings import MEDIA_ROOT


logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = 'Take photo with Pi camera'

    def handle(self, *args, **options):
        logger.info(self.style.SUCCESS('Taking photo with Pi Camera'))

        trigger_time = datetime.now()  # Most important time is what time it was triggered
        day = trigger_time.strftime("%Y-%m-%d")
        full_image_dir = join(MEDIA_ROOT, day)  # YYYY-MM-DD
        makedirs(full_image_dir, exist_ok=True)  # Ensure daily folder exists
        image_filename = f'image-{trigger_time.strftime("%Y-%m-%d-%H-%M-%S")}.jpg'  # YYYY-MM-DD-HH-MM-SS
        output_filename = join(
            full_image_dir,
            image_filename,
        )

        logger.info(self.style.SUCCESS(f'Taking picture to {output_filename}'))

        # Take the photo
        code = system(f'raspistill -o "{output_filename}" --annotate 12 --quality 100')
        if code != 0:
            logger.info(self.style.ERROR(f'Error taking picture with raspistill.'))
            raise Exception('Failure during `raspistill`. Does it exist?')

        # Store the photo reference in database
        Photo.objects.create(time_taken=trigger_time, image_file=join(day, image_filename)).save()
        logger.info(self.style.SUCCESS(f'Took photo {output_filename}'))
