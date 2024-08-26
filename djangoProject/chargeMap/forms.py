from django import forms
from django.forms import ModelForm
from .models import *

modes = (
    ("driving", "driving"),
    ("walking", "walking"),
)
class DistanceForm(ModelForm):
    from_location = forms.ModelChoiceField(label="Location from", required=True, queryset=EChargeStations.objects.all())
    to_location = forms.ModelChoiceField(label="Location to", required=True, queryset=EChargeStations.objects.all())
    mode = forms.ChoiceField(choices=modes, required=True)

    class Meta:
        model = Distance
        exclude = ['created_at', 'updated_at', 'model','edited_at', 'distance_km', 'durations_km', 'duration_mins', 'duration_traffic_mins','to_location']

