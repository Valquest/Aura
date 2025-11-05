from django.contrib import admin
from django.urls import include, path
from controlhub import views

urlpatterns = [
    path('', views.index, name='index'), # controlhub view
    path('admin/', admin.site.urls),
    path('controlhub/', include('controlhub.urls')),
    path('iotcore/', include('iotcore.urls')),
]
