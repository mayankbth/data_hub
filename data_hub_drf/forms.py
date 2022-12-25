from django import forms


class UploadForm(forms.Form):
    file = forms.FileField()
    # Provide '0' or '1' for the BooleanField
    data = forms.BooleanField()
    schema = forms.BooleanField()