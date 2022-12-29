from django import forms


class UploadForm(forms.Form):
    file = forms.FileField()
    # Provide 'True' or 'False' for the BooleanField
    data = forms.CharField(max_length=10)
    schema = forms.CharField(max_length=10)