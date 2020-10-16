from django import forms
import datetime

class ImportGeojsonfileForm(forms.Form):
    import_file = forms.FileField(label="Select a geojson file")
    from_date = forms.DateField(initial=datetime.date.today)
    end_date = forms.DateField(initial=datetime.date.today)