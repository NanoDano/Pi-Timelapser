from django.db.models import Model, DateTimeField, ImageField


class Photo(Model):
    time_taken = DateTimeField(blank=False, null=False)
    image_file = ImageField(blank=False, null=False)

    def __str__(self):
        return str(self.time_taken)
