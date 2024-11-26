from django import forms

class UploadForm(forms.Form):
    file = forms.FileField()
    description = forms.CharField(max_length=255)
