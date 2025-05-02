from django import forms
from .models import SubRubric, SuperRubric

class SubRubricForm(forms.ModelForm):
    super_rubric = forms.ModelChoiceField(
        queryset=SuperRubric.objects.all(),
        empty_label=None,
        label='Super Rubric',
        required=True
    )

    class Meta:
        model = SubRubric
        fields = '__all__'