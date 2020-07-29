from datetime import timedelta
from glob import glob
from os import system
from os.path import join, getmtime

from django.core.management import BaseCommand
from django.utils.datetime_safe import datetime

from app.settings import MEDIA_ROOT, RESOLUTION


class Command(BaseCommand):

    help = 'Perform nightly build making timelapse video and uploading timelapse over FTP'

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.yesterdays_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        self.local_image_base_dir = join(MEDIA_ROOT, self.yesterdays_date)

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Beginning timelapse nightly build'))
        self.make_timelapse_video()
        self.zip_video()
        try:
            ftp_upload(f'{video_path}.gz')
        except Exception as e:
            # TODO Email me error
            self.stdout.write("Error uploading over FTP. Aborting and not deleting content.")
            raise e
        delete_photo_dir(self.yesterdays_date)
        # sendmail()

    def make_timelapse_video(self):
        image_dir = join(self.local_image_base_dir, self.yesterdays_date)
        images = glob(join(image_dir, '*.jpg'))
        images.sort(key=getmtime)

        image_list_file = join(image_dir, 'image-list.txt')
        with open(image_list_file, 'w') as temp_file:
            for image in images:
                temp_file.write(f'{image}\n')

        video_path = join(self.local_image_base_dir, self.yesterdays_date, f'timelapse-{self.yesterdays_date}.avi')
        command = f'mencoder -nosound -ovc lavc -lavcopts vcodec=mpeg4:aspect=16/9:vbitrate=8000000 -vf scale={RESOLUTION} -o "{video_path}" -mf type=jpeg:fps=24 "mf://@{image_list_file}" '
        system(command)

    def zip_video(self):

        system(f'gzip {video_path}')



#
#
# #!/usr/bin/python3
# """
# Create timelapse video, upload, then delete
#
# Requires dotenv
# pip install python-dotenv
# """
# import logging
# from datetime import datetime, timedelta
# from glob import glob
# from os import system, remove, environ
# from os.path import join, getmtime, basename
# from shutil import rmtree
# from smtplib import SMTP_SSL, SMTP_SSL_PORT
# from email.message import EmailMessage
# from ftplib import FTP
# logging.basicConfig(level=logging.INFO)
# from dotenv import load_dotenv
#
# # TODO make fault tolerant on FTP uploads
# # TODO use env vars
# # TODO document/package better
#
# load_dotenv()

def delete_photo_dir(yesterdays_date):
    rmtree(join(IMAGE_BASE_DIR, date))





def delete_content(date):
    rmtree(join(IMAGE_BASE_DIR, date))


def ftp_upload(date):
    #logging.debug('Connecting to FTP _ as _')
    with FTP('ftp.example.com', 'user', 'pass') as ftp:
        # Move in to target dir, ensuring it exists
        try:
            logging.debug(f'Changing FTP dir to {FTP_DESTINATION_DIR}')
            ftp.cwd(FTP_DESTINATION_DIR)
        except Exception:
            logging.warning(f'Could not change FTP dir to {FTP_DESTINATION_DIR}. Trying to create.')
            try:
                logging.debug(f'Trying to create FTP dir {FTP_DESTINATION_DIR}')
                ftp.mkd(FTP_DESTINATION_DIR)
            except Exception as e:
                logging.error(f"Error creating/moving to the FTP destination: {FTP_DESTINATION_DIR}")
                raise e

        try:
            logging.debug(f'Trying to create FTP dir to {date}')
            ftp.mkd(date)
        except Exception as e:
            logging.warning(f'Error creating daily folder for upload. May already exist. {e}')

        try:
            logging.debug(f'Trying to change FTP dir to {date}')
            ftp.cwd(date)
        except Exception as e:
            logging.error(f'Could not move to FTP dir {date}. {e}')
            raise e

        # Upload all files
        for local_filename in glob(join(IMAGE_BASE_DIR, date, '*')):
            with open(local_filename, 'rb') as local_file:
                logging.info(f'Uploading {local_filename}')
                try:
                    ftp.storbinary(f'STOR {basename(local_filename)}', local_file)
                except TimeoutError:
                    # Retry one more time if it timed out.
                    ftp.storbinary(f'STOR {basename(local_filename)}', local_file)

