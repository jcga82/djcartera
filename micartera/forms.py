from django import forms
from .models import Empresa, ESTRATEGIA_CHOICES

class CategoryFieldForm(forms.ModelForm):

    class Meta:
        model = Empresa
        fields = ('estrategia',)
        widgets = {
            'estrategia': forms.Select(choices=ESTRATEGIA_CHOICES)
        }