from datetime import timedelta
from ftplib import FTP_TLS
from glob import glob
from os import system
from os.path import join, getmtime, basename
from shutil import rmtree

from django.core.mail import mail_admins
from django.core.management import BaseCommand
from django.utils.datetime_safe import datetime

from app.settings import MEDIA_ROOT, RESOLUTION, FTP_DESTINATION_DIR, FTP_SERVER, FTP_USER, FTP_PASS


class Command(BaseCommand):

    help = 'Perform nightly build making timelapse video and uploading timelapse over FTP'

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.yesterdays_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        self.local_image_base_dir = join(MEDIA_ROOT, self.yesterdays_date)
        self.image_list_file = self.create_image_file_list()
        self.video_path = join(self.local_image_base_dir, f'timelapse-{self.yesterdays_date}.avi')
        self.zipped_video_path = f'{self.video_path}.gz'

    def create_image_file_list(self):
        images = glob(join(self.local_image_base_dir, '*.jpg'))
        images.sort(key=getmtime)
        image_list_file = join(self.local_image_base_dir, 'image-list.txt')

        with open(image_list_file, 'w') as temp_file:
            for image in images:
                temp_file.write(f'{image}\n')
        return image_list_file

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Beginning timelapse nightly build'))
        try:
            self.make_timelapse_video()
            self.zip_video()
            self.ftp_upload()
            self.delete_photo_dir()
            mail_admins('Timelapse video uploaded', f'New timelapse video is ready for {self.yesterdays_date}: {self.zipped_video_path}')
        except Exception as e:
            mail_admins('Error with timelapse nightly build', f'Error with timelapse for {FTP_DESTINATION_DIR}')

    def make_timelapse_video(self):
        command = f'mencoder -nosound -ovc lavc -lavcopts vcodec=mpeg4:aspect=16/9:vbitrate=8000000 -vf scale={RESOLUTION} -o "{self.video_path}" -mf type=jpeg:fps=24 "mf://@{self.image_list_file}" '
        #           mencoder -nosound -ovc lavc -lavcopts vcodec=mpeg4:aspect=16/9:vbitrate=8000000 -vf scale=1920:1080 -o timelapse.avi -mf type=jpeg:fps=24 mf://@stills.txt
        self.stdout.write(self.style.SUCCESS(f'Command: {command}'))
        system(command)

    def zip_video(self):
        self.stdout.write(f'Zipping {self.video_path}')
        if not system(f'gzip -f {self.video_path}'):
            raise Exception(f'Error zipping {self.video_path}')

    def ftp_upload(self):
        self.stdout.write(f'Uploading to FTP {FTP_SERVER} with {FTP_USER} to {FTP_DESTINATION_DIR} file {self.zipped_video_path}')
        with FTP_TLS(FTP_SERVER, FTP_USER, FTP_PASS) as ftp:
            try:
                ftp.cwd(FTP_DESTINATION_DIR)
            except Exception:
                ftp.mkd(FTP_DESTINATION_DIR)

            with open(self.zipped_video_path, 'rb') as local_file:
                try:
                    ftp.storbinary(f'STOR {basename(self.zipped_video_path)}', local_file)
                except TimeoutError:  # Retry one more time if it timed out.
                    try:
                        ftp.storbinary(f'STOR {basename(self.zipped_video_path)}', local_file)
                    except Exception as e:
                        # Error uploading on second attempt too
                        mail_admins('Error uploading timelapse', f'Error uploading timelapse {self.zipped_video_path}')

    def delete_photo_dir(self):
        if not rmtree(self.local_image_base_dir):
            raise Exception(f'Error deleting {self.local_image_base_dir}')



