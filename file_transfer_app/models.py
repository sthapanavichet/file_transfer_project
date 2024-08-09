from django.db import models
from django.contrib.auth.models import User


class FileTransfer(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='files/')
    uploader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_files', default=1)
    shared_with = models.ManyToManyField(User, related_name='shared_files')
