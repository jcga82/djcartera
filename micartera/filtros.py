import django_filters
from .models import *


class DividendosFilter(django_filters.FilterSet):
    class Meta():
        model = DividendoEmpresa
        fields = ['empresa',]