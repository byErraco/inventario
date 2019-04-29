from django.urls import path

from .views import PersonasView

app_name = "personas"

urlpatterns = [
	path('', PersonasView.as_view(), name ="personas")
]