"""djcartera URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from micartera.views import *
from micartera import views

from django.contrib import admin


urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),

    path('', include(('micartera.urls', 'users'), namespace='users')),
    path('', include(('micartera.urls', 'carteras'), namespace='carteras')),
    path('', include(('micartera.urls', 'empresas'), namespace='empresas')),
    path('', include(('micartera.urls', 'dividendos'), namespace='dividendos')),
    path('', include(('micartera.urls', 'fundamentales'), namespace='fundamentales')),
    path('', include(('micartera.urls', 'historico'), namespace='historico')),
    path('', include(('micartera.urls', 'qhistorico'), namespace='qhistorico')),
    path('', include(('micartera.urls', 'viviendas'), namespace='viviendas')),
    path('micartera/', include(('micartera.urls', 'micartera'), namespace='micartera')),
    path('api/authentication/', include('dj_rest_auth.urls')),
    # url(r'^admin/', admin.site.urls),

]
