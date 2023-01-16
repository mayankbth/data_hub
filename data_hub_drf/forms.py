from django import forms


class UploadForm(forms.Form):

    file = forms.FileField(required=False)
    # Provide 'True' or 'False' for the BooleanField (treat "data" and "schema" as the BooleanFields).
    data = forms.CharField(max_length=10)
    schema = forms.CharField(max_length=10)
    data_types = forms.JSONField(required=False)
    table_name = forms.CharField(max_length=100)

    # custom validation
    def clean(self):
        cleaned_data = super().clean()
        data = cleaned_data.get("data")
        file = cleaned_data.get("file")
        schema = cleaned_data.get("schema")
        data_types = cleaned_data.get("data_types")
        table_name = cleaned_data.get("table_name")

        if data == "False" and schema == "False":
            raise forms.ValidationError("Both 'data' and 'schema' can not be 'False'.")
        if data == "True" and schema == "True":
            raise forms.ValidationError("Both 'data' and 'schema' can not be 'True'.")
        if schema == "True" and data_types == None:
            raise forms.ValidationError("if 'schema' is 'True', then 'data_types' has to be provided.")
        if schema == "False" and data_types != None:
            raise forms.ValidationError("if 'schema' is 'False', then 'data_types' should not be provided.")
        if len(table_name) > 63:
            raise forms.ValidationError("'table_name' can_not be more than 63 characters.")
        # to perform the regular_expression on "table_name" to check the validity of table_name provide.
        import re
        match = re.match(r"^[a-z_][a-z0-9_]*$", table_name)
        if match:
            # string (table_name) is valid.
            pass
        else:
            raise forms.ValidationError("'table_name' can only start with lowercase or underscores and it can only consist of underscores, lowercase or numbers.")
        if data == "True" and file == None:
            raise forms.ValidationError("When 'data' is 'True' then 'file' needs to be provided.")
        if not file.name.endswith(".xlsx"):
            raise forms.ValidationError("File must be a Excel.")


class TableCreatorForm(forms.Form):

    table_name = forms.CharField(max_length=100)
    data_types = forms.JSONField()


class TableDataForm(forms.Form):
    limit = forms.IntegerField(required=True)
    start_row_after = forms.IntegerField(required=True)
    object_count_after = forms.IntegerField(required=True)
