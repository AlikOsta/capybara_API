from django import forms
from .models import SubLocal, SuperLocal

class SubLocalForm(forms.ModelForm):
    super_rubric = forms.ModelChoiceField(
        queryset=SuperLocal.objects.all(),
        empty_label=None,
        label='Super Local',
        required=True
    )

    class Meta:
        model = SubLocal
        fields = '__all__'