from django import forms


class UploadForm(forms.Form):
    file = forms.FileField()
    # Provide 'True' or 'False' for the BooleanField
    data = forms.CharField(max_length=10)
    schema = forms.CharField(max_length=10)
    data_types = forms.JSONField(required=False)


# class OperationForm(forms.Form):
#     operation_type_choice = (
#         ("all_tables", "all_tables"),
#         ("table_data_all", "table_data_all"),
#     )
#     operation_type = forms.ChoiceField(choices=operation_type_choice, required=True)


class TableDataForm(forms.Form):
    limit = forms.IntegerField(required=True)
    start_row_after = forms.IntegerField(required=True)
    object_count_after = forms.IntegerField(required=True)
