from django.urls import path

from .views import TiendasView


app_name = "tiendas"

urlpatterns = [
	path('', TiendasView.as_view(), name ="tiendas"),
]