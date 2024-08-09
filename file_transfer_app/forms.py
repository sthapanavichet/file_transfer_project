from django import forms
from .models import FileTransfer

class FileTransferForm(forms.ModelForm):
    class Meta:
        model = FileTransfer
        fields = ['title', 'file']
